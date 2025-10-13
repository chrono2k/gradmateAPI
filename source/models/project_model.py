from utils.mysqlUtils import send_sql_command, connect_to_db


class Project:
    def __init__(self, id, name, description, course_id, observation, status):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.course_id = course_id
        self.observation = observation

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }

    @staticmethod
    def select_all_projects(status='Pré-projeto'):
        """
        Busca todos os projetos

        Args:
            status (str): Status dos projetos a buscar ('Pré-projeto','Qualificação','Defesa','Finalizado','Trancado','all')

        Returns:
            list: Lista de tuplas com os dados dos projetos
        """
        if status == 'all':
            query = """
                SELECT id, name, description, course_id, observation, status, created_at, updated_at
                FROM projects 
                ORDER BY name ASC
            """
            return send_sql_command(query)
        else:
            query = """
                SELECT id, name, description, course_id, observation, status, created_at, updated_at 
                FROM projects 
                WHERE status = %s
                ORDER BY name ASC
            """
            return send_sql_command(query, (status,))
