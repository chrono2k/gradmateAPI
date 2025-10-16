from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace, fields
from decorators import token_required
from models.student_model import Student
from models.teacher_model import Teacher
from api.teacher import teacher_model, format_teacher_response

from datetime import datetime

report_ns = Namespace('report', description='Gerenciamento de relatórios')

report_model = report_ns.model('Report', {
    'id': fields.Integer(description='ID do relatorio'),
    'description': fields.String(description='Descrição sobre o relatorio'),
    'pendency': fields.String(description='Pendencias referente ao projeto'),
    'status': fields.String(description='Status do relatorio', enum=['pendente', 'concluido']),
    'next_steps': fields.String(description='Proximos passos a ser executados para andamento do projeto'),
    'local': fields.String(description='local fisico que foi feita a reunião do relatorio'),
    'feedback': fields.String(description='Feedback para melhoria do projeto'),
    'teacher': fields.Nested(teacher_model),

})


def format_report_response(report_data):
    """
    Formata os dados do relatório para resposta da API

    Args:
        report_data (tuple): Tupla com dados do relatório no banco

    Returns:
        dict: Dicionário formatado
    """
    teacher = ""
    if report_data[7] is not None:
        teacher = format_teacher_response(Teacher.select_teacher_by_id(report_data[7]))

    print(report_data)
    return {
        'id': report_data[0],
        'description': report_data[1],
        'pendency': report_data[2],
        'status': report_data[3],
        'next_steps': report_data[4],
        'local': report_data[5],
        'feedback': report_data[6],
        'teacher': teacher,
        'project_id': report_data[8],
        'created_at': report_data[9].isoformat() if report_data[9] else None,
        'updated_at': report_data[10].isoformat() if report_data[10] else None
    }

