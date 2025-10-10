from utils.mysqlUtils import execute_migration


CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS users (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(80) NOT NULL UNIQUE,
    authority ENUM('admin', 'teacher', 'students') DEFAULT 'students',
    `password_hash` VARCHAR(256) NOT NULL,
    status ENUM('ativo', 'inativo') DEFAULT 'ativo'

);
"""

INSERT_VALUE_TABLE_QUERY = """
INSERT INTO users (id, username,authority,password_hash,status) VALUES 
(1,'teste','admin', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo'),
(2,'professor_1','teacher', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo'),
(3,'professor_2','teacher', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo'),
(4,'professor_3','teacher', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo'),
(5,'professor_4','teacher', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo'),
(6,'aluno_1','students', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo'),
(7,'aluno_2','students', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo'),
(8,'aluno_3','students', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo'),
(9,'aluno_4','students', 'pbkdf2:sha256:150000$GUiqGKP4$dcf21e3db41e7fe0fe7cfae5b7e13d9f9f589587ef97a1ce4c2bff5c64100c81','ativo');
"""


def run_migration():
    print("executando migration")
    execute_migration(CREATE_TABLE_QUERY)
    execute_migration(INSERT_VALUE_TABLE_QUERY)

if __name__ == "__main__":
    run_migration()