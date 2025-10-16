from utils.mysqlUtils import send_sql_command
from datetime import datetime


class DateStatus:
    """Classe para gerenciar operações de status de datas no banco de dados"""

    @staticmethod
    def select_all_date_statuses(year=None):
        """
        Busca todos os status de datas

        Args:
            year (int, optional): Ano específico para filtrar

        Returns:
            list: Lista de tuplas com os dados dos status de datas
        """
        if year:
            query = """
                SELECT id, date, status, created_at, updated_at
                FROM date_status
                WHERE YEAR(date) = %s
                ORDER BY date ASC
            """
            return send_sql_command(query, (year,))
        else:
            query = """
                SELECT id, date, status, created_at, updated_at
                FROM date_status
                ORDER BY date DESC
            """
            return send_sql_command(query)

    @staticmethod
    def select_date_status_by_id(status_id):
        """
        Busca um status de data específico por ID

        Args:
            status_id (int): ID do status de data

        Returns:
            tuple: Dados do status ou None se não encontrado
        """
        query = """
            SELECT id, date, status, created_at, updated_at
            FROM date_status
            WHERE id = %s
        """
        result = send_sql_command(query, (status_id,))
        return result[0] if result else None

    @staticmethod
    def select_date_status_by_date(date_str):
        """
        Busca um status de data específico por data

        Args:
            date_str (str): Data em formato YYYY-MM-DD

        Returns:
            tuple: Dados do status ou None se não encontrado
        """
        query = """
            SELECT id, date, status, created_at, updated_at
            FROM date_status
            WHERE date = %s
        """
        result = send_sql_command(query, (date_str,))
        return result[0] if result else None

    @staticmethod
    def select_date_statuses_by_status(status):
        """
        Busca todas as datas com um status específico

        Args:
            status (int): Status (entre 1 e 6)

        Returns:
            list: Lista de datas com o status
        """
        query = """
            SELECT id, date, status, created_at, updated_at
            FROM date_status
            WHERE status = %s
            ORDER BY date ASC
        """
        return send_sql_command(query, (status,))

    @staticmethod
    def select_date_statuses_by_date_range(start_date, end_date, status=None):
        """
        Busca status de datas em um intervalo

        Args:
            start_date (str): Data inicial (YYYY-MM-DD)
            end_date (str): Data final (YYYY-MM-DD)
            status (int, optional): Filtrar por status específico

        Returns:
            list: Lista de status de datas no intervalo
        """
        if status:
            query = """
                SELECT id, date, status, created_at, updated_at
                FROM date_status
                WHERE date BETWEEN %s AND %s AND status = %s
                ORDER BY date ASC
            """
            return send_sql_command(query, (start_date, end_date, status))
        else:
            query = """
                SELECT id, date, status, created_at, updated_at
                FROM date_status
                WHERE date BETWEEN %s AND %s
                ORDER BY date ASC
            """
            return send_sql_command(query, (start_date, end_date))

    @staticmethod
    def insert_date_status(date_str, status):
        """
        Insere um novo status de data

        Args:
            date_str (str): Data em formato YYYY-MM-DD
            status (int): Status (entre 1 e 6)

        Returns:
            int: ID do status inserido ou None em caso de erro
        """
        query = """
            INSERT INTO date_status (date, status)
            VALUES (%s, %s)
        """
        result = send_sql_command(query, (date_str, status))
        return result if result else None

    @staticmethod
    def update_date_status(status_id, status):
        """
        Atualiza o status de uma data

        Args:
            status_id (int): ID do status de data
            status (int): Novo status (entre 1 e 6)

        Returns:
            bool: True se atualizado com sucesso
        """
        query = """
            UPDATE date_status
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        result = send_sql_command(query, (status, status_id))
        return result is not None

    @staticmethod
    def update_date_status_by_date(date_str, status):
        """
        Atualiza ou cria o status de uma data

        Args:
            date_str (str): Data em formato YYYY-MM-DD
            status (int): Novo status (1, 2 ou 3)

        Returns:
            bool: True se atualizado/criado com sucesso
        """
        existing = DateStatus.select_date_status_by_date(date_str)

        if existing:
            # Atualizar
            query = """
                UPDATE date_status
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE date = %s
            """
            result = send_sql_command(query, (status, date_str))
        else:
            # Inserir
            query = """
                INSERT INTO date_status (date, status)
                VALUES (%s, %s)
            """
            result = send_sql_command(query, (date_str, status))

        return result is not None

    @staticmethod
    def delete_date_status(status_id):
        """
        Remove um status de data

        Args:
            status_id (int): ID do status de data

        Returns:
            bool: True se removido com sucesso
        """
        query = "DELETE FROM date_status WHERE id = %s"
        result = send_sql_command(query, (status_id,))
        return result is not None

    @staticmethod
    def delete_date_status_by_date(date_str):
        """
        Remove o status de uma data específica

        Args:
            date_str (str): Data em formato YYYY-MM-DD

        Returns:
            bool: True se removido com sucesso
        """
        query = "DELETE FROM date_status WHERE date = %s"
        result = send_sql_command(query, (date_str,))
        return result is not None

    @staticmethod
    def check_date_status_exists(date_str):
        """
        Verifica se uma data tem status cadastrado

        Args:
            date_str (str): Data em formato YYYY-MM-DD

        Returns:
            bool: True se existe status para essa data
        """
        query = "SELECT id FROM date_status WHERE date = %s"
        result = send_sql_command(query, (date_str,))
        return len(result) > 0

    @staticmethod
    def count_date_statuses(year=None, status=None):
        """
        Conta o total de status de datas

        Args:
            year (int, optional): Filtrar por ano
            status (int, optional): Filtrar por status específico

        Returns:
            int: Total de status
        """
        if year and status:
            query = """
                SELECT COUNT(*) FROM date_status
                WHERE YEAR(date) = %s AND status = %s
            """
            result = send_sql_command(query, (year, status))
        elif year:
            query = """
                SELECT COUNT(*) FROM date_status
                WHERE YEAR(date) = %s
            """
            result = send_sql_command(query, (year,))
        elif status:
            query = """
                SELECT COUNT(*) FROM date_status
                WHERE status = %s
            """
            result = send_sql_command(query, (status,))
        else:
            query = "SELECT COUNT(*) FROM date_status"
            result = send_sql_command(query)

        return result[0][0] if result else 0

    @staticmethod
    def get_date_status_statistics(year=None):
        """
        Retorna estatísticas dos status de datas

        Args:
            year (int, optional): Ano específico

        Returns:
            dict: Dicionário com estatísticas
        """
        if year:
            query = """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as status_1,
                    SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) as status_2,
                    SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as status_3,
                    SUM(CASE WHEN status = 4 THEN 1 ELSE 0 END) as status_4,
                    SUM(CASE WHEN status = 5 THEN 1 ELSE 0 END) as status_5,
                    SUM(CASE WHEN status = 6 THEN 1 ELSE 0 END) as status_6
                FROM date_status
                WHERE YEAR(date) = %s
            """
            result = send_sql_command(query, (year,))
        else:
            query = """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as status_1,
                    SUM(CASE WHEN status = 2 THEN 1 ELSE 0 END) as status_2,
                    SUM(CASE WHEN status = 3 THEN 1 ELSE 0 END) as status_3,
                    SUM(CASE WHEN status = 4 THEN 1 ELSE 0 END) as status_4,
                    SUM(CASE WHEN status = 5 THEN 1 ELSE 0 END) as status_5,
                    SUM(CASE WHEN status = 6 THEN 1 ELSE 0 END) as status_6
                FROM date_status
            """
            result = send_sql_command(query)

        if result:
            row = result[0]
            return {
                'total': row[0],
                'status_1': row[1] or 0,
                'status_2': row[2] or 0,
                'status_3': row[3] or 0,
                'status_4': row[4] or 0,
                'status_5': row[5] or 0,
                'status_6': row[6] or 0
            }
        return {
            'total': 0,
            'status_1': 0,
            'status_2': 0,
            'status_3': 0,
            'status_4': 0,
            'status_5': 0,
            'status_6': 0
        }

    @staticmethod
    def get_statuses_for_year(year):
        """
        Retorna todos os status de datas de um ano em formato dicionário

        Args:
            year (int): Ano desejado

        Returns:
            dict: Dicionário com formato {YYYY-MM-DD: status}
        """
        statuses = DateStatus.select_all_date_statuses(year)
        result = {}

        for status_data in statuses:
            date_str = status_data[1].isoformat() if hasattr(status_data[1], 'isoformat') else str(status_data[1])
            result[date_str] = status_data[2]

        return result

    @staticmethod
    def clear_year_statuses(year):
        """
        Remove todos os status de um ano específico

        Args:
            year (int): Ano

        Returns:
            bool: True se removido com sucesso
        """
        query = """
            DELETE FROM date_status
            WHERE YEAR(date) = %s
        """
        result = send_sql_command(query, (year,))
        return result is not None