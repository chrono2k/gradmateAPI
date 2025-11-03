from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace, fields
from decorators import token_required
from utils.request_utils import get_json_data
from models.student_model import Student
from models.user_model import User
from datetime import datetime

student_ns = Namespace('student', description='Gerenciamento de alunos')

student_model = student_ns.model('Student', {
    'id': fields.Integer(description='ID do aluno'),
    'name': fields.String(required=True, description='Nome do aluno'),
    'registration': fields.String(required=True, description='RA do aluno'),
    'observation': fields.String(description='Observação sobre o aluno'),
    'image': fields.String(description='Imagem do aluno'),
    'status': fields.String(description='Status do aluno'),
    'telephone': fields.String(description='Telefone do aluno'),
    'user_id': fields.String(description='Id do usuário do aluno'),
    'created_at': fields.DateTime(description='Data de criação'),
    'updated_at': fields.DateTime(description='Data de atualização')
})

student_create_model = student_ns.model('StudentCreate', {
    'name': fields.String(required=True, description='Nome do aluno', min_length=3, max_length=255),
    'email': fields.String(required=True, description='Email/login do aluno', min_length=3, max_length=255),
    'registration': fields.String(required=True, description='RA do aluno', min_length=3, max_length=255),
    'observation': fields.String(description='Observação sobre o aluno'),
    'image': fields.String(description='Imagem do aluno')
})

student_update_model = student_ns.model('StudentUpdate', {
    'id': fields.Integer(required=True, description='ID do aluno'),
    'name': fields.String(description='Novo nome do aluno'),
    'email': fields.String(description='Novo email do aluno'),
    'observation': fields.String(description='Nova observação'),
    'registration': fields.String(description='Ra do aluno'),
    'telephone': fields.String(description='Telefone do aluno'),
    'image': fields.String(description='Nova imagem')
})

student_delete_model = student_ns.model('StudentDelete', {
    'id': fields.Integer(required=True, description='ID do aluno a ser desativado')
})

student_active_model = student_ns.model('StudentActive', {
    'id': fields.Integer(required=True, description='ID do aluno a ser ativado')
})

student_search_model = student_ns.model('StudentSearch', {
    'name': fields.String(description='Nome do aluno para buscar'),
    'start_date': fields.String(description='Data inicial (YYYY-MM-DD)'),
    'end_date': fields.String(description='Data final (YYYY-MM-DD)'),
})


def format_student_response(student_data):
    """
    Formata os dados do aluno para resposta da API

    Args:
        student_data (tuple): Tupla com dados do aluno do banco

    Returns:
        dict: Dicionário formatado
    """
    return {
        'id': student_data[0],
        'name': student_data[1],
        'registration': student_data[2],
        'observation': student_data[3],
        'image': student_data[4],
        'status': student_data[5],
        'telephone': student_data[9] if len(student_data) > 9 else None,
        'user': User.select_user_by_id(student_data[6]).to_dict(),
        'created_at': student_data[7].isoformat() if student_data[7] else None,
        'updated_at': student_data[8].isoformat() if student_data[8] else None
    }


@student_ns.route('/')
class StudentList(Resource):
    """Endpoints para listar e criar alunos"""

    @token_required
    @student_ns.doc('list_student', description='Lista todos os alunos')
    @student_ns.response(200, 'Lista de alunos retornada com sucesso', [student_model])
    @student_ns.response(401, 'Não autorizado')
    @student_ns.response(500, 'Erro interno do servidor')
    def get(self, current_user_id):
        """Lista todos os alunos"""
        try:
            students = Student.select_all_student()
            response = [format_student_response(student) for student in students]

            return make_response(jsonify({
                'success': True,
                'students': response,
                'total': len(response)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar alunos',
                'error': str(e)
            }), 500)

    @token_required
    @student_ns.doc('create_student', description='Cria um novo aluno')
    @student_ns.expect(student_create_model)
    @student_ns.response(201, 'Aluno criado com sucesso')
    @student_ns.response(400, 'Dados inválidos')
    @student_ns.response(409, 'Aluno já existe')
    def post(self, current_user_id):
        """Cria um novo aluno"""
        try:
            data = get_json_data()
            if not data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Informações obrigatórias'
                }), 400)

            if 'name' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do aluno é obrigatório'
                }), 400)
            if 'email' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Email do aluno é obrigatório'
                }), 400)
            if 'registration' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'RA do aluno é obrigatório'
                }), 400)

            name = (data.get('name') or '').strip()
            email = (data.get('email') or '').strip()
            registration = (data.get('registration') or '').strip()
            observation = (data.get('observation') or '').strip() or None
            image = (data.get('image') or '').strip() or None

            if len(name) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do aluno deve ter no mínimo 3 caracteres'
                }), 400)
            if len(email) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Email do aluno deve ter no mínimo 3 caracteres'
                }), 400)
            if len(registration) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'RA do aluno deve ter no mínimo 3 caracteres'
                }), 400)
            if Student.check_student_email_exists(email):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Já existe um aluno cadastrado com este email'
                }), 409)
            if Student.check_student_registration_exists(registration):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Já existe um aluno cadastrado com este RA'
                }), 409)
            student_id = Student.insert_student(name, email, registration, observation, image)

            if student_id:
                return make_response(jsonify({
                    'success': True,
                    'message': 'Aluno cadastrado com sucesso!',
                    'student_id': student_id
                }), 201)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao cadastrar aluno'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao cadastrar aluno',
                'error': str(e)
            }), 500)

    @token_required
    @student_ns.doc('update_student', description='Atualiza um aluno existente')
    @student_ns.expect(student_update_model)
    @student_ns.response(200, 'Aluno atualizado com sucesso')
    @student_ns.response(404, 'Aluno não encontrado')
    @student_ns.response(409, 'email já existe')
    def put(self, current_user_id):
        """Atualiza um aluno"""
        try:
            data = get_json_data()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do aluno é obrigatório'
                }), 400)

            student_id = data.get('id')
            name = (data.get('name') or '').strip() if 'name' in data and data.get('name') else None
            email = (data.get('email') or '').strip() if 'email' in data and data.get('email') else None
            registration = (data.get('registration') or '').strip() if 'registration' in data and data.get('registration') else None
            telephone = (data.get('telephone') or '').strip() if 'telephone' in data and data.get('telephone') else None
            observation = (data.get('observation') or '').strip() if 'observation' in data and data.get('observation') else None
            image = (data.get('image') or '').strip() if 'image' in data and data.get('image') else None
            
            if not Student.check_student_exists(student_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Aluno não encontrado'
                }), 404)
            if name:
                if len(name) < 3:
                    return make_response(jsonify({
                        'success': False,
                        'message': 'Nome do aluno deve ter no mínimo 3 caracteres'
                    }), 400)
                Student.update_name(student_id, name)
            if email:
                if Student.check_student_email_exists(email, student_id=student_id):
                    return make_response(jsonify({
                        'success': False,
                        'message': 'Já existe outro aluno com este email'
                    }), 409)
                Student.update_email(student_id, email)
            if registration:
                if Student.check_student_registration_exists(registration, student_id):
                    return make_response(jsonify({
                        'success': False,
                        'message': 'Já existe outro aluno com este RA'
                    }), 409)
                Student.update_registration(student_id, registration)
            
            if telephone is not None:
                Student.update_telephone(student_id, telephone)

            Student.update_observation_and_image(student_id, observation, image)
            return make_response(jsonify({
                'success': True,
                'message': 'Aluno atualizado com sucesso!'
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao atualizar aluno',
                'error': str(e)
            }), 500)

    @token_required
    @student_ns.doc('delete_student', description='Remove um aluno (exclusão lógica)')
    @student_ns.expect(student_delete_model)
    @student_ns.response(200, 'Aluno desativado com sucesso')
    @student_ns.response(404, 'Aluno não encontrado')
    def delete(self, current_user_id):
        """Remove um aluno (marca como inativo)"""
        try:
            data = get_json_data()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do aluno é obrigatório'
                }), 400)

            student_id = data.get('id')
            student = Student.select_student_by_id(student_id)
            if not student:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Aluno não encontrado'
                }), 404)
            if Student.delete_student(student_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Aluno desativado com sucesso!'
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

@student_ns.route('/active')
class ActiveStudent(Resource):
    """Endpoint para ativação de aluno"""

    @token_required
    @student_ns.doc('active_student', description='Ativar um aluno (Ativação)')
    @student_ns.expect(student_active_model)
    @student_ns.response(200, 'Aluno ativado com sucesso')
    @student_ns.response(404, 'Aluno não encontrado')
    def post(self, current_user_id):
        """Ativa um aluno (marca como ativo)"""
        try:
            data = get_json_data()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do aluno é obrigatório'
                }), 400)

            student_id = data.get('id')
            student = Student.select_student_by_id(student_id)
            if not student:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Aluno não encontrado'
                }), 404)
            if Student.activate_student(student_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Aluno ativado com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao ativar aluno'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao ativar aluno',
                'error': str(e)
            }), 500)

@student_ns.route('/<int:student_id>')
class StudentDetail(Resource):
    """Endpoints para busca de alunos específico"""

    @token_required
    @student_ns.doc('get_student', description='Busca um aluno por ID')
    @student_ns.response(200, 'Aluno encontrado', student_model)
    @student_ns.response(404, 'Aluno não encontrado')
    def get(self, current_user_id, student_id):
        """Busca um aluno específico por ID"""
        try:
            student = Student.select_student_by_id(student_id)

            if not student:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Aluno não encontrado'
                }), 404)

            return make_response(jsonify({
                'success': True,
                'student': format_student_response(student)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar aluno',
                'error': str(e)
            }), 500)


@student_ns.route('/search')
class StudentSearch(Resource):
    """Endpoints para busca avançada de alunos"""

    @token_required
    @student_ns.doc('search_students', description='Busca alunos com filtros')
    @student_ns.expect(student_search_model)
    @student_ns.response(200, 'Busca realizada com sucesso', [student_model])
    def post(self, current_user_id):
        """Busca alunos com filtros avançados"""
        try:
            data = get_json_data()

            name = data.get('name')
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            if name:
                students = Student.select_student_by_name(name)
            elif start_date or end_date:
                students = Student.select_student_by_date_range(start_date, end_date)
            else:
                students = Student.select_all_student()

            response = [format_student_response(student) for student in students]

            return make_response(jsonify({
                'success': True,
                'students': response,
                'total': len(response)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar alunos',
                'error': str(e)
            }), 500)
