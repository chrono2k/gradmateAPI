from utils.mysqlUtils import execute_migration

ALTER_TABLE_ADD_ROLE = """
ALTER TABLE teacher_project 
ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'advisor';
"""

CREATE_INDEX_ROLE = """
CREATE INDEX idx_teacher_project_role ON teacher_project(role);
"""

BACKFILL_ROLE = """
UPDATE teacher_project SET role = 'advisor' WHERE role IS NULL OR role = '';
"""


def run_migration():
    try:
        execute_migration(ALTER_TABLE_ADD_ROLE)
    except Exception as e:
        # Column may already exist; proceed to create index/backfill
        print(f"ALTER role column skipped/failed: {e}")
    try:
        execute_migration(BACKFILL_ROLE)
    except Exception as e:
        print(f"Backfill skipped/failed: {e}")
    try:
        execute_migration(CREATE_INDEX_ROLE)
    except Exception as e:
        print(f"Create index skipped/failed: {e}")


if __name__ == "__main__":
    run_migration()