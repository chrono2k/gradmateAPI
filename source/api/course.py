from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace, fields
from decorators import token_required
from models.course_model import Course
from datetime import datetime

course_ns = Namespace('course', description='Gerenciamento de cursos')

course_model = course_ns.model('Course', {
    'id': fields.Integer(description='ID do curso'),
    'name': fields.String(required=True, description='Nome do curso'),
    'observation': fields.String(description='Observação sobre o curso'),
    'status': fields.String(description='Status do curso', enum=['ativo', 'inativo']),
    'created_at': fields.DateTime(description='Data de criação'),
    'updated_at': fields.DateTime(description='Data de atualização')
})

course_create_model = course_ns.model('CourseCreate', {
    'name': fields.String(required=True, description='Nome do curso', min_length=3, max_length=255),
    'observation': fields.String(description='Observação sobre o curso')
})

course_update_model = course_ns.model('CourseUpdate', {
    'id': fields.Integer(required=True, description='ID do curso'),
    'name': fields.String(description='Novo nome do curso'),
    'observation': fields.String(description='Nova observação')
})

course_delete_model = course_ns.model('CourseDelete', {
    'id': fields.Integer(required=True, description='ID do curso a ser desativado')
})
course_active_model = course_ns.model('CourseActive', {
    'id': fields.Integer(required=True, description='ID do curso a ser ativado')
})

course_search_model = course_ns.model('CourseSearch', {
    'name': fields.String(description='Nome do curso para buscar'),
    'start_date': fields.String(description='Data inicial (YYYY-MM-DD)'),
    'end_date': fields.String(description='Data final (YYYY-MM-DD)'),
    'status': fields.String(description='Status', enum=['ativo', 'inativo', 'all'])
})

course_statistics_model = course_ns.model('CourseStatistics', {
    'total': fields.Integer(description='Total de cursos'),
    'ativos': fields.Integer(description='Cursos ativos'),
    'inativos': fields.Integer(description='Cursos inativos'),
    'ultimo_cadastro': fields.DateTime(description='Data do último cadastro')
})


def format_course_response(course_data):
    """
    Formata os dados do curso para resposta da API

    Args:
        course_data (tuple): Tupla com dados do curso do banco

    Returns:
        dict: Dicionário formatado
    """
    return {
        'id': course_data[0],
        'name': course_data[1],
        'observation': course_data[2],
        'status': course_data[3],
        'created_at': course_data[4].isoformat() if course_data[4] else None,
        'updated_at': course_data[5].isoformat() if course_data[5] else None
    }


@course_ns.route('/')
class CourseList(Resource):
    """Endpoints para listar e criar cursos"""

    @token_required
    @course_ns.doc('list_courses', description='Lista todos os cursos ativos')
    @course_ns.param('status', 'Status dos cursos (ativo/inativo/all)', _in='query')
    @course_ns.response(200, 'Lista de cursos retornada com sucesso', [course_model])
    @course_ns.response(401, 'Não autorizado')
    @course_ns.response(500, 'Erro interno do servidor')
    def get(self, current_user_id):
        """Lista todos os cursos"""
        try:
            status = request.args.get('status', 'ativo')
            if status not in ['ativo', 'inativo', 'all']:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Status inválido. Use: ativo, inativo ou all'
                }), 400)

            courses = Course.select_all_courses(status)
            response = [format_course_response(course) for course in courses]

            return make_response(jsonify({
                'success': True,
                'courses': response,
                'total': len(response)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar cursos',
                'error': str(e)
            }), 500)

    @token_required
    @course_ns.doc('create_course', description='Cria um novo curso')
    @course_ns.expect(course_create_model)
    @course_ns.response(201, 'Curso criado com sucesso')
    @course_ns.response(400, 'Dados inválidos')
    @course_ns.response(409, 'Curso já existe')
    def post(self, current_user_id):
        """Cria um novo curso"""
        try:
            data = request.get_json()
            if not data or 'name' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do curso é obrigatório'
                }), 400)

            name = data.get('name', '').strip()
            observation = data.get('observation', '').strip() or None

            if len(name) < 3:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do curso deve ter no mínimo 3 caracteres'
                }), 400)
            if Course.check_course_name_exists(name):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Já existe um curso cadastrado com este nome'
                }), 409)
            course_id = Course.insert_course(name, observation)

            if course_id:
                return make_response(jsonify({
                    'success': True,
                    'message': 'Curso cadastrado com sucesso!',
                    'course_id': course_id
                }), 201)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao cadastrar curso'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao cadastrar curso',
                'error': str(e)
            }), 500)

    @token_required
    @course_ns.doc('update_course', description='Atualiza um curso existente')
    @course_ns.expect(course_update_model)
    @course_ns.response(200, 'Curso atualizado com sucesso')
    @course_ns.response(404, 'Curso não encontrado')
    @course_ns.response(409, 'Nome já existe')
    def put(self, current_user_id):
        """Atualiza um curso"""
        try:
            data = request.get_json()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do curso é obrigatório'
                }), 400)

            course_id = data.get('id')
            name = data.get('name', '').strip() if 'name' in data else None
            observation = data.get('observation', '').strip() if 'observation' in data else None
            if not Course.check_course_exists(course_id):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Curso não encontrado'
                }), 404)
            if name:
                if len(name) < 3:
                    return make_response(jsonify({
                        'success': False,
                        'message': 'Nome do curso deve ter no mínimo 3 caracteres'
                    }), 400)
                if Course.check_course_name_exists(name, exclude_id=course_id):
                    return make_response(jsonify({
                        'success': False,
                        'message': 'Já existe outro curso com este nome'
                    }), 409)
            if Course.update_course(course_id, name, observation):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Curso atualizado com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nenhuma alteração foi realizada'
                }), 400)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao atualizar curso',
                'error': str(e)
            }), 500)

    @token_required
    @course_ns.doc('delete_course', description='Remove um curso (exclusão lógica)')
    @course_ns.expect(course_delete_model)
    @course_ns.response(200, 'Curso desativado com sucesso')
    @course_ns.response(404, 'Curso não encontrado')
    def delete(self, current_user_id):
        """Remove um curso (marca como inativo)"""
        try:
            data = request.get_json()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do curso é obrigatório'
                }), 400)

            course_id = data.get('id')
            course = Course.select_course_by_id(course_id)
            if not course:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Curso não encontrado'
                }), 404)
            if Course.delete_course(course_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Curso desativado com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao remover curso'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao remover curso',
                'error': str(e)
            }), 500)

@course_ns.route('/active')
class ActiveCourse(Resource):
    """Endpoint para ativação de curso"""

    @token_required
    @course_ns.doc('active_course', description='Ativar um curso (Ativação)')
    @course_ns.expect(course_active_model)
    @course_ns.response(200, 'Curso ativado com sucesso')
    @course_ns.response(404, 'Curso não encontrado')
    def post(self, current_user_id):
        """Ativa um curso (marca como ativo)"""
        try:
            data = request.get_json()

            if not data or 'id' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'ID do curso é obrigatório'
                }), 400)

            course_id = data.get('id')
            course = Course.select_course_by_id(course_id)
            if not course:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Curso não encontrado'
                }), 404)
            if Course.activate_course(course_id):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Curso ativado com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao ativar curso'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao ativar curso',
                'error': str(e)
            }), 500)

@course_ns.route('/<int:course_id>')
class CourseDetail(Resource):
    """Endpoints para operações em curso específico"""

    @token_required
    @course_ns.doc('get_course', description='Busca um curso por ID')
    @course_ns.response(200, 'Curso encontrado', course_model)
    @course_ns.response(404, 'Curso não encontrado')
    def get(self, current_user_id, course_id):
        """Busca um curso específico por ID"""
        try:
            course = Course.select_course_by_id(course_id)

            if not course:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Curso não encontrado'
                }), 404)

            return make_response(jsonify({
                'success': True,
                'course': format_course_response(course)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar curso',
                'error': str(e)
            }), 500)


@course_ns.route('/search')
class CourseSearch(Resource):
    """Endpoints para busca avançada de cursos"""

    @token_required
    @course_ns.doc('search_courses', description='Busca cursos com filtros')
    @course_ns.expect(course_search_model)
    @course_ns.response(200, 'Busca realizada com sucesso', [course_model])
    def post(self, current_user_id):
        """Busca cursos com filtros avançados"""
        try:
            data = request.get_json() or {}

            name = data.get('name')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            status = data.get('status', 'ativo')
            if name:
                courses = Course.select_courses_by_name(name)
            elif start_date or end_date:
                courses = Course.select_courses_by_date_range(start_date, end_date, status)
            else:
                courses = Course.select_all_courses(status)

            response = [format_course_response(course) for course in courses]

            return make_response(jsonify({
                'success': True,
                'courses': response,
                'total': len(response)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar cursos',
                'error': str(e)
            }), 500)


@course_ns.route('/statistics')
class CourseStatistics(Resource):
    """Endpoints para estatísticas de cursos"""

    @token_required
    @course_ns.doc('get_statistics', description='Retorna estatísticas dos cursos')
    @course_ns.response(200, 'Estatísticas retornadas com sucesso', course_statistics_model)
    def get(self, current_user_id):
        """Retorna estatísticas dos cursos"""
        try:
            stats = Course.get_course_statistics()
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