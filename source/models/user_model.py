from utils.mysqlUtils import send_sql_command,connect_to_db


class User:
    def __init__(self, id, username, authority, password_hash, status, name=None):
        self.id = id
        self.username = username
        self.authority = authority
        self.password_hash = password_hash
        self.status = status
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'authority': self.authority,
            'status': self.status,
            'name': self.name
        }


    @staticmethod
    def find_by_username(username):
        result = send_sql_command("SELECT id, username, authority, password_hash, status, name FROM users WHERE username = %s", (username,))
        if result in (0, "0"):
            return None
        row = result[0] if result else None
        if row:
            return User(row[0], row[1], row[2], row[3], row[4], row[5] if len(row) > 5 else None)
        return None

    @staticmethod
    def delete_user(user_id,active):
        send_sql_command("UPDATE users set active =%s where id =%s",(active,user_id))

    @staticmethod
    def find_by_id(user_id):
        result = send_sql_command("SELECT id, username, authority, password_hash, status, name FROM users WHERE id = %s", (user_id,))
        if result in (0, "0"):
            return None
        row = result[0] if result else None
        if row:
            return User(row[0], row[1], row[2], row[3], row[4], row[5] if len(row) > 5 else None)
        return None

    @staticmethod
    def select_user_by_id(user_id):
        """
        Busca um professor específico por ID

        Args:
            user_id (int): ID do professor

        Returns:
            tuple: Dados do professor ou None se não encontrado
        """
        query = """
            SELECT id, username, authority, password_hash, status, name FROM users WHERE id = %s
        """
        result = send_sql_command(query, (user_id,))
        if result in (0, "0"):
            return None
        row = result[0] if result else None
        if row:
            return User(row[0], row[1], row[2], row[3], row[4], row[5] if len(row) > 5 else None)
        return None



    @staticmethod
    def get_all():
        connection,cursor = connect_to_db()
        query = "SELECT * FROM users"
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        result = [
            dict(zip(columns, row)) for row in cursor.fetchall()
        ]
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def create_user(username, password_hash, authority="user", name=None):
        return send_sql_command(
            "INSERT INTO users (username, password_hash, authority, name) VALUES (%s, %s, %s, %s)",
            (username, password_hash, authority, name)
        )

    @staticmethod
    def update_password(id, password_hash):
        send_sql_command("UPDATE users set password_hash =%s where id =%s", (password_hash,id))

    @staticmethod
    def update_authority(id,authority):
        send_sql_command("UPDATE users set authority =%s where id =%s", (authority,id))

    @staticmethod
    def username_exists(username):
        result = send_sql_command("SELECT id FROM users WHERE username = %s", (username,))
        if result in (0, "0"):
            return False
        return bool(result)

    @staticmethod
    def set_status(id, status):
        # status must be 'ativo' or 'inativo'
        send_sql_command("UPDATE users SET status = %s WHERE id = %s", (status, id))

