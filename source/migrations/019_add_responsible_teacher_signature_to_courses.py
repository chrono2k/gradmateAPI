from utils.mysqlUtils import execute_migration

ADD_RESPONSIBLE_TEACHER = """
ALTER TABLE course
ADD COLUMN responsible_teacher_name VARCHAR(255) NULL 
AFTER observation;
"""

ADD_SIGNATURE_URL = """
ALTER TABLE course
ADD COLUMN responsible_signature_url VARCHAR(500) NULL 
AFTER responsible_teacher_name;
"""

ADD_INDEX = """
CREATE INDEX idx_responsible_teacher ON course(responsible_teacher_name);
"""


def run_migration():
    execute_migration(ADD_RESPONSIBLE_TEACHER)
    execute_migration(ADD_SIGNATURE_URL)
    execute_migration(ADD_INDEX)


if __name__ == "__main__":
    run_migration()
