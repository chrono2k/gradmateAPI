from utils.mysqlUtils import send_sql_command, connect_to_db
from werkzeug.security import generate_password_hash

class Report:
    @staticmethod
    def find_all_by_project(project_id):
        """
         Busca todos os relatórios que estão em um determinado projeto

        Args:
            project_id (int): ID do projeto

         Returns:
             list: Lista de tuplas com os dados dos relatórios
         """
        query = """
            SELECT r.* 
            FROM report r
            WHERE r.project_id = %s
        """
        return send_sql_command(query, (project_id,))

