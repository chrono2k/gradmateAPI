from utils.mysqlUtils import execute_migration

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS date_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    status TINYINT NOT NULL CHECK (status IN (1, 2, 3)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,    
    INDEX idx_date (date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

INSERT_VALUE_TABLE_QUERY = """
INSERT INTO date_status (date, status) VALUES
('2025-01-15', 1),
('2025-01-20', 2),
('2025-02-10', 3),
('2025-03-05', 1),
('2025-03-15', 2),
('2025-04-30', 3),
('2025-05-12', 1)
ON DUPLICATE KEY UPDATE status = VALUES(status);
"""

def run_migration():
    print("executando migration")
    execute_migration(CREATE_TABLE_QUERY)
    execute_migration(INSERT_VALUE_TABLE_QUERY)


if __name__ == "__main__":
    run_migration()
