from flask import request
import json


def get_json_data():
    """
    Helper para pegar JSON do request de forma segura
    Trata caso onde request.get_json() retorna string ao invés de dict
    """
    data = request.get_json() or {}
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return {}
    return data if isinstance(data, dict) else {}
