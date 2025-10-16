from utils.mysqlUtils import execute_migration

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS date_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    status TINYINT NOT NULL CHECK (status IN (1, 2, 3, 4 ,5, 6 )),
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
('2025-10-30', 1),
('2025-10-31', 1),
('2025-11-3', 2),
('2025-11-4', 2),
('2025-11-5', 2),
('2025-11-6', 2),
('2025-11-7', 2),
('2025-11-10', 3),
('2025-11-11', 3),
('2025-11-12', 3),
('2025-11-13', 3),
('2025-11-17', 4),
('2025-11-18', 4),
('2025-11-19', 4),
('2025-11-20', 4),
('2025-11-24', 5),
('2025-11-25', 5),
('2025-11-26', 5),
('2025-11-27', 5),
('2025-11-28', 5),
('2025-12-10', 6),
('2025-12-11', 6),
('2025-12-12', 6)
ON DUPLICATE KEY UPDATE status = VALUES(status);
"""

def run_migration():
    print("executando migration")
    execute_migration(CREATE_TABLE_QUERY)
    execute_migration(INSERT_VALUE_TABLE_QUERY)


if __name__ == "__main__":
    run_migration()
