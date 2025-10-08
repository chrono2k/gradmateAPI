from utils.mysqlUtils import send_sql_command,connect_to_db


class StudentsCourse:
    def __init__(self, id, students_id, course_id):
        self.id = id
        self.students_id = students_id
        self.course_id = course_id

    def to_dict(self):
        return {
            'id': self.id,
            'students_id': self.students_id,
            'course_id': self.course_id
        }

