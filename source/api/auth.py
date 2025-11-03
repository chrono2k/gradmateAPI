import datetime
import os
from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace, fields
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import User
from utils.jwt_utils import encode_jwt
from utils.config import Config
from time import strftime, localtime
from decorators import token_required
from utils.request_utils import get_json_data

auth_ns = Namespace('auth', description='Autenticação de usuário')

login_model = auth_ns.model('LoginInput', {
    'username': fields.String(required=True, description='Nome de usuário'),
    'password': fields.String(required=True, description='Senha'),
})

token_model = auth_ns.model('LoginOutput', {
    'token': fields.String(description='JWT gerado após login bem-sucedido')
})

user_out_model = auth_ns.model('User', {
    'id': fields.Integer,
    'username': fields.String,
    'authority': fields.String(enum=['admin', 'teacher', 'student']),
    'status': fields.String(enum=['ativo', 'inativo']),
    'name': fields.String
})

user_create_model = auth_ns.model('UserCreate', {
    'username': fields.String(required=True, description='Login do usuário (email)'),
    'password': fields.String(required=True, description='Senha inicial'),
    'authority': fields.String(required=True, description='Papel do usuário', enum=['admin', 'teacher', 'student']),
    'name': fields.String(required=False, description='Nome completo do usuário')
})

user_update_role_model = auth_ns.model('UserUpdateRole', {
    'authority': fields.String(required=True, enum=['admin', 'teacher', 'student'])
})

user_update_status_model = auth_ns.model('UserUpdateStatus', {
    'status': fields.String(required=True, enum=['ativo', 'inativo'])
})

user_reset_password_model = auth_ns.model('UserResetPassword', {
    'password': fields.String(required=True, description='Nova senha')
})


@auth_ns.route('/login/')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login realizado com sucesso', token_model)
    @auth_ns.response(401, 'Credenciais inválidas')
    def post(self):
        """Autentica usuário e retorna JWT"""
        data = get_json_data()
        username = data.get('username')
        password = data.get('password')
        user = User.find_by_username(username)
        print(generate_password_hash("teste"))
        if user and check_password_hash(user.password_hash, password) and user.status == 'ativo':
            token = encode_jwt({
                'username': user.username,
                'id': user.id,
                'exp': (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp()
            }, Config.JWT_SECRET_KEY)

            return jsonify({'token': token})

        else:
            return make_response(jsonify({"message": "Invalid credentials"}), 401)


def require_admin(user_id):
    """Helper para garantir que o usuário é admin"""
    user = User.find_by_id(user_id)
    if not user or user.authority != 'admin':
        return False
    return True


@auth_ns.route('/users')
class AdminUsers(Resource):
    """Admin: listar e criar usuários"""

    @token_required
    def get(self, current_user_id):
        """Lista todos os usuários"""
        if not require_admin(current_user_id):
            return make_response(jsonify({'success': False, 'message': 'Não autorizado'}), 403)
        users = User.get_all()
        return make_response(jsonify({'success': True, 'users': users, 'total': len(users)}), 200)

    @token_required
    @auth_ns.expect(user_create_model)
    def post(self, current_user_id):
        """Cria novo usuário"""
        if not require_admin(current_user_id):
            return make_response(jsonify({'success': False, 'message': 'Não autorizado'}), 403)
        data = get_json_data()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        authority = data.get('authority', 'student')
        name = data.get('name', '').strip() or None
        if not username or not password:
            return make_response(jsonify({'success': False, 'message': 'username e password são obrigatórios'}), 400)
        if User.username_exists(username):
            return make_response(jsonify({'success': False, 'message': 'Username já existe'}), 409)
        user_id = User.create_user(username, generate_password_hash(password), authority, name)
        return make_response(jsonify({'success': True, 'user_id': user_id}), 201)


@auth_ns.route('/users/<int:user_id>')
class AdminUserDetail(Resource):
    """Admin: atualizar role e status, resetar senha"""

    @token_required
    @auth_ns.expect(user_update_role_model)
    def put(self, current_user_id, user_id):
        """Atualiza usuário"""
        if not require_admin(current_user_id):
            return make_response(jsonify({'success': False, 'message': 'Não autorizado'}), 403)
        data = get_json_data()
        authority = data.get('authority')
        if authority not in ['admin', 'teacher', 'student']:
            return make_response(jsonify({'success': False, 'message': 'authority inválida'}), 400)
        if not User.find_by_id(user_id):
            return make_response(jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404)
        User.update_authority(user_id, authority)
        return make_response(jsonify({'success': True, 'message': 'Perfil atualizado'}), 200)

    @token_required
    @auth_ns.expect(user_update_status_model)
    def patch(self, current_user_id, user_id):
        """Altera status (ativo/inativo)"""
        if not require_admin(current_user_id):
            return make_response(jsonify({'success': False, 'message': 'Não autorizado'}), 403)
        data = get_json_data()
        status = data.get('status')
        if status not in ['ativo', 'inativo']:
            return make_response(jsonify({'success': False, 'message': 'status inválido'}), 400)
        if not User.find_by_id(user_id):
            return make_response(jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404)
        User.set_status(user_id, status)
        return make_response(jsonify({'success': True, 'message': 'Status atualizado'}), 200)


@auth_ns.route('/user')
class CurrentUser(Resource):
    @token_required
    def get(self, current_user_id):
        """Dados do usuário autenticado"""
        user = User.find_by_id(current_user_id)
        if not user:
            return make_response(jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404)
        return make_response(jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'authority': user.authority,
                'status': user.status,
                'name': user.name
            }
        }), 200)


@auth_ns.route('/users/<int:user_id>/password')
class AdminUserPassword(Resource):
    @token_required
    @auth_ns.expect(user_reset_password_model)
    def post(self, current_user_id, user_id):
        """Reset de senha"""
        if not require_admin(current_user_id):
            return make_response(jsonify({'success': False, 'message': 'Não autorizado'}), 403)
        data = get_json_data()
        password = data.get('password')
        if not password:
            return make_response(jsonify({'success': False, 'message': 'password é obrigatório'}), 400)
        if not User.find_by_id(user_id):
            return make_response(jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404)
        User.update_password(user_id, generate_password_hash(password))
        return make_response(jsonify({'success': True, 'message': 'Senha redefinida'}), 200)
