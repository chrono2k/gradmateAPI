from utils.mysqlUtils import execute_migration


CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS course (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    observation TEXT NULL,
    status ENUM('ativo', 'inativo') DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nome (name),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

INSERT_VALUE_TABLE_QUERY = """
INSERT INTO course (id, name, observation, status) VALUES
(1,'Análise e Desenvolvimento de Sistemas', 'Curso focado em desenvolvimento de software e análise de requisitos', 'ativo'),
(2,'Gestão da Tecnologia da Informação', 'Formação de profissionais para gerenciar equipes e projetos de TI',  'ativo'),
(3,'Redes de Computadores', 'Especialização em infraestrutura e segurança de redes', 'ativo'),
(4,'Ciência da Computação', 'Formação ampla em computação, algoritmos e programação', 'ativo'),
(5,'Segurança da Informação', 'Curso especializado em cybersecurity e proteção de dados', 'ativo');
"""


def run_migration():
    print("executando migration")
    execute_migration(CREATE_TABLE_QUERY)
    execute_migration(INSERT_VALUE_TABLE_QUERY)

if __name__ == "__main__":
    run_migration()