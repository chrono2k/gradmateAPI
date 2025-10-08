from utils.mysqlUtils import send_sql_command,connect_to_db


class Course:
    def __init__(self, id, name, observation,status, created_at):
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

