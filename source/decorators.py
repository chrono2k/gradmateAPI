from functools import wraps
from flask import request, jsonify, make_response
from utils.config import Config
from utils.jwt_utils import decode_jwt


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('authorization')
        print("x" * 60)
        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 403)
        try:
            data = decode_jwt(token, Config.JWT_SECRET_KEY)
            current_user_id = data['id']
            print(f"Payload decodificado: {data}")
        except Exception as e:
            return make_response(jsonify({'message': 'Token is invalid!', 'error': str(e)}), 403)
        print(current_user_id)
        return f(*args, current_user_id=current_user_id, **kwargs)

    return decorated
