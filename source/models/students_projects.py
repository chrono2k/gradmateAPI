from utils.mysqlUtils import send_sql_command,connect_to_db


class StudentsProjects:
    def __init__(self, id, students_id, project_id):
        self.id = id
        self.students_id = students_id
        self.project_id = project_id

    def to_dict(self):
        return {
            'id': self.id,
            'students_id': self.students_id,
            'project_id': self.project_id
        }

