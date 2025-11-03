"""
Helper functions for course signature file management
"""
from werkzeug.utils import secure_filename
import os
import uuid
from utils.config import Config
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


def allowed_signature_file(filename):
    """
    Verifica se a extensão do arquivo é permitida

    Args:
        filename (str): Nome do arquivo

    Returns:
        bool: True se permitido
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_signatures_upload_dir():
    """
    Retorna o diretório de upload de assinaturas

    Returns:
        str: Caminho absoluto do diretório
    """
    base = Config.UPLOAD_FOLDER if hasattr(Config, 'UPLOAD_FOLDER') else 'uploads'
    # Resolve repo root: <repo>/source/utils -> go up two levels
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(utils_dir, '..', '..'))
    path = os.path.join(repo_root, base, 'signatures')
    os.makedirs(path, exist_ok=True)
    return path


def save_signature_file(file, course_id):
    """
    Salva arquivo de assinatura com validações

    Args:
        file: FileStorage object do Flask
        course_id (int): ID do curso

    Returns:
        str: URL relativa do arquivo salvo

    Raises:
        ValueError: Se arquivo inválido ou muito grande
    """
    if not file or not file.filename:
        raise ValueError("Arquivo inválido")

    if not allowed_signature_file(file.filename):
        raise ValueError("Tipo de arquivo não permitido. Use PNG, JPG ou JPEG")

    # Verificar tamanho
    file.seek(0, os.SEEK_END)
    size = file.tell()
    if size > MAX_FILE_SIZE:
        raise ValueError(f"Arquivo muito grande (máx {MAX_FILE_SIZE / (1024*1024)}MB)")
    file.seek(0)

    # Gerar nome único
    ext = file.filename.rsplit('.', 1)[1].lower()
    timestamp = int(datetime.now().timestamp())
    unique_id = uuid.uuid4().hex[:8]
    filename = f"course_{course_id}_signature_{timestamp}_{unique_id}.{ext}"

    # Salvar arquivo
    upload_dir = get_signatures_upload_dir()
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Retornar apenas o nome do arquivo (frontend concatena com /course/signature/)
    return filename


def delete_signature_file(signature_url):
    """
    Remove arquivo de assinatura do disco

    Args:
        signature_url (str): URL relativa do arquivo

    Returns:
        bool: True se removido com sucesso
    """
    if not signature_url:
        return False

    try:
        upload_dir = get_signatures_upload_dir()
        # Extrair apenas o nome do arquivo da URL
        filename = signature_url.split('/')[-1]
        filepath = os.path.join(upload_dir, filename)

        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Erro ao deletar assinatura: {e}")
        return False
