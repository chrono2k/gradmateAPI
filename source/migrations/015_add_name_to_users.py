from utils.mysqlUtils import execute_migration

def run_migration():
    """Adiciona coluna 'name' na tabela users"""
    
    sql = """
    ALTER TABLE users 
    ADD COLUMN name VARCHAR(255) NULL AFTER username;
    """
    
    execute_migration(sql)
    print("Coluna 'name' adicionada à tabela users com sucesso!")
