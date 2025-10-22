from flask import request, jsonify, make_response, send_file
from flask_restx import Resource, Namespace, fields
from decorators import token_required
from models.project_model import Project
from models.user_model import User
from models.course_model import Course
from models.teacher_model import Teacher
from models.student_model import Student
from models.report_model import Report
from models.project_file_model import ProjectFile
from models.defense_minutes_model import DefenseMinutes
from api.course import course_model, format_course_response
from api.teacher import teacher_model, format_teacher_response
from api.student import student_model, format_student_response
from api.report import report_model, format_report_response
from datetime import datetime
from utils.config import Config
from werkzeug.utils import secure_filename
import os
import uuid
from urllib.parse import quote
import json
from utils.request_utils import get_json_data

project_ns = Namespace('project', description='Gerenciamento de projetos TCC')


def user_can_manage_project(user_id, project_id):
    # Only admin or advisor in project
    from models.user_model import User
    from models.project_model import Project
    user = User.find_by_id(user_id)
    if not user:
        return False
    if user.authority == 'admin':
        return True
    # Check if user is advisor in project
    from models.teacher_model import Teacher
    teacher = Teacher.select_teacher_by_user_id(user_id)
    if not teacher:
        return False
    return Project.check_teacher_in_project_with_role(project_id, teacher[0], 'advisor')


ata_model = project_ns.model('DefenseMinutes', {
    'id': fields.Integer,
    'project_id': fields.Integer,
    'file_id': fields.Integer,
    'student_name': fields.String,
    'title': fields.String,
    'result': fields.String(enum=['aprovado', 'reprovado', 'pendente']),
    'location': fields.String,
    'started_at': fields.DateTime,
    'created_at': fields.DateTime,
    'created_by': fields.Integer
})


def format_ata_response(row):
    if not row:
        return None
    return {
        'id': row[0],
        'project_id': row[1],
        'file_id': row[2],
        'student_name': row[3],
        'title': row[4],
        'result': row[5],
        'location': row[6],
        'started_at': row[7].isoformat() if row[7] else None,
        'created_at': row[8].isoformat() if row[8] else None,
        'created_by': row[9]
    }


project_model = project_ns.model('Project', {
    'id': fields.Integer(description='ID do projeto'),
    'name': fields.String(required=True, description='Nome do projeto'),
    'description': fields.String(description='Descrição sobre o projeto'),
    'course': fields.Nested(course_model),
    'observation': fields.String(description='Observação sobre o projeto'),
    'status': fields.String(description='status do projeto',
                            enum=['Pré-projeto', 'Qualificação', 'Defesa', 'Finalizado', 'Trancado']),
    'teachers': fields.List(fields.Nested(teacher_model)),
    'guests': fields.List(fields.Nested(teacher_model)),
    'students': fields.List(fields.Nested(student_model)),
    'reports': fields.List(fields.Nested(report_model)),
    'created_at': fields.DateTime(description='Data de criação'),
    'updated_at': fields.DateTime(description='Data de atualização')
})
report_teacher_model = project_ns.model('ReportTeacher', {
    'id': fields.Integer(),
    'name': fields.String(),
    'observation': fields.String(),
    'image': fields.String(),
    'user_id': fields.String()
})

report_model = project_ns.model('Report', {
    'id': fields.Integer(),
    'description': fields.String(),
    'pendency': fields.String(),
    'status': fields.String(),
    'next_steps': fields.String(),
    'local': fields.String(),
    'feedback': fields.String(),
    'teacher': fields.Nested(report_teacher_model),
    'created_at': fields.DateTime(),
    'updated_at': fields.DateTime()
})

project_create_model = project_ns.model('ProjectCreate', {
    'name': fields.String(required=True, description='Nome do projeto', min_length=3, max_length=255),
    'description': fields.String(description='Descrição sobre o projeto'),
    'course_id': fields.Integer(description='Id do curso que está o projeto'),
    'observation': fields.String(description='Observação sobre o projeto'),
    'status': fields.String(description='status sobre o projeto')
})

project_update_model = project_ns.model('ProjectUpdate', {
    'id': fields.Integer(required=True, description='ID do projeto'),
    'name': fields.String(description='Novo nome do projeto'),
    'description': fields.String(description='Descrição sobre o projeto'),
    'course_id': fields.Integer(description='Id do curso que está o projeto'),
    'observation': fields.String(description='Observação sobre o projeto'),
    'status': fields.String(description='status sobre o projeto')
})

project_search_model = project_ns.model('ProjectSearch', {
    'name': fields.String(description='Nome do projeto para buscar'),
    'start_date': fields.String(description='Data inicial (YYYY-MM-DD)'),
    'end_date': fields.String(description='Data final (YYYY-MM-DD)'),
})

# ===== Files models/helpers =====
file_model = project_ns.model('ProjectFile', {
    'id': fields.Integer,
    'project_id': fields.Integer,
    'original_name': fields.String,
    'stored_name': fields.String,
    'mime_type': fields.String,
    'size': fields.Integer,
    'uploaded_by': fields.Integer,
    'created_at': fields.DateTime
})


def format_file_response(row):
    if not row:
        return None
    return {
        'id': row[0],
        'project_id': row[1],
        'original_name': row[2],
        'stored_name': row[3],
        'mime_type': row[4],
        'size': row[5],
        'uploaded_by': row[6],
        'created_at': row[7].isoformat() if row[7] else None
    }


def get_project_upload_dir(project_id: int) -> str:
    base = Config.UPLOAD_FOLDER if hasattr(Config, 'UPLOAD_FOLDER') else 'uploads'
    # Resolve repo root: <repo>/source/api/project.py -> go up two levels
    api_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(api_dir, '..', '..'))
    path = os.path.join(repo_root, base, 'projects', str(project_id))
    os.makedirs(path, exist_ok=True)
    return path


def format_project_response(project_data):
    """
    Formata os dados do projeto para resposta da API

    Args:
        project_data (tuple): Tupla com dados do projeto do banco

    Returns:
        dict: Dicionário formatado
    """
    try:
        teachers = Project.get_project_teachers_by_role(project_data[0], 'advisor')
        guests = Project.get_project_teachers_by_role(project_data[0], 'guest')
        students = Student.find_all_by_project(project_data[0])
        reports = Report.find_all_by_project(project_data[0])
        return {
            'id': project_data[0],
            'name': project_data[1],
            'description': project_data[2],
            'course': format_course_response(Course.select_course_by_id(project_data[3])),
            'observation': project_data[4],
            'status': project_data[5],
            'teachers': [format_teacher_response(teacher) for teacher in teachers] if teachers != 0 else None,
            'guests': [format_teacher_response(guest) for guest in guests] if guests != 0 else None,
            'students': [format_student_response(student) for student in students] if students != 0 else None,
            'reports': [format_report_response(report) for report in reports] if reports != 0 else None,
            'created_at': project_data[6].isoformat() if project_data[6] else None,
            'updated_at': project_data[7].isoformat() if project_data[7] else None
        }
    except Exception as e:
        print(f"Erro ao formatar projeto: {e}")
    return {}


@project_ns.route('/<int:project_id>/atas')
class ProjectAtas(Resource):
    @token_required
    def post(self, current_user_id, project_id):
        """Cria registro de ata de defesa"""
        if not user_can_manage_project(current_user_id, project_id):
            return make_response(jsonify({'success': False, 'message': 'Não autorizado'}), 403)
        data = get_json_data()
        file_id = data.get('file_id')
        student_name = data.get('student_name', '').strip() or None
        title = data.get('title', '').strip()
        result = data.get('result', '').strip().lower()
        location = data.get('location')
        started_at = data.get('started_at')
        if not file_id or not title or result not in ['aprovado', 'reprovado', 'pendente']:
            return make_response(jsonify({'success': False, 'message': 'Payload inválido'}), 400)
        # Check project exists
        if not Project.check_project_exists(project_id):
            return make_response(jsonify({'success': False, 'message': 'Projeto não encontrado'}), 404)
        # Check file ownership
        if not DefenseMinutes.validate_file_ownership(project_id, file_id):
            return make_response(jsonify({'success': False, 'message': 'Arquivo não pertence ao projeto'}), 404)
        ata_id = DefenseMinutes.insert(project_id, file_id, student_name, title, result, location, started_at,
                                       current_user_id)
        row = DefenseMinutes.get_by_id(ata_id)
        return make_response(jsonify({'success': True, 'ata': format_ata_response(row)}), 201)


@project_ns.route('/atas')
class AllDefenseMinutes(Resource):
    """Lista todas as atas de defesa"""

    @token_required
    def get(self, current_user_id):
        """Lista todas as atas de defesa do sistema"""
        try:
            result = DefenseMinutes.list_all_with_project()
            items = []
            if result and result not in (0, "0"):
                items = [
                    {
                        'id': r[0],
                        'project_id': r[1],
                        'file_id': r[2],
                        'student_name': r[3],
                        'title': r[4],
                        'result': r[5],
                        'location': r[6],
                        'started_at': r[7].isoformat() if r[7] else None,
                        'created_at': r[8].isoformat() if r[8] else None,
                        'created_by': r[9],
                        'project_name': r[10]
                    } for r in result
                ]
            return make_response(jsonify({'success': True, 'items': items, 'total': len(items)}), 200)
        except Exception as e:
            return make_response(jsonify({'success': False, 'message': 'Erro ao listar atas', 'error': str(e)}), 500)


@project_ns.route('/')
class ProjectList(Resource):
    """Endpoints para listar e criar projetos"""

    @token_required
    @project_ns.doc('list_project', description='Lista todos os projetos')
    @project_ns.response(200, 'Lista de projetos retornada com sucesso', [project_model])
    @project_ns.response(401, 'Não autorizado')
    @project_ns.response(500, 'Erro interno do servidor')
    def get(self, current_user_id):
        """Lista todos os projetos, filtrando por usuário logado"""
        try:
            user = User.find_by_id(current_user_id)
            status = request.args.get('status', 'Pré-projeto')
            projects = []
            if user:
                if user.authority == 'student':
                    result = Project.select_projects_by_student(user.id, status)
                    projects = result if result and result not in (0, "0") else []
                elif user.authority == 'teacher':
                    result = Project.select_projects_by_teacher(user.id, status)
                    projects = result if result and result not in (0, "0") else []
                else:
                    # Admin vê todos
                    result = Project.select_all_projects(status)
                    projects = result if result and result not in (0, "0") else []
            response = [format_project_response(project) for project in projects]
            return make_response(jsonify({
                'success': True,
                'projects': response,
                'total': len(response)
            }), 200)
        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar projetos',
                'error': str(e)
            }), 500)

    @token_required
    @project_ns.doc('create_project')
    @project_ns.response(201, 'Projeto criado com sucesso')
    def post(self, current_user_id):
        """Cria um novo projeto"""
        try:
            data = get_json_data()

            if not data or 'name' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do projeto é obrigatório'
                }), 400)

            name = data.get('name', '').strip()
            description = data.get('description', '').strip() or None
            # Aceita tanto course_id quanto courseId
            course_id = data.get('course_id') or data.get('courseId')
            observation = data.get('observation', '').strip() or None
            status = data.get('status', 'Pré-projeto')

            if len(name) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do projeto deve ter no mínimo 3 caracteres'
                }), 400)

            project_id = Project.insert_project(name, description, course_id, observation, status)

            if project_id:
                # Se for professor, adiciona ele como orientador do projeto
                user = User.find_by_id(current_user_id)
                if user and user.authority == 'teacher':
                    teacher = Teacher.select_teacher_by_user_id(current_user_id)
                    if teacher and teacher != 0:
                        teacher_id = teacher[0]
                        Project.add_teacher_to_project_with_role(project_id, teacher_id, 'advisor')

                return make_response(jsonify({
                    'success': True,
                    'message': 'Projeto criado com sucesso!',
                    'project_id': project_id
                }), 201)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao criar projeto'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao criar projeto',
                'error': str(e)
            }), 500)


@project_ns.route('/<int:project_id>')
class ProjectDetail(Resource):
    """Endpoints para operações em projeto específico"""

    @token_required
    @project_ns.doc('get_project', description='Busca um projeto por ID')
    @project_ns.response(200, 'Projeto encontrado', project_model)
    @project_ns.response(404, 'Projeto não encontrado')
    def get(self, current_user_id, project_id):
        """Busca um projeto específico por ID"""
        try:
            project = Project.select_project_by_id(project_id)
            if not project:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            return make_response(jsonify({
                'success': True,
                'project': format_project_response(project)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar projeto',
                'error': str(e)
            }), 500)

    @token_required
    @project_ns.doc('update_project')
    @project_ns.response(200, 'Projeto atualizado')
    def put(self, current_user_id, project_id):
        """Atualiza um projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            data = get_json_data()
            print(data)
            print(data.get('name'))

            name = data.get('name') if isinstance(data, dict) and 'name' in data else None
            description = data.get('description') if isinstance(data, dict) and 'description' in data else None
            course_id = data.get('course_id') if isinstance(data, dict) and 'course_id' in data else None
            observation = data.get('observation') if isinstance(data, dict) and 'observation' in data else None
            status = data.get('status') if isinstance(data, dict) and 'status' in data else None

            # Atualiza projeto
            updated = Project.update_project(project_id, name, description, course_id, observation, status)

            # Se status for Concluído/Finalizado, marcar alunos do projeto como "formado"
            normalized_status = None
            try:
                normalized_status = status.strip().lower() if isinstance(status, str) else None
            except Exception:
                normalized_status = None

            did_grad = False
            if normalized_status in ('concluído', 'concluido', 'finalizado'):
                try:
                    # Atualiza status dos alunos vinculados ao projeto
                    from models.student_model import Student
                    Student.set_status_by_project(project_id, 'formado')
                    did_grad = True
                except Exception:
                    # não quebra a atualização do projeto se falhar
                    did_grad = False

            if updated or did_grad:
                msg = 'Projeto atualizado com sucesso!'
                if did_grad:
                    msg += " Alunos do projeto marcados como 'formado'."
                return make_response(jsonify({'success': True, 'message': msg}), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nenhuma alteração foi realizada'
                }), 400)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao atualizar projeto',
                'error': str(e)
            }), 500)

    @token_required
    @project_ns.doc('delete_project')
    @project_ns.response(200, 'Projeto removido')
    def delete(self, current_user_id, project_id):
        """Remove um projeto"""
        try:
            # Apenas admin ou orientador do projeto podem remover
            if not user_can_manage_project(current_user_id, project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Não autorizado'
                }), 403)
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            if Project.delete_project(project_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Projeto removido com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao remover projeto'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao remover projeto',
                'error': str(e)
            }), 500)


@project_ns.route('/<int:project_id>/teachers')
class ProjectTeachers(Resource):
    """Endpoints para gerenciar professores do projeto"""

    @token_required
    @project_ns.doc('add_teachers')
    @project_ns.response(200, 'Professores adicionados')
    def post(self, current_user_id, project_id):
        """Adiciona professores ao projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            data = get_json_data()
            teacher_ids = data.get('teacher_ids', [])

            if not teacher_ids:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Lista de professores vazia'
                }), 400)

            added = 0
            for teacher_id in teacher_ids:
                if not Project.check_teacher_in_project(project_id, teacher_id):
                    if Project.add_teacher_to_project(project_id, teacher_id):
                        added += 1

            return make_response(jsonify({
                'success': True,
                'message': f'{added} professor(es) adicionado(s) com sucesso!'
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao adicionar professores',
                'error': str(e)
            }), 500)


@project_ns.route('/<int:project_id>/teachers/<int:teacher_id>')
class ProjectTeacherDetail(Resource):
    """Endpoints para remover professor do projeto"""

    @token_required
    @project_ns.doc('remove_teacher')
    @project_ns.response(200, 'Professor removido')
    def delete(self, current_user_id, project_id, teacher_id):
        """Remove um professor do projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            if Project.remove_teacher_from_project(project_id, teacher_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Professor removido com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao remover professor'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao remover professor',
                'error': str(e)
            }), 500)


@project_ns.route('/<int:project_id>/guests')
class ProjectGuests(Resource):
    """Endpoints para gerenciar convidados (banca) do projeto"""

    @token_required
    def put(self, current_user_id, project_id):
        """Adiciona convidados ao projeto (role = 'guest')"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({'success': False, 'message': 'Projeto não encontrado'}), 404)

            data = get_json_data()
            guest_ids = data.get('guest_ids', [])

            if not isinstance(guest_ids, list) or not guest_ids:
                return make_response(jsonify({'success': False, 'message': 'guest_ids deve ser uma lista não vazia'}),
                                     422)

            added = []
            warnings = []
            for guest_id in guest_ids:
                # validar professor
                if not Teacher.select_teacher_by_id(guest_id):
                    warnings.append({'id': guest_id, 'message': 'Professor inválido'})
                    continue
                # não pode ser orientador
                if Project.check_teacher_in_project_with_role(project_id, guest_id, 'advisor'):
                    return make_response(jsonify({'success': False, 'message': 'Professor já é orientador do projeto'}),
                                         400)
                # idempotente: pular se já é guest
                if Project.check_teacher_in_project_with_role(project_id, guest_id, 'guest'):
                    continue
                if Project.add_teacher_to_project_with_role(project_id, guest_id, 'guest'):
                    added.append(guest_id)

            # retornar lista de convidados atual
            guests = Project.get_project_teachers_by_role(project_id, 'guest')
            return make_response(jsonify({
                'success': True,
                'message': 'Convidados adicionados com sucesso',
                'guests': [format_teacher_response(g) for g in guests] if guests != 0 else [],
                'warnings': warnings
            }), 200)
        except Exception as e:
            return make_response(
                jsonify({'success': False, 'message': 'Erro ao adicionar convidados', 'error': str(e)}), 500)


@project_ns.route('/<int:project_id>/guests/<int:guest_id>')
class ProjectGuestDetail(Resource):
    """Remover convidado do projeto"""

    @token_required
    def delete(self, current_user_id, project_id, guest_id):
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({'success': False, 'message': 'Projeto não encontrado'}), 404)

            # precisa existir como guest
            if not Project.check_teacher_in_project_with_role(project_id, guest_id, 'guest'):
                return make_response(jsonify({'success': False, 'message': 'Convidado não encontrado'}), 404)

            if Project.remove_guest_from_project(project_id, guest_id):
                return make_response(jsonify({'success': True, 'message': 'Convidado removido com sucesso'}), 200)
            else:
                return make_response(jsonify({'success': False, 'message': 'Erro ao remover convidado'}), 500)
        except Exception as e:
            return make_response(jsonify({'success': False, 'message': 'Erro ao remover convidado', 'error': str(e)}),
                                 500)


@project_ns.route('/<int:project_id>/students')
class ProjectStudents(Resource):
    """Endpoints para gerenciar alunos do projeto"""

    @token_required
    @project_ns.doc('add_students')
    @project_ns.response(200, 'Alunos adicionados')
    def post(self, current_user_id, project_id):
        """Adiciona alunos ao projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            data = get_json_data()
            student_ids = data.get('student_ids', [])

            if not student_ids:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Lista de alunos vazia'
                }), 400)

            added = 0
            for student_id in student_ids:
                if not Project.check_student_in_project(project_id, student_id):
                    if Project.add_student_to_project(project_id, student_id):
                        added += 1

            return make_response(jsonify({
                'success': True,
                'message': f'{added} aluno(s) adicionado(s) com sucesso!'
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao adicionar alunos',
                'error': str(e)
            }), 500)


@project_ns.route('/<int:project_id>/students/<int:student_id>')
class ProjectStudentDetail(Resource):
    """Endpoints para remover aluno do projeto"""

    @token_required
    @project_ns.doc('remove_student')
    @project_ns.response(200, 'Aluno removido')
    def delete(self, current_user_id, project_id, student_id):
        """Remove um aluno do projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            if Project.remove_student_from_project(project_id, student_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Aluno removido com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao remover aluno'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao remover aluno',
                'error': str(e)
            }), 500)


@project_ns.route('/<int:project_id>/reports')
class ProjectReports(Resource):
    """Endpoints para gerenciar relatórios do projeto"""

    @token_required
    @project_ns.doc('add_report')
    @project_ns.response(201, 'Relatório criado')
    def post(self, current_user_id, project_id):
        """Adiciona um novo relatório ao projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            data = get_json_data()

            if not data or 'description' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Descrição do relatório é obrigatória'
                }), 400)

            description = data.get('description', '').strip()
            pendency = data.get('pendency', '').strip() or None
            status = data.get('status', 'pendente')
            next_steps = data.get('next_steps', '').strip() or None
            local = data.get('local', '').strip() or None
            feedback = data.get('feedback', '').strip() or None

            if len(description) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Descrição deve ter no mínimo 3 caracteres'
                }), 400)

            teacher = Teacher.select_teacher_by_user_id(current_user_id)
            teacher_id = teacher[0] if teacher and teacher != 0 else None

            report_id = Project.insert_report(
                project_id, description, teacher_id, pendency,
                status, next_steps, local, feedback
            )

            if report_id:
                return make_response(jsonify({
                    'success': True,
                    'message': 'Relatório criado com sucesso!',
                    'report_id': report_id
                }), 201)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao criar relatório'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao criar relatório',
                'error': str(e)
            }), 500)


@project_ns.route('/<int:project_id>/reports/<int:report_id>')
class ProjectReportDetail(Resource):
    """Endpoints para operações em relatório específico"""

    @token_required
    @project_ns.doc('update_report')
    @project_ns.response(200, 'Relatório atualizado')
    def put(self, current_user_id, project_id, report_id):
        """Atualiza um relatório do projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            report = Project.get_report_by_id(report_id)
            if not report or report[1] != project_id:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Relatório não encontrado'
                }), 404)

            data = get_json_data()

            description = data.get('description') if 'description' in data else None
            pendency = data.get('pendency') if 'pendency' in data else None
            status = data.get('status') if 'status' in data else None
            next_steps = data.get('next_steps') if 'next_steps' in data else None
            local = data.get('local') if 'local' in data else None
            feedback = data.get('feedback') if 'feedback' in data else None

            # Definir teacher_id apenas se usuário for professor
            _t = Teacher.select_teacher_by_user_id(current_user_id)
            teacher_id = _t[0] if _t and _t != 0 else None

            if Project.update_report(report_id, description, pendency, status,
                                     next_steps, local, feedback, teacher_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Relatório atualizado com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nenhuma alteração foi realizada'
                }), 400)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao atualizar relatório',
                'error': str(e)
            }), 500)

    @token_required
    @project_ns.doc('delete_report')
    @project_ns.response(200, 'Relatório removido')
    def delete(self, current_user_id, project_id, report_id):
        """Remove um relatório do projeto"""
        try:
            # Apenas admin ou orientador do projeto podem remover relatório
            if not user_can_manage_project(current_user_id, project_id):
                return make_response(jsonify({'success': False, 'message': 'Não autorizado'}), 403)
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Projeto não encontrado'
                }), 404)

            report = Project.get_report_by_id(report_id)
            if not report or report[1] != project_id:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Relatório não encontrado'
                }), 404)

            if Project.delete_report(report_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Relatório removido com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao remover relatório'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao remover relatório',
                'error': str(e)
            }), 500)


@project_ns.route('/statistics')
class ProjectStatistics(Resource):
    """Endpoints para estatísticas de projetos"""

    @token_required
    @project_ns.doc('get_statistics')
    @project_ns.response(200, 'Estatísticas retornadas')
    def get(self, current_user_id):
        """Retorna estatísticas dos projetos"""
        try:
            stats = Project.get_project_statistics()

            if stats['ultimo_cadastro']:
                stats['ultimo_cadastro'] = stats['ultimo_cadastro'].isoformat()

            return make_response(jsonify({
                'success': True,
                'statistics': stats
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar estatísticas',
                'error': str(e)
            }), 500)


# ===== Files endpoints =====
@project_ns.route('/<int:project_id>/files')
class ProjectFiles(Resource):
    @token_required
    def get(self, current_user_id, project_id):
        """Lista arquivos do projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({'success': False, 'message': 'Projeto não encontrado'}), 404)
            rows = ProjectFile.list_by_project(project_id)
            files = [format_file_response(r) for r in rows] if rows and rows != "0" else []
            return make_response(jsonify({'success': True, 'files': files, 'total': len(files)}), 200)
        except Exception as e:
            return make_response(jsonify({'success': False, 'message': 'Erro ao listar arquivos', 'error': str(e)}),
                                 500)

    @token_required
    def post(self, current_user_id, project_id):
        """Upload de um ou mais arquivos para o projeto"""
        try:
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({'success': False, 'message': 'Projeto não encontrado'}), 404)

            if 'files[]' not in request.files:
                # também aceitar 'files' simples
                if 'files' not in request.files:
                    return make_response(jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400)
                files = request.files.getlist('files')
            else:
                files = request.files.getlist('files[]')

            saved = []
            upload_dir = get_project_upload_dir(project_id)

            for file in files:
                if not file or file.filename == '':
                    continue
                original_name = file.filename
                safe_name = secure_filename(original_name)
                ext = os.path.splitext(safe_name)[1]
                unique = f"{uuid.uuid4().hex}{ext}"
                abs_path = os.path.join(upload_dir, unique)
                file.save(abs_path)
                size = os.path.getsize(abs_path)
                mime = file.mimetype
                file_id = ProjectFile.insert_file(project_id, original_name, unique, mime, size, current_user_id)
                saved.append({'id': file_id, 'original_name': original_name})

            return make_response(jsonify({'success': True, 'saved': saved}), 200)
        except Exception as e:
            return make_response(jsonify({'success': False, 'message': 'Erro no upload', 'error': str(e)}), 500)


@project_ns.route('/<int:project_id>/files/bulk-delete')
class ProjectFilesBulkDelete(Resource):
    @token_required
    def post(self, current_user_id, project_id):
        """Remove múltiplos arquivos do projeto (best-effort)"""
        try:
            # AuthZ: apenas admin/teacher
            user = User.find_by_id(current_user_id)
            if not user or user.authority not in ('admin', 'teacher'):
                return make_response(jsonify({'success': False, 'message': 'Não autorizado'}), 403)

            # Projeto precisa existir
            if not Project.check_project_exists(project_id):
                return make_response(jsonify({'success': False, 'message': 'Projeto não encontrado'}), 404)

            data = get_json_data()
            file_ids = data.get('file_ids') if isinstance(data, dict) else None

            # Validação do payload
            if not isinstance(file_ids, list) or not file_ids:
                return make_response(jsonify({'success': False, 'message': 'file_ids deve ser uma lista não vazia'}),
                                     400)

            # Normaliza ids para inteiros válidos
            try:
                file_ids = [int(x) for x in file_ids]
            except Exception:
                return make_response(jsonify({'success': False, 'message': 'file_ids deve conter apenas números'}), 400)

            deleted = []
            failed = []
            upload_dir = get_project_upload_dir(project_id)

            for fid in file_ids:
                try:
                    row = ProjectFile.get_by_id(fid)
                    # ownership: arquivo precisa pertencer ao projeto
                    if not row or row[1] != project_id:
                        failed.append(fid)
                        continue

                    stored_name = row[3]
                    abs_path = os.path.join(upload_dir, stored_name)
                    # Apaga do banco primeiro
                    ok_db = ProjectFile.delete_by_id(fid)
                    # Tenta apagar o arquivo físico (não falha se já não existir)
                    try:
                        if os.path.exists(abs_path):
                            os.remove(abs_path)
                    except Exception:
                        pass

                    if ok_db:
                        deleted.append(fid)
                    else:
                        failed.append(fid)
                except Exception:
                    failed.append(fid)

            if not deleted and not failed:
                return make_response(jsonify({'success': False, 'message': 'Nenhum arquivo processado'}), 400)

            return make_response(jsonify({'success': True, 'deleted': deleted, 'failed': failed}), 200)
        except Exception as e:
            return make_response(jsonify({'success': False, 'message': 'Erro ao remover arquivos', 'error': str(e)}),
                                 500)


@project_ns.route('/<int:project_id>/files/<int:file_id>/download')
class ProjectFileDownload(Resource):
    @token_required
    def get(self, current_user_id, project_id, file_id):
        """Baixa um arquivo específico do projeto"""
        try:
            row = ProjectFile.get_by_id(file_id)
            if not row or row[1] != project_id:
                return make_response(jsonify({'success': False, 'message': 'Arquivo não encontrado'}), 404)

            upload_dir = get_project_upload_dir(project_id)
            abs_path = os.path.join(upload_dir, row[3])
            if not os.path.exists(abs_path):
                return make_response(jsonify({'success': False, 'message': 'Arquivo não existe no servidor'}), 404)

            filename = row[2]
            response = make_response(send_file(abs_path, as_attachment=True, download_name=filename))
            # Garantir header com nome em UTF-8
            response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{quote(filename)}"
            return response
        except Exception as e:
            return make_response(jsonify({'success': False, 'message': 'Erro no download', 'error': str(e)}), 500)


@project_ns.route('/<int:project_id>/files/<int:file_id>')
class ProjectFileDelete(Resource):
    @token_required
    def delete(self, current_user_id, project_id, file_id):
        """Remove metadados e arquivo físico"""
        try:
            row = ProjectFile.get_by_id(file_id)
            if not row or row[1] != project_id:
                return make_response(jsonify({'success': False, 'message': 'Arquivo não encontrado'}), 404)

            upload_dir = get_project_upload_dir(project_id)
            abs_path = os.path.join(upload_dir, row[3])
            # Apaga do banco primeiro
            ok = ProjectFile.delete_by_id(file_id)
            # Tenta apagar o arquivo físico (não falha se já não existir)
            try:
                if os.path.exists(abs_path):
                    os.remove(abs_path)
            except Exception:
                pass

            if ok:
                return make_response(jsonify({'success': True, 'message': 'Arquivo removido'}), 200)
            else:
                return make_response(jsonify({'success': False, 'message': 'Erro ao remover arquivo'}), 500)
        except Exception as e:
            return make_response(jsonify({'success': False, 'message': 'Erro ao remover arquivo', 'error': str(e)}),
                                 500)
