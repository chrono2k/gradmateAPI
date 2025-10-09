from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace, fields
from decorators import token_required
from models.teacher_model import Teacher
from datetime import datetime

teacher_ns = Namespace('teacher', description='Gerenciamento de professores')

teacher_model = teacher_ns.model('Teacher', {
    'id': fields.Integer(description='ID do professor'),
    'name': fields.String(required=True, description='Nome do professor'),
    'observation': fields.String(description='Observação sobre o professor'),
    'image': fields.String(description='Imagem do professor'),
    'user_id': fields.String(description='Id do usuário do professor'),
    'created_at': fields.DateTime(description='Data de criação'),
    'updated_at': fields.DateTime(description='Data de atualização')
})

teacher_create_model = teacher_ns.model('TeacherCreate', {
    'name': fields.String(required=True, description='Nome do professor', min_length=3, max_length=255),
    'email': fields.String(required=True, description='Email/login do professor', min_length=3, max_length=255),
    'observation': fields.String(description='Observação sobre o professor'),
    'image': fields.String(description='Imagem do professor')
})

teacher_update_model = teacher_ns.model('TeacherUpdate', {
    'id': fields.Integer(required=True, description='ID do professor'),
    'name': fields.String(description='Novo nome do professor'),
    'email': fields.String(description='Novo email do professor'),
    'observation': fields.String(description='Nova observação'),
    'image': fields.String(description='Nova imagem')
})

teacher_delete_model = teacher_ns.model('TeacherDelete', {
    'id': fields.Integer(required=True, description='ID do professor a ser desativado')
})
teacher_active_model = teacher_ns.model('TeacherActive', {
    'id': fields.Integer(required=True, description='ID do professor a ser ativado')
})

teacher_search_model = teacher_ns.model('TeacherSearch', {
    'name': fields.String(description='Nome do professor para buscar'),
    'start_date': fields.String(description='Data inicial (YYYY-MM-DD)'),
    'end_date': fields.String(description='Data final (YYYY-MM-DD)'),
})


def format_teacher_response(teacher_data):
    """
    Formata os dados do professor para resposta da API

    Args:
        teacher_data (tuple): Tupla com dados do professor do banco

    Returns:
        dict: Dicionário formatado
    """
    return {
        'id': teacher_data[0],
        'name': teacher_data[1],
        'observation': teacher_data[2],
        'image': teacher_data[3],
        'user_id': teacher_data[4],
        'created_at': teacher_data[5].isoformat() if teacher_data[5] else None,
        'updated_at': teacher_data[6].isoformat() if teacher_data[6] else None
    }


@teacher_ns.route('/')
class TeacherList(Resource):
    """Endpoints para listar e criar professores"""

    @token_required
    @teacher_ns.doc('list_teacher', description='Lista todos os professores')
    @teacher_ns.response(200, 'Lista de professores retornada com sucesso', [teacher_model])
    @teacher_ns.response(401, 'Não autorizado')
    @teacher_ns.response(500, 'Erro interno do servidor')
    def get(self, current_user_id):
        """Lista todos os professores"""
        try:
            teachers = Teacher.select_all_teachers()
            response = [format_teacher_response(teacher) for teacher in teachers]

            return make_response(jsonify({
                'success': True,
                'teachers': response,
                'total': len(response)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar professores',
                'error': str(e)
            }), 500)

    @token_required
    @teacher_ns.doc('create_teacher', description='Cria um novo professor')
    @teacher_ns.expect(teacher_create_model)
    @teacher_ns.response(201, 'Professor criado com sucesso')
    @teacher_ns.response(400, 'Dados inválidos')
    @teacher_ns.response(409, 'Professor já existe')
    def post(self, current_user_id):
        """Cria um novo professor"""
        try:
            data = request.get_json()
            if not data or 'name' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do professor é obrigatório'
                }), 400)
            if not data or 'email' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Email do professor é obrigatório'
                }), 400)

            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            observation = data.get('observation', '').strip() or None
            image = data.get('image', '').strip() or None

            if len(name) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do professor deve ter no mínimo 3 caracteres'
                }), 400)
            if len(email) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Email do professor deve ter no mínimo 3 caracteres'
                }), 400)
            if Teacher.check_teacher_email_exists(name):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Já existe um professor cadastrado com este email'
                }), 409)
            teacher_id = Teacher.insert_teacher(name, email, observation, image)

            if teacher_id:
                return make_response(jsonify({
                    'success': True,
                    'message': 'Professor cadastrado com sucesso!',
                    'teacher_id': teacher_id
                }), 201)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao cadastrar professor'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao cadastrar professor',
                'error': str(e)
            }), 500)

    @token_required
    @teacher_ns.doc('update_teacher', description='Atualiza um professor existente')
    @teacher_ns.expect(teacher_update_model)
    @teacher_ns.response(200, 'Professor atualizado com sucesso')
    @teacher_ns.response(404, 'Professor não encontrado')
    @teacher_ns.response(409, 'email já existe')
    def put(self, current_user_id):
        """Atualiza um professor"""
        try:
            data = request.get_json()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do professor é obrigatório'
                }), 400)

            teacher_id = data.get('id')
            name = data.get('name', '').strip() if 'name' in data else None
            email = data.get('email', '').strip() if 'email' in data else None
            observation = data.get('observation', '').strip() if 'observation' in data else None
            image = data.get('image', '').strip() if 'image' in data else None
            if not Teacher.check_teacher_exists(teacher_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Professor não encontrado'
                }), 404)
            if name:
                if len(name) < 3:
                    return make_response(jsonify({
                        'success': False,
                        'message': 'Nome do curso professor ter no mínimo 3 caracteres'
                    }), 400)
                Teacher.update_name(teacher_id, name)
            if email:
                if Teacher.check_teacher_email_exists(email, exclude_id=teacher_id):
                    return make_response(jsonify({
                        'success': False,
                        'message': 'Já existe outro professor com este email'
                    }), 409)
                Teacher.update_email(teacher_id, email)
            Teacher.update_observation_and_image(teacher_id, observation,image)
            return make_response(jsonify({
                'success': True,
                'message': 'Curso atualizado com sucesso!'
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao atualizar curso',
                'error': str(e)
            }), 500)

    @token_required
    @teacher_ns.doc('delete_teacher', description='Remove um professor (exclusão lógica)')
    @teacher_ns.expect(teacher_delete_model)
    @teacher_ns.response(200, 'Professor desativado com sucesso')
    @teacher_ns.response(404, 'Professor não encontrado')
    def delete(self, current_user_id):
        """Remove um professor (marca como inativo)"""
        try:
            data = request.get_json()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do professor é obrigatório'
                }), 400)

            teacher_id = data.get('id')
            teacher = Teacher.select_teacher_by_id(teacher_id)
            if not teacher:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Professor não encontrado'
                }), 404)
            if Teacher.delete_teacher(teacher_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Professor desativado com sucesso!'
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

@teacher_ns.route('/active')
class ActiveTeacher(Resource):
    """Endpoint para ativação de professor"""

    @token_required
    @teacher_ns.doc('active_teacher', description='Ativar um professor (Ativação)')
    @teacher_ns.expect(teacher_active_model)
    @teacher_ns.response(200, 'Professor ativado com sucesso')
    @teacher_ns.response(404, 'Professor não encontrado')
    def post(self, current_user_id):
        """Ativa um professor (marca como ativo)"""
        try:
            data = request.get_json()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do professor é obrigatório'
                }), 400)

            teacher_id = data.get('id')
            teacher = Teacher.select_teacher_by_id(teacher_id)
            if not teacher:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Professor não encontrado'
                }), 404)
            if Teacher.activate_teacher(teacher_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Professor ativado com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao ativar professor'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao ativar professor',
                'error': str(e)
            }), 500)

@teacher_ns.route('/<int:teacher_id>')
class teacherDetail(Resource):
    """Endpoints para busca de professores específico"""

    @token_required
    @teacher_ns.doc('get_teacher', description='Busca um professor por ID')
    @teacher_ns.response(200, 'Professor encontrado', teacher_model)
    @teacher_ns.response(404, 'Professor não encontrado')
    def get(self, current_user_id, teacher_id):
        """Busca um professor específico por ID"""
        try:
            teacher = Teacher.select_teacher_by_id(teacher_id)

            if not teacher:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Professor não encontrado'
                }), 404)

            return make_response(jsonify({
                'success': True,
                'teacher': format_teacher_response(teacher)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar professor',
                'error': str(e)
            }), 500)


@teacher_ns.route('/search')
class CourseSearch(Resource):
    """Endpoints para busca avançada de professores"""

    @token_required
    @teacher_ns.doc('search_teachers', description='Busca professores com filtros')
    @teacher_ns.expect(teacher_search_model)
    @teacher_ns.response(200, 'Busca realizada com sucesso', [teacher_model])
    def post(self, current_user_id):
        """Busca professores com filtros avançados"""
        try:
            data = request.get_json() or {}

            name = data.get('name')
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            if name:
                teachers = Teacher.select_teacher_by_name(name)
            elif start_date or end_date:
                teachers = Teacher.select_teacher_by_date_range(start_date, end_date)
            else:
                teachers = Teacher.select_all_teacher()

            response = [format_teacher_response(teacher) for teacher in teachers]

            return make_response(jsonify({
                'success': True,
                'teachers': response,
                'total': len(response)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar Professores',
                'error': str(e)
            }), 500)