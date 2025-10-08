from utils.mysqlUtils import send_sql_command, connect_to_db

class Students:
    def __init__(self, id, name, registration, observation, image, user_id, status):
        self.id = id
        self.name = name
        self.registration = registration
        self.observation = observation
        self.image = image
        self.user_id = user_id
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'registration': self.registration,
            'observation': self.observation,
            'image': self.image,
            'user_id':self.user_id,
            'status':self.status
        }

