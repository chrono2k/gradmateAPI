import datetime
import os
from flask import request, jsonify, make_response
from flask_restx import Resource, Namespace, fields
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import User
from utils.jwt_utils import encode_jwt
from utils.config import Config
from time import strftime, localtime

auth_ns = Namespace('auth',description='Autenticação de usuário')

login_model = auth_ns.model('LoginInput', {
    'username': fields.String(required=True, description='Nome de usuário'),
    'password': fields.String(required=True, description='Senha'),
    'epoch': fields.Integer(required=True, description='Timestamp para sincronizar o relógio interno')
})

token_model = auth_ns.model('LoginOutput', {
    'token': fields.String(description='JWT gerado após login bem-sucedido')
})

@auth_ns.route('/login/')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login realizado com sucesso', token_model)
    @auth_ns.response(401, 'Credenciais inválidas')
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.find_by_username(username)
        print(generate_password_hash("teste"))
        if user and check_password_hash(user.password_hash, password) and user.active:
            token = encode_jwt({
                'username': user.username,
                'id': user.id,
                'exp': (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp()
            }, Config.JWT_SECRET_KEY)

            return jsonify({'token': token})

        else:
            return make_response(jsonify({"message": "Invalid credentials"}), 401)