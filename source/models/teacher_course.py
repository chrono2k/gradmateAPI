from utils.mysqlUtils import send_sql_command,connect_to_db


class TeacherCourse:
    def __init__(self, id, teacher_id, course_id, description):
        self.id = id
        self.teacher_id = teacher_id
        self.course_id = course_id
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'course_id': self.course_id,
            'description': self.description
        }

