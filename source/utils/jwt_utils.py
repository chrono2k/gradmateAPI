import base64
import hmac
import hashlib
import json
from datetime import datetime, timedelta

def encode_jwt(payload, secret, algorithm='HS256'):
    header = {
        "alg": algorithm,
        "typ": "JWT"
    }
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()

    signature = hmac.new(secret.encode(), f'{header_b64}.{payload_b64}'.encode(), hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()

    return f'{header_b64}.{payload_b64}.{signature_b64}'

def decode_jwt(token, secret, algorithms=['HS256']):
    header_b64, payload_b64, signature_b64 = token.split('.')
    expected_signature = hmac.new(secret.encode(), f'{header_b64}.{payload_b64}'.encode(), hashlib.sha256).digest()
    expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).rstrip(b'=').decode()

    if not hmac.compare_digest(expected_signature_b64, signature_b64):
        raise ValueError("Token signature is invalid!")

    payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '=='))
    return payload