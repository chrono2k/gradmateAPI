from utils.mysqlUtils import execute_migration

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    course_id INT,
    observation TEXT NULL,
    status ENUM('Pré-projeto', 'Qualificação','Defesa','Finalizado','Trancado') DEFAULT 'Pré-projeto',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nome (name),
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

INSERT_VALUE_TABLE_QUERY = """
INSERT INTO projects (id, name, description) VALUES
(1,'Projeto 1','Projeto 1'),
(2,'Projeto 2','Projeto 2'),
(3,'Projeto 3','Projeto 3'),
(4,'Projeto 4','Projeto 4');
"""


def run_migration():
    print("executando migration")
    execute_migration(CREATE_TABLE_QUERY)
    execute_migration(INSERT_VALUE_TABLE_QUERY)

if __name__ == "__main__":
    run_migration()