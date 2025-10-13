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

project_ns = Namespace('project', description='Gerenciamento de projetos')


project_model = project_ns.model('Project', {
    'id': fields.Integer(description='ID do projeto'),
    'name': fields.String(required=True, description='Nome do projeto'),
    'description': fields.String(description='Descrição sobre o projeto'),
    'course': fields.Nested(course_model),
    'observation': fields.String(description='Observação sobre o projeto'),
    'status': fields.String(description='status do projeto', enum=['Pré-projeto', 'Qualificação', 'Defesa', 'Finalizado', 'Trancado']),
    'teachers': fields.List(fields.Nested(teacher_model)),
    'students': fields.List(fields.Nested(student_model)),
    'reports': fields.List(fields.Nested(report_model)),
    'created_at': fields.DateTime(description='Data de criação'),
    'updated_at': fields.DateTime(description='Data de atualização')
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
        print(f"Erro ao formatar projeto: {e}")  # Para debug
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
