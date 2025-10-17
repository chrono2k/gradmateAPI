from utils.mysqlUtils import execute_migration

def run_migration():
    """Altera coluna student_name da tabela defense_minutes para permitir NULL"""
    
    sql = """
    ALTER TABLE defense_minutes 
    MODIFY COLUMN student_name VARCHAR(255) NULL;
    """
    
    execute_migration(sql)
    print("Coluna 'student_name' da tabela defense_minutes alterada para permitir NULL com sucesso!")