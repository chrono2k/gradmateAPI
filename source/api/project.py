from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace, fields
from decorators import token_required
from models.project_model import Project
from models.user_model import User
from models.course_model import Course
from models.teacher_model import Teacher
from models.student_model import Student
from models.report_model import Report
from api.course import course_model, format_course_response
from api.teacher import teacher_model, format_teacher_response
from api.student import student_model, format_student_response
from api.report import report_model, format_report_response
from datetime import datetime
import json

project_ns = Namespace('project', description='Gerenciamento de projetos TCC')

project_model = project_ns.model('Project', {
    'id': fields.Integer(description='ID do projeto'),
    'name': fields.String(required=True, description='Nome do projeto'),
    'description': fields.String(description='Descrição sobre o projeto'),
    'course': fields.Nested(course_model),
    'observation': fields.String(description='Observação sobre o projeto'),
    'status': fields.String(description='status do projeto',
                            enum=['Pré-projeto', 'Qualificação', 'Defesa', 'Finalizado', 'Trancado']),
    'teachers': fields.List(fields.Nested(teacher_model)),
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


def format_project_response(project_data):
    """
    Formata os dados do projeto para resposta da API

    Args:
        project_data (tuple): Tupla com dados do projeto do banco

    Returns:
        dict: Dicionário formatado
    """
    try:

        teachers = Teacher.find_all_by_project(project_data[0])
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
            'students': [format_student_response(student) for student in students] if students != 0 else None,
            'reports': [format_report_response(report) for report in reports] if reports != 0 else None,
            'created_at': project_data[6].isoformat() if project_data[6] else None,
            'updated_at': project_data[7].isoformat() if project_data[7] else None
        }
    except Exception as e:
        print(f"Erro ao formatar projeto: {e}")
    return {}


@project_ns.route('/')
class ProjectList(Resource):
    """Endpoints para listar e criar projetos"""

    @token_required
    @project_ns.doc('list_project', description='Lista todos os projetos')
    @project_ns.response(200, 'Lista de projetos retornada com sucesso', [project_model])
    @project_ns.response(401, 'Não autorizado')
    @project_ns.response(500, 'Erro interno do servidor')
    def get(self, current_user_id):
        """Lista todos os projetos"""
        try:
            projects = Project.select_all_projects()
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
            data = json.loads(request.get_json())

            if not data or 'name' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do projeto é obrigatório'
                }), 400)

            name = data.get('name', '').strip()
            description = data.get('description', '').strip() or None
            course_id = data.get('course_id', None)
            observation = data.get('observation', '').strip() or None
            status = data.get('status', 'Pré-projeto')

            if len(name) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do projeto deve ter no mínimo 3 caracteres'
                }), 400)

            project_id = Project.insert_project(name, description, course_id, observation, status)

            if project_id:
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

            data = json.loads(request.get_json())
            print(data)
            print(data.get('name'))

            name = data.get('name') if 'name' in data else None
            description = data.get('description') if 'description' in data else None
            course_id = data.get('course_id') if 'course_id' in data else None
            observation = data.get('observation') if 'observation' in data else None
            status = data.get('status') if 'status' in data else None

            if Project.update_project(project_id, name, description, course_id, observation, status):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Projeto atualizado com sucesso!'
                }), 200)
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

            data = json.loads(request.get_json())
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

            data = json.loads(request.get_json())
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

            data = json.loads(request.get_json())

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
            print("x"*60)
            print(current_user_id)
            print(Teacher.select_teacher_by_user_id(current_user_id))
            print(Teacher.select_teacher_by_user_id(current_user_id)[0])

            report_id = Project.insert_report(
                project_id, description, Teacher.select_teacher_by_user_id(current_user_id)[0], pendency,
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

            data = json.loads(request.get_json())

            description = data.get('description') if 'description' in data else None
            pendency = data.get('pendency') if 'pendency' in data else None
            status = data.get('status') if 'status' in data else None
            next_steps = data.get('next_steps') if 'next_steps' in data else None
            local = data.get('local') if 'local' in data else None
            feedback = data.get('feedback') if 'feedback' in data else None

            if Project.update_report(report_id, description, pendency, status,
                                     next_steps, local, feedback, Teacher.select_teacher_by_user_id(current_user_id)[0]):
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
