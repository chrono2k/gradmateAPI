from flask import request, jsonify, make_response, send_file
from flask_restx import Resource, Namespace, fields
from decorators import token_required
from models.course_model import Course
from datetime import datetime
from utils.request_utils import get_json_data
from utils.signature_utils import save_signature_file, delete_signature_file, get_signatures_upload_dir
import os

course_ns = Namespace('course', description='Gerenciamento de cursos')

course_model = course_ns.model('Course', {
    'id': fields.Integer(description='ID do curso'),
    'name': fields.String(required=True, description='Nome do curso'),
    'observation': fields.String(description='Observação sobre o curso'),
    'status': fields.String(description='Status do curso', enum=['ativo', 'inativo']),
    'created_at': fields.DateTime(description='Data de criação'),
    'updated_at': fields.DateTime(description='Data de atualização'),
    'responsible_teacher_name': fields.String(description='Nome do professor responsável/coordenador'),
    'responsible_signature_url': fields.String(description='URL da assinatura digital')
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
    if not course_data:
        return None
    return {
        'id': course_data[0],
        'name': course_data[1],
        'observation': course_data[2],
        'status': course_data[3],
        'created_at': course_data[4].isoformat() if course_data[4] else None,
        'updated_at': course_data[5].isoformat() if course_data[5] else None,
        'responsible_teacher_name': course_data[6] if len(course_data) > 6 else None,
        'responsible_signature_url': course_data[7] if len(course_data) > 7 else None
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
            print(f"Erro ao formatar projeto: {e}")
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar cursos',
                'error': str(e)
            }), 500)

    @token_required
    @course_ns.doc('create_course', description='Cria um novo curso (suporta JSON ou multipart/form-data com assinatura)')
    @course_ns.response(201, 'Curso criado com sucesso')
    @course_ns.response(400, 'Dados inválidos')
    @course_ns.response(409, 'Curso já existe')
    def post(self, current_user_id):
        """Cria um novo curso (JSON ou multipart com assinatura)"""
        try:
            # Detectar se é multipart/form-data ou JSON
            is_multipart = request.content_type and 'multipart/form-data' in request.content_type
            
            if is_multipart:
                # Processar FormData
                name = request.form.get('name', '').strip()
                observation = request.form.get('observation', '').strip() or None
                responsible_teacher_name = request.form.get('responsible_teacher_name', '').strip() or None
                signature_file = request.files.get('signature')
            else:
                # Processar JSON
                data = get_json_data()
                if not data or 'name' not in data:
                    return make_response(jsonify({
                        'success': False,
                        'message': 'Nome do curso é obrigatório'
                    }), 400)
                name = data.get('name', '').strip()
                observation = data.get('observation', '').strip() or None
                responsible_teacher_name = data.get('responsible_teacher_name', '').strip() or None
                signature_file = None

            # Validações
            if not name:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome do curso é obrigatório'
                }), 400)

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

            # Inserir curso no banco (sem assinatura ainda)
            course_id = Course.insert_course(name, observation, responsible_teacher_name, None)

            if not course_id:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao cadastrar curso'
                }), 500)

            # Processar upload de assinatura se houver
            signature_url = None
            if signature_file:
                try:
                    signature_url = save_signature_file(signature_file, course_id)
                    # Atualizar curso com URL da assinatura
                    Course.update_course(course_id, responsible_signature_url=signature_url)
                except ValueError as ve:
                    # Se falhar no upload, remover curso e retornar erro
                    Course.permanent_delete_course(course_id)
                    return make_response(jsonify({
                        'success': False,
                        'message': f'Erro no upload da assinatura: {str(ve)}'
                    }), 400)

            # Buscar curso criado para retornar
            course = Course.select_course_by_id(course_id)
            return make_response(jsonify({
                'success': True,
                'message': 'Curso cadastrado com sucesso!',
                'course': format_course_response(course)
            }), 201)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao cadastrar curso',
                'error': str(e)
            }), 500)

    @token_required
    @course_ns.doc('update_course', description='Atualiza um curso existente (suporta JSON ou multipart/form-data)')
    @course_ns.response(200, 'Curso atualizado com sucesso')
    @course_ns.response(404, 'Curso não encontrado')
    @course_ns.response(409, 'Nome já existe')
    def put(self, current_user_id):
        """Atualiza um curso (JSON ou multipart com nova assinatura)"""
        try:
            # Detectar se é multipart/form-data ou JSON
            is_multipart = request.content_type and 'multipart/form-data' in request.content_type
            
            if is_multipart:
                # Processar FormData
                try:
                    course_id = int(request.form.get('id'))
                except (TypeError, ValueError):
                    return make_response(jsonify({
                        'success': False,
                        'message': 'ID do curso é obrigatório e deve ser um número'
                    }), 400)
                
                name = request.form.get('name', '').strip() if 'name' in request.form else None
                observation = request.form.get('observation', '').strip() if 'observation' in request.form else None
                responsible_teacher_name = request.form.get('responsible_teacher_name', '').strip() if 'responsible_teacher_name' in request.form else None
                signature_file = request.files.get('signature')
                remove_signature = False
            else:
                # Processar JSON
                data = get_json_data()
                if not data or 'id' not in data:
                    return make_response(jsonify({
                        'success': False,
                        'message': 'ID do curso é obrigatório'
                    }), 400)

                course_id = data.get('id')
                name = data.get('name', '').strip() if 'name' in data else None
                observation = data.get('observation', '').strip() if 'observation' in data else None
                responsible_teacher_name = data.get('responsible_teacher_name', '').strip() if 'responsible_teacher_name' in data else None
                signature_file = None
                remove_signature = data.get('remove_signature', False)

            # Verificar se curso existe e obter dados atuais
            current_course = Course.select_course_by_id(course_id)
            if not current_course:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Curso não encontrado'
                }), 404)

            # Validar nome se fornecido
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

            # Gerenciar assinatura
            new_signature_url = None
            old_signature_url = current_course[7] if len(current_course) > 7 else None

            if signature_file:
                # Upload de nova assinatura
                try:
                    new_signature_url = save_signature_file(signature_file, course_id)
                    # Deletar assinatura antiga se existir
                    if old_signature_url:
                        delete_signature_file(old_signature_url)
                except ValueError as ve:
                    return make_response(jsonify({
                        'success': False,
                        'message': f'Erro no upload da assinatura: {str(ve)}'
                    }), 400)
            elif remove_signature:
                # Remover assinatura existente
                if old_signature_url:
                    delete_signature_file(old_signature_url)
                new_signature_url = None  # Seta NULL no banco
            # else: manter assinatura existente (não passa parâmetro)

            # Atualizar curso
            update_params = {}
            if name is not None:
                update_params['name'] = name
            if observation is not None:
                update_params['observation'] = observation
            if responsible_teacher_name is not None:
                update_params['responsible_teacher_name'] = responsible_teacher_name
            if signature_file or remove_signature:
                update_params['responsible_signature_url'] = new_signature_url

            if not update_params:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nenhuma alteração foi realizada'
                }), 400)

            if Course.update_course(course_id, **update_params):
                # Buscar curso atualizado
                updated_course = Course.select_course_by_id(course_id)
                return make_response(jsonify({
                    'success': True,
                    'message': 'Curso atualizado com sucesso!',
                    'course': format_course_response(updated_course)
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao atualizar curso'
                }), 500)

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
            data = get_json_data()

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
            data = get_json_data()

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
            data = get_json_data()

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


@course_ns.route('/signature/<string:filename>')
class CourseSignatureDownload(Resource):
    """Endpoint para download de assinaturas de curso"""

    @course_ns.doc('download_signature', description='Baixa arquivo de assinatura')
    @course_ns.response(200, 'Arquivo encontrado')
    @course_ns.response(404, 'Arquivo não encontrado')
    def get(self, filename):
        """Serve arquivo de assinatura (público para certificados)"""
        try:
            # Validar nome do arquivo (evitar path traversal)
            if '..' in filename or '/' in filename or '\\' in filename:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Nome de arquivo inválido'
                }), 400)

            upload_dir = get_signatures_upload_dir()
            filepath = os.path.join(upload_dir, filename)

            if not os.path.exists(filepath):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Arquivo não encontrado'
                }), 404)

            # Determinar MIME type baseado na extensão
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            mime_types = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg'
            }
            mimetype = mime_types.get(ext, 'application/octet-stream')

            return send_file(filepath, mimetype=mimetype, as_attachment=False)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar arquivo',
                'error': str(e)
            }), 500)