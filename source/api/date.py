from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace, fields
from decorators import token_required
from utils.request_utils import get_json_data
from models.date_model import DateStatus
from datetime import datetime

date_status_ns = Namespace('date-status', description='Gerenciamento de status de datas')

date_status_model = date_status_ns.model('DateStatus', {
    'id': fields.Integer(description='ID do status'),
    'date': fields.String(required=True, description='Data (YYYY-MM-DD)'),
    'status': fields.Integer(required=True, description='Status (1, 2, 3, 4, 5 ou 6)', enum=[1, 2, 3]),
    'created_at': fields.DateTime(description='Data de criação'),
    'updated_at': fields.DateTime(description='Data de atualização')
})

date_status_create_model = date_status_ns.model('DateStatusCreate', {
    'date': fields.String(required=True, description='Data (YYYY-MM-DD)'),
    'status': fields.Integer(required=True, description='Status (1, 2, 3, 4, 5 ou 6)', enum=[1, 2, 3], min=1, max=6)
})

date_status_update_model = date_status_ns.model('DateStatusUpdate', {
    'date': fields.String(required=True, description='Data (YYYY-MM-DD)'),
    'status': fields.Integer(required=True, description='Status (1, 2, 3, 4, 5 ou 6)', enum=[1, 2, 3], min=1, max=6)
})

date_status_delete_model = date_status_ns.model('DateStatusDelete', {
    'date': fields.String(required=True, description='Data (YYYY-MM-DD)')
})

date_status_statistics_model = date_status_ns.model('DateStatusStatistics', {
    'total': fields.Integer(description='Total de datas com status'),
    'status_1': fields.Integer(description='Total com status 1'),
    'status_2': fields.Integer(description='Total com status 2'),
    'status_3': fields.Integer(description='Total com status 3'),
    'status_4': fields.Integer(description='Total com status 4'),
    'status_5': fields.Integer(description='Total com status 5'),
    'status_6': fields.Integer(description='Total com status 6')
})


def format_date_status_response(status_data):
    """
    Formata os dados do status de data para resposta da API

    Args:
        status_data (tuple): Tupla com dados do status

    Returns:
        dict: Dicionário formatado
    """
    return {
        'id': status_data[0],
        'date': status_data[1].isoformat() if hasattr(status_data[1], 'isoformat') else str(status_data[1]),
        'status': status_data[2],
        'created_at': status_data[3].isoformat() if status_data[3] else None,
        'updated_at': status_data[4].isoformat() if status_data[4] else None
    }


def validate_date_format(date_str):
    """Valida se a data está no formato YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


@date_status_ns.route('/')
class DateStatusList(Resource):
    """Endpoints para listar e criar status de datas"""

    @token_required
    @date_status_ns.doc('list_date_statuses')
    @date_status_ns.param('year', 'Ano para filtrar', _in='query', type='int')
    @date_status_ns.response(200, 'Lista de status de datas', [date_status_model])
    @date_status_ns.response(401, 'Não autorizado')
    def get(self, current_user_id):
        """Lista todos os status de datas, opcionalmente filtrado por ano"""
        try:
            year = request.args.get('year', type=int)

            statuses = DateStatus.select_all_date_statuses(year)
            response = [format_date_status_response(status) for status in statuses]

            return make_response(jsonify({
                'success': True,
                'statuses': response,
                'total': len(response)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar status de datas',
                'error': str(e)
            }), 500)

    @token_required
    @date_status_ns.doc('create_date_status')
    @date_status_ns.expect(date_status_create_model)
    @date_status_ns.response(201, 'Status de data criado com sucesso')
    @date_status_ns.response(400, 'Dados inválidos')
    def post(self, current_user_id):
        """Cria um novo status de data"""
        try:
            data = get_json_data()


            if not data or 'date' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Data é obrigatório'
                }), 400)

            date_str = data.get('date')
            status = data.get('status')

            if not validate_date_format(date_str):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Data deve estar no formato YYYY-MM-DD'
                }), 400)

            if status not in [1, 2, 3, 4, 5, 6]:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Status deve estar entre 1 e 6'
                }), 400)

            status_id = DateStatus.insert_date_status(date_str, status)

            if status_id:
                return make_response(jsonify({
                    'success': True,
                    'message': 'Status de data criado com sucesso!',
                    'status_id': status_id
                }), 201)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao criar status de data'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao criar status de data',
                'error': str(e)
            }), 500)

    @token_required
    @date_status_ns.doc('update_date_status')
    @date_status_ns.expect(date_status_update_model)
    @date_status_ns.response(200, 'Status de data atualizado com sucesso')
    @date_status_ns.response(400, 'Dados inválidos')
    def put(self, current_user_id):
        """Atualiza ou cria o status de uma data"""
        try:
            data = get_json_data()

            if not data or 'date' not in data or 'status' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Data e status são obrigatórios'
                }), 400)

            date_str = data.get('date')
            status = data.get('status')

            if not validate_date_format(date_str):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Data deve estar no formato YYYY-MM-DD'
                }), 400)

            if status not in [1, 2, 3, 4, 5, 6]:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Status deve estar entre 1 e 6'
                }), 400)

            if DateStatus.update_date_status_by_date(date_str, status):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Status de data atualizado com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao atualizar status de data'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao atualizar status de data',
                'error': str(e)
            }), 500)

    @token_required
    @date_status_ns.doc('delete_date_status')
    @date_status_ns.expect(date_status_delete_model)
    @date_status_ns.response(200, 'Status de data removido com sucesso')
    @date_status_ns.response(404, 'Status não encontrado')
    def delete(self, current_user_id):
        """Remove o status de uma data"""
        try:
            data = get_json_data()

            if not data or 'date' not in data:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Data é obrigatória'
                }), 400)

            date_str = data.get('date')

            if not validate_date_format(date_str):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Data deve estar no formato YYYY-MM-DD'
                }), 400)

            if not DateStatus.check_date_status_exists(date_str):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Status não encontrado para essa data'
                }), 404)

            if DateStatus.delete_date_status_by_date(date_str):
                return make_response(jsonify({
                    'success': True,
                    'message': 'Status de data removido com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao remover status de data'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao remover status de data',
                'error': str(e)
            }), 500)


@date_status_ns.route('/year/<int:year>')
class DateStatusYear(Resource):
    """Endpoints para operações específicas de um ano"""

    @token_required
    @date_status_ns.doc('get_year_statuses')
    @date_status_ns.response(200, 'Statuses do ano em formato dicionário')
    def get(self, current_user_id, year):
        """Retorna todos os status de datas de um ano em formato dicionário"""
        try:
            statuses = DateStatus.get_statuses_for_year(year)

            return make_response(jsonify({
                'success': True,
                'year': year,
                'statuses': statuses,
                'total': len(statuses)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar status do ano',
                'error': str(e)
            }), 500)

    @token_required
    @date_status_ns.doc('clear_year_statuses')
    @date_status_ns.response(200, 'Todos os status do ano foram removidos')
    def delete(self, current_user_id, year):
        """Remove todos os status de datas de um ano específico"""
        try:
            if not confirm_year_deletion(year):
                return make_response(jsonify({
                    'success': False,
                    'message': 'Exclusão não confirmada'
                }), 400)

            if DateStatus.clear_year_statuses(year):
                return make_response(jsonify({
                    'success': True,
                    'message': f'Todos os status de {year} foram removidos com sucesso!'
                }), 200)
            else:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Erro ao remover status do ano'
                }), 500)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao remover status do ano',
                'error': str(e)
            }), 500)


@date_status_ns.route('/statistics')
class DateStatusStatistics(Resource):
    """Endpoints para estatísticas de status de datas"""

    @token_required
    @date_status_ns.doc('get_statistics')
    @date_status_ns.param('year', 'Ano para filtrar', _in='query', type='int')
    @date_status_ns.response(200, 'Estatísticas de status de datas', date_status_statistics_model)
    def get(self, current_user_id):
        """Retorna estatísticas dos status de datas"""
        try:
            year = request.args.get('year', type=int)
            stats = DateStatus.get_date_status_statistics(year)

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


@date_status_ns.route('/status/<int:status_num>')
class DateStatusByStatus(Resource):
    """Endpoints para buscar por status específico"""

    @token_required
    @date_status_ns.doc('get_dates_by_status')
    @date_status_ns.response(200, 'Datas com o status especificado', [date_status_model])
    def get(self, current_user_id, status_num):
        """Retorna todas as datas com um status específico"""
        try:
            if status_num not in [1, 2, 3, 4, 5, 6]:
                return make_response(jsonify({
                    'success': False,
                    'message': 'Status deve estar entre 1 e 6'
                }), 400)

            statuses = DateStatus.select_date_statuses_by_status(status_num)
            response = [format_date_status_response(status) for status in statuses]

            return make_response(jsonify({
                'success': True,
                'status': status_num,
                'statuses': response,
                'total': len(response)
            }), 200)

        except Exception as e:
            return make_response(jsonify({
                'success': False,
                'message': 'Erro ao buscar status',
                'error': str(e)
            }), 500)


def confirm_year_deletion(year):
    confirmation = request.args.get('confirm', type=str)
    return confirmation == 'true'
