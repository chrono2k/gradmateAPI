from utils.mysqlUtils import send_sql_command,connect_to_db
from werkzeug.security import generate_password_hash


class Teacher:
    @staticmethod
    def select_all_teacher():
        """
        Busca todos os professores

        Returns:
            list: Lista de tuplas com os dados dos professores
        """
        query = """
            SELECT id, name, observation, image, user_id, created_at, updated_at 
            FROM teachers 
            ORDER BY name ASC
        """
        return send_sql_command(query, ())

    @staticmethod
    def select_teacher_by_id(teacher_id):
        """
        Busca um professor específico por ID

        Args:
            teacher_id (int): ID do professor

        Returns:
            tuple: Dados do professor ou None se não encontrado
        """
        query = """
            SELECT id, name, observation, image, user_id, created_at, updated_at 
            FROM teachers 
            WHERE id = %s
        """
        result = send_sql_command(query, (teacher_id,))
        return result[0] if result != 0 else None

    @staticmethod
    def select_teacher_by_name(name):
        """
        Busca professor por nome (busca parcial)

        Args:
            name (str): Nome ou parte do nome do professor

        Returns:
            list: Lista de professores encontrados
        """
        query = """
            SELECT id, name, observation, image, user_id, created_at, updated_at 
            FROM teachers 
            WHERE name LIKE %s
            ORDER BY name ASC
        """
        search_term = f"%{name}%"
        return send_sql_command(query, (search_term,))

    @staticmethod
    def select_teacher_by_date_range(start_date=None, end_date=None):
        """
        Busca professores por intervalo de datas de cadastro

        Args:
            start_date (str): Data inicial (formato: YYYY-MM-DD)
            end_date (str): Data final (formato: YYYY-MM-DD)

        Returns:
            list: Lista de professores no intervalo de datas
        """
        if start_date and end_date:
            query = """
                SELECT id, name, observation, image, user_id, created_at, updated_at 
                FROM teachers 
                WHERE DATE(created_at) BETWEEN %s AND %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (start_date, end_date))
        elif start_date:
            query = """
                SELECT id, name, observation, image, user_id, created_at, updated_at
                FROM teachers 
                WHERE DATE(created_at) >= %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (start_date))
        elif end_date:
            query = """
                SELECT id, name, observation, image, user_id, created_at, updated_at
                FROM teachers 
                WHERE DATE(created_at) <= %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (end_date))
        else:
            return Teacher.select_all_teacher()

    @staticmethod
    def insert_teacher(name, email, observation=None, image=None):
        """
        Insere um novo usuário e professor

        Args:
            name (str): Nome do professor
            email (str): email do professor
            observation (str, optional): Observação sobre o professor
            image (str, optional): Imagem do professor
        Returns:
            int: ID do professor inserido ou None em caso de erro
        """
        query = """
        INSERT INTO users (username, authority, password_hash) 
        VALUES (%s, %s, %s)
        """
        user_id = send_sql_command(query, (email, 'teacher', generate_password_hash("fatec")))
        if user_id != 0:
            query = """
                INSERT INTO teachers (name, observation, image, user_id) 
                VALUES (%s, %s, %s, %s)
            """
            result = send_sql_command(query, (name, observation, image, user_id))
            return result if result != 0 else None
        return None

    @staticmethod
    def update_teacher_status(teacher_id, status):
        """
        Atualiza o status de um professor

        Args:
            teacher_id (int): ID do professor
            status (str): Novo status ('ativo' ou 'inativo')

        Returns:
            bool: True se atualizado com sucesso
        """
        teacher = Teacher.select_teacher_by_id(teacher_id)
        if teacher:
            query = """
                UPDATE users 
                SET status = %s
                WHERE id = %s
            """
            send_sql_command(query, (status, teacher[4]))
            return True
        return False

    @staticmethod
    def update_name(teacher_id, name):
        """
        Atualiza o nome de um professor

        Args:
            teacher_id (int): ID do professor
            name (str): Novo nome

        Returns:
            bool: True se atualizado com sucesso
        """
        query = """
            UPDATE teachers 
            SET name = %s
            WHERE id = %s
        """
        send_sql_command(query, (name, teacher_id))
        return True

    @staticmethod
    def update_email(teacher_id, email):
        """
        Atualiza o email de um professor

        Args:
            teacher_id (int): ID do professor
            email (str): Novo email

        Returns:
            bool: True se atualizado com sucesso
        """
        teacher = Teacher.select_teacher_by_id(teacher_id)
        if teacher:
            query = """
                UPDATE users 
                SET username = %s
                WHERE id = %s
            """
            send_sql_command(query, (email, teacher[4]))
            return True
        return False

    @staticmethod
    def update_observation_and_image(teacher_id, observation, image):
        """
        Atualiza o nome de um professor

        Args:
            teacher_id (int): ID do professor
            observation (str): Observação sobre o professor
            image (str): Imagem do professor

        Returns:
            bool: True se atualizado com sucesso
        """
        query = """
            UPDATE teachers 
            SET observation = %s , image = %s
            WHERE id = %s
        """
        send_sql_command(query, (observation, image, teacher_id))
        return True

    @staticmethod
    def delete_teacher(teacher_id):
        """
        Exclusão lógica - marca o usuario do professor como inativo

        Args:
            teacher_id (int): ID do professor

        Returns:
            bool: True se desativado com sucesso
        """
        return Teacher.update_teacher_status(teacher_id, 'inativo')

    @staticmethod
    def activate_teacher(teacher_id):
        """
        Ativação lógica - marca o usuario do professor como ativo

        Args:
            teacher_id (int): ID do professor

        Returns:
            bool: True se ativado com sucesso
        """
        return Teacher.update_teacher_status(teacher_id, 'ativo')



    @staticmethod
    def permanent_delete_teacher(teacher_id):
        """
        Exclusão física - remove o professor do banco de dados
        CUIDADO: Esta operação não pode ser desfeita!

        Args:
            teacher_id (int): ID do professor

        Returns:
            bool: True se removido com sucesso
        """
        query = "DELETE FROM teachers WHERE id = %s"
        result = send_sql_command(query, (teacher_id,))
        return result != 0

    @staticmethod
    def check_teacher_exists(teacher_id):
        """
        Verifica se um professor existe

        Args:
            teacher_id (int): ID do professor

        Returns:
            bool: True se o professor existe
        """
        query = "SELECT id FROM teachers WHERE id = %s"
        result = send_sql_command(query, (teacher_id,))
        return result != 0

    @staticmethod
    def check_teacher_email_exists(email, teacher_id=None):
        """
        Verifica se já existe um professor com o email informado

        Args:
            email (str): Email do professor
            teacher_id (int, optional): ID do professor

        Returns:
            bool: True se já existe um usuario com este email
        """
        if teacher_id:
            teacher = Teacher.select_teacher_by_id(teacher_id)
            if teacher:
                query = """
                    SELECT id FROM users 
                    WHERE username = %s AND id != %s
                """
                result = send_sql_command(query, (email, teacher[4]))
        else:
            query = """
                SELECT id FROM users 
                WHERE username = %s
            """
            result = send_sql_command(query, (email,))
        return result != 0