from utils.mysqlUtils import execute_migration

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    registration TEXT NULL,
    observation TEXT NULL,
    image TEXT NULL,
    user_id INT,
    status ENUM('formado', 'cursando') DEFAULT 'cursando',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nome (name),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

INSERT_VALUE_TABLE_QUERY = """
INSERT INTO students (id, name,registration, observation, status) VALUES
(1,'fulano',"40028922", '', 'ativo'),
(2,'ciclano',"40028922", '',  'ativo'),
(3,'beltrano',"40028922", '', 'ativo'),
(4,'deltrano',"40028922", '', 'ativo')
"""


def run_migration():
    print("executando migration")
    execute_migration(CREATE_TABLE_QUERY)
    execute_migration(INSERT_VALUE_TABLE_QUERY)

if __name__ == "__main__":
    run_migration()