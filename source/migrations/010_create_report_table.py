from utils.mysqlUtils import execute_migration

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description TEXT NULL,
    pendency TEXT NULL,
    status ENUM('pendente', 'concluido') DEFAULT 'pendente',
    next_steps TEXT NULL,
    local TEXT NULL,
    feedback TEXT NULL,
    teacher_id INT,
    project_id INT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


def run_migration():
    print("executando migration")
    execute_migration(CREATE_TABLE_QUERY)


if __name__ == "__main__":
    run_migration()
