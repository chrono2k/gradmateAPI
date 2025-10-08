from utils.mysqlUtils import send_sql_command,connect_to_db


class Projects:
    def __init__(self, id, name, description, status):
        self.id = id
        self.name = name
        self.description = description
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status':self.status
        }
