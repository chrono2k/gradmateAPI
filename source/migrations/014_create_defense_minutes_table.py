from utils.mysqlUtils import execute_migration

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS defense_minutes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id INT NOT NULL,
  file_id INT NOT NULL,
  student_name VARCHAR(255) NOT NULL,
  title TEXT NOT NULL,
  result VARCHAR(20) NOT NULL,
  location VARCHAR(255) NULL,
  started_at TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by INT NULL,
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  FOREIGN KEY (file_id) REFERENCES project_files(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);
"""

CREATE_INDEX_QUERY = """
CREATE INDEX idx_defense_minutes_project ON defense_minutes(project_id);
"""

def run_migration():
    execute_migration(CREATE_TABLE_QUERY)
    execute_migration(CREATE_INDEX_QUERY)

if __name__ == "__main__":
    run_migration()
