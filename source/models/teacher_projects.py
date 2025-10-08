from utils.mysqlUtils import send_sql_command,connect_to_db


class TeacherProjects:
    def __init__(self, id, teacher_id, project_id):
        self.id = id
        self.teacher_id = teacher_id
        self.project_id = project_id

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'project_id': self.project_id
        }

