from utils.mysqlUtils import execute_migration

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS student_project (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    project_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

INSERT_VALUE_TABLE_QUERY = """
INSERT INTO student_project (id, student_id, project_id) VALUES
(1,1,1),
(2,2,2),
(3,3,2),
(4,4,3);
"""


def run_migration():
    print("executando migration")
    execute_migration(CREATE_TABLE_QUERY)
    execute_migration(INSERT_VALUE_TABLE_QUERY)

if __name__ == "__main__":
    run_migration()