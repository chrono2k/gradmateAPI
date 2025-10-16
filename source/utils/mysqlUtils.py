from MySQLdb import connections as sqlconnector
from utils.config import Config

def initialize_database():
    try:
        connection = sqlconnector.Connection(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        connection.commit()
        cursor.close()
        connection.close()
    except sqlconnector.Error as e:
        print(f"Erro ao criar banco de dados: {e}")
        raise

def connect_to_db() -> object:
    try:
        connection = sqlconnector.Connection(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        cursor = connection.cursor()
        return connection, cursor
    except sqlconnector.Error as e:
        print(f"Erro na conexão: {e}")
        raise


def execute_migration(table_query):
    print("-" * 60)
    connection, cursor = connect_to_db()
    try:
        cursor.execute(table_query)
        print("Migração executada com sucesso.")
    except Exception as e:
        print(f"Erro ao executar a migração: {e}")
    finally:
        connection.commit()
        cursor.close()
        connection.close()

def send_sql_command(sql_statement, args=None):
    connection = None
    cursor = None
    try:
        connection, cursor = connect_to_db()

        cursor.execute("SET SESSION query_cache_type = OFF")
        cursor.execute("SET SESSION tmp_table_size = 67108864")
        cursor.execute("SET SESSION max_heap_table_size = 67108864")

        cursor.execute(sql_statement, args)
        result = cursor.fetchall()
        last_id = int(cursor.lastrowid)
        return last_id if result == () else result

    except Exception as e:
        print(f"[ERROR] send_sql_command: {e}")
        return "0"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.commit()
            connection.close()
