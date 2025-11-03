from utils.mysqlUtils import send_sql_command
from datetime import datetime

"""
Model de Curso
Responsável pelas operações de banco de dados relacionadas aos cursos
"""


class Course:
    """Classe para gerenciar operações de cursos no banco de dados"""

    def __init__(self, id, name, observation, status, created_at):
        self.id = id
        self.name = name
        self.observation = observation
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'observation': self.observation,
            'status': self.status,
            'created_at': self.created_at
        }

    @staticmethod
    def select_all_courses(status='ativo'):
        """
        Busca todos os cursos

        Args:
            status (str): Status dos cursos a buscar ('ativo', 'inativo', 'all')

        Returns:
            list: Lista de tuplas com os dados dos cursos
        """
        if status == 'all':
            query = """
                SELECT id, name, observation, status, created_at, updated_at, 
                       responsible_teacher_name, responsible_signature_url
                FROM course 
                ORDER BY name ASC
            """
            return send_sql_command(query)
        else:
            query = """
                SELECT id, name, observation, status, created_at, updated_at,
                       responsible_teacher_name, responsible_signature_url
                FROM course 
                WHERE status = %s
                ORDER BY name ASC
            """
            return send_sql_command(query, (status,))

    @staticmethod
    def select_course_by_id(course_id):
        """
        Busca um curso específico por ID

        Args:
            course_id (int): ID do curso

        Returns:
            tuple: Dados do curso ou None se não encontrado
        """
        query = """
            SELECT id, name, observation, status, created_at, updated_at,
                   responsible_teacher_name, responsible_signature_url
            FROM course 
            WHERE id = %s
        """
        result = send_sql_command(query, (course_id,))
        return result[0] if result != 0 else None

    @staticmethod
    def select_courses_by_name(name):
        """
        Busca cursos por nome (busca parcial)

        Args:
            name (str): Nome ou parte do nome do curso

        Returns:
            list: Lista de cursos encontrados
        """
        query = """
            SELECT id, name, observation, status, created_at, updated_at 
            FROM course 
            WHERE name LIKE %s AND status = 'ativo'
            ORDER BY name ASC
        """
        search_term = f"%{name}%"
        return send_sql_command(query, (search_term,))

    @staticmethod
    def select_courses_by_date_range(start_date=None, end_date=None, status='ativo'):
        """
        Busca cursos por intervalo de datas de cadastro

        Args:
            start_date (str): Data inicial (formato: YYYY-MM-DD)
            end_date (str): Data final (formato: YYYY-MM-DD)
            status (str): Status dos cursos

        Returns:
            list: Lista de cursos no intervalo de datas
        """
        if start_date and end_date:
            query = """
                SELECT id, name, observation, status, created_at, updated_at 
                FROM course 
                WHERE DATE(created_at) BETWEEN %s AND %s
                AND status = %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (start_date, end_date, status))
        elif start_date:
            query = """
                SELECT id, name, observation, status, created_at, updated_at 
                FROM course 
                WHERE DATE(created_at) >= %s
                AND status = %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (start_date, status))
        elif end_date:
            query = """
                SELECT id, name, observation, status, created_at, updated_at 
                FROM course 
                WHERE DATE(created_at) <= %s
                AND status = %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (end_date, status))
        else:
            return Course.select_all_courses(status)

    @staticmethod
    def insert_course(name, observation=None, responsible_teacher_name=None, responsible_signature_url=None):
        """
        Insere um novo curso

        Args:
            name (str): Nome do curso
            observation (str, optional): Observação sobre o curso
            responsible_teacher_name (str, optional): Nome do professor responsável
            responsible_signature_url (str, optional): URL da assinatura

        Returns:
            int: ID do curso inserido ou None em caso de erro
        """
        query = """
            INSERT INTO course (name, observation, status, responsible_teacher_name, responsible_signature_url) 
            VALUES (%s, %s, 'ativo', %s, %s)
        """
        result = send_sql_command(query, (name, observation, responsible_teacher_name, responsible_signature_url))
        # print("-" * 10)
        # print(result)
        return result if result != 0 else None

    @staticmethod
    def update_course(course_id, name=None, observation=None, responsible_teacher_name=None, responsible_signature_url=None):
        """
        Atualiza os dados de um curso

        Args:
            course_id (int): ID do curso
            name (str, optional): Novo nome do curso
            observation (str, optional): Observação sobre o curso
            responsible_teacher_name (str, optional): Nome do professor responsável
            responsible_signature_url (str, optional): URL da assinatura

        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)

        if observation is not None:
            updates.append("observation = %s")
            params.append(observation)

        if responsible_teacher_name is not None:
            updates.append("responsible_teacher_name = %s")
            params.append(responsible_teacher_name)

        if responsible_signature_url is not None:
            updates.append("responsible_signature_url = %s")
            params.append(responsible_signature_url)

        if not updates:
            return False

        params.append(course_id)
        query = f"""
            UPDATE course 
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """

        send_sql_command(query, tuple(params))
        return True

    @staticmethod
    def update_course_status(course_id, status):
        """
        Atualiza o status de um curso

        Args:
            course_id (int): ID do curso
            status (str): Novo status ('ativo' ou 'inativo')

        Returns:
            bool: True se atualizado com sucesso
        """
        query = """
            UPDATE course 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        send_sql_command(query, (status, course_id))
        return True

    @staticmethod
    def delete_course(course_id):
        """
        Exclusão lógica - marca o curso como inativo

        Args:
            course_id (int): ID do curso

        Returns:
            bool: True se desativado com sucesso
        """
        return Course.update_course_status(course_id, 'inativo')

    @staticmethod
    def activate_course(course_id):
        """
        Ativação lógica - marca o curso como ativo

        Args:
            course_id (int): ID do curso

        Returns:
            bool: True se ativado com sucesso
        """
        return Course.update_course_status(course_id, 'ativo')



    @staticmethod
    def permanent_delete_course(course_id):
        """
        Exclusão física - remove o curso do banco de dados
        CUIDADO: Esta operação não pode ser desfeita!

        Args:
            course_id (int): ID do curso

        Returns:
            bool: True se removido com sucesso
        """
        query = "DELETE FROM course WHERE id = %s"
        result = send_sql_command(query, (course_id,))
        return result != 0

    @staticmethod
    def check_course_exists(course_id):
        """
        Verifica se um curso existe

        Args:
            course_id (int): ID do curso

        Returns:
            bool: True se o curso existe
        """
        query = "SELECT id FROM course WHERE id = %s"
        result = send_sql_command(query, (course_id,))
        return result != 0

    @staticmethod
    def check_course_name_exists(name, exclude_id=None):
        """
        Verifica se já existe um curso com o nome informado

        Args:
            name (str): Nome do curso
            exclude_id (int, optional): ID do curso a ser excluído da busca

        Returns:
            bool: True se já existe um curso com este nome
        """
        if exclude_id:
            query = """SELECT id FROM course WHERE name = %s AND id != %s"""
            result = send_sql_command(query, (name, exclude_id))
        else:
            query = """SELECT id FROM course WHERE name = %s"""
            result = send_sql_command(query, (name,))

        return result != 0

    @staticmethod
    def count_courses(status='ativo'):
        """
        Conta o total de cursos

        Args:
            status (str): Status dos cursos a contar

        Returns:
            int: Total de cursos
        """
        if status == 'all':
            query = "SELECT COUNT(*) FROM course"
            result = send_sql_command(query)
        else:
            query = "SELECT COUNT(*) FROM course WHERE status = %s"
            result = send_sql_command(query, (status,))

        return result[0][0] if result != 0 else 0

    @staticmethod
    def get_course_statistics():
        """
        Retorna estatísticas dos cursos

        Returns:
            dict: Dicionário com estatísticas
        """
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'ativo' THEN 1 ELSE 0 END) as ativos,
                SUM(CASE WHEN status = 'inativo' THEN 1 ELSE 0 END) as inativos,
                MAX(created_at) as ultimo_cadastro
            FROM course
        """
        result = send_sql_command(query)

        if result != 0:
            row = result[0]
            return {
                'total': row[0],
                'ativos': row[1],
                'inativos': row[2],
                'ultimo_cadastro': row[3]
            }
        return {
            'total': 0,
            'ativos': 0,
            'inativos': 0,
            'ultimo_cadastro': None
        }
