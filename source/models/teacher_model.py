from utils.mysqlUtils import send_sql_command,connect_to_db

class Teacher:
    def __init__(self, id, name, observation, image, user_id):
        self.id = id
        self.name = name
        self.observation = observation
        self.image = image
        self.user_id = user_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'observation': self.observation,
            'image': self.image,
            'user_id': self.user_id
        }

