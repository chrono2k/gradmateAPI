from utils.mysqlUtils import send_sql_command, connect_to_db
from werkzeug.security import generate_password_hash

class Student:
    @staticmethod
    def select_all_student():
        """
        Busca todos os alunos

        Returns:
            list: Lista de tuplas com os dados dos alunos
        """
        query = """
            SELECT id, name, registration, observation, image, status, user_id, created_at, updated_at 
            FROM students 
            ORDER BY name ASC
        """
        return send_sql_command(query, ())

    @staticmethod
    def find_all_by_project(project_id):
        """
         Busca todos os alunos que estão em um determinado projeto

        Args:
            project_id (int): ID do projeto

         Returns:
             list: Lista de tuplas com os dados dos alunos
         """
        query = """
            SELECT s.id, s.name, s.registration, s.observation, s.image, s.status, s.user_id, s.created_at, s.updated_at 
            FROM students s
            INNER JOIN student_project sp ON s.id = sp.student_id
            WHERE sp.project_id = %s
        """
        return send_sql_command(query, (project_id,))


    @staticmethod
    def select_student_by_id(student_id):
        """
        Busca um aluno específico por ID

        Args:
            student_id (int): ID do aluno

        Returns:
            tuple: Dados do aluno ou None se não encontrado
        """
        query = """
            SELECT id, name, registration, observation, image, status, user_id, created_at, updated_at 
            FROM students 
            WHERE id = %s
        """
        result = send_sql_command(query, (student_id,))
        return result[0] if result != 0 else None

    @staticmethod
    def select_student_by_name(name):
        """
        Busca aluno por nome (busca parcial)

        Args:
            name (str): Nome ou parte do nome do aluno

        Returns:
            list: Lista de alunos encontrados
        """
        query = """
            SELECT id, name, registration, observation, image, status, user_id, created_at, updated_at 
            FROM students 
            WHERE name LIKE %s
            ORDER BY name ASC
        """
        search_term = f"%{name}%"
        return send_sql_command(query, (search_term,))

    @staticmethod
    def select_student_by_date_range(start_date=None, end_date=None):
        """
        Busca alunos por intervalo de datas de cadastro

        Args:
            start_date (str): Data inicial (formato: YYYY-MM-DD)
            end_date (str): Data final (formato: YYYY-MM-DD)

        Returns:
            list: Lista de alunos no intervalo de datas
        """
        if start_date and end_date:
            query = """
                SELECT id, name, registration, observation, image, status, user_id, created_at, updated_at 
                FROM students 
                WHERE DATE(created_at) BETWEEN %s AND %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (start_date, end_date))
        elif start_date:
            query = """
                SELECT id, name, registration, observation, image, status, user_id, created_at, updated_at
                FROM students 
                WHERE DATE(created_at) >= %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (start_date))
        elif end_date:
            query = """
                SELECT id, name, registration, observation, image, status, user_id, created_at, updated_at
                FROM students 
                WHERE DATE(created_at) <= %s
                ORDER BY created_at DESC
            """
            return send_sql_command(query, (end_date))
        else:
            return Student.select_all_student()

    @staticmethod
    def insert_student(name, email, registration, observation=None, image=None):
        """
        Insere um novo usuário e aluno

        Args:
            name (str): Nome do aluno
            email (str): email do aluno
            registration (str): RA do aluno
            observation (str, optional): Observação sobre o aluno
            image (str, optional): Imagem do aluno
        Returns:
            int: ID do aluno inserido ou None em caso de erro
        """
        query = """
        INSERT INTO users (username, authority, password_hash) 
        VALUES (%s, %s, %s)
        """
        user_id = send_sql_command(query, (email, 'student', generate_password_hash("fatec")))
        if user_id != 0:
            query = """
                INSERT INTO students (name, registration, observation, image, user_id) 
                VALUES (%s, %s, %s, %s, %s)
            """
            result = send_sql_command(query, (name,registration, observation, image, user_id))
            return result if result != 0 else None
        return None


    @staticmethod
    def update_student_status(student_id, status):
        """
        Atualiza o status de um aluno

        Args:
            student_id (int): ID do aluno
            status (str): Novo status ('ativo' ou 'inativo')

        Returns:
            bool: True se atualizado com sucesso
        """
        student = Student.select_student_by_id(student_id)
        if student:
            query = """
                UPDATE users 
                SET status = %s
                WHERE id = %s
            """
            send_sql_command(query, (status, student[6]))
            return True
        return False

    @staticmethod
    def update_name(student_id, name):
        """
        Atualiza o nome de um aluno

        Args:
            student_id (int): ID do aluno
            name (str): Novo nome

        Returns:
            bool: True se atualizado com sucesso
        """
        query = """
            UPDATE students 
            SET name = %s
            WHERE id = %s
        """
        send_sql_command(query, (name, student_id))
        return True

    @staticmethod
    def update_email(student_id, email):
        """
        Atualiza o email de um aluno

        Args:
            student_id (int): ID do aluno
            email (str): Novo email

        Returns:
            bool: True se atualizado com sucesso
        """
        student = Student.select_student_by_id(student_id)
        if student:
            query = """
                UPDATE users 
                SET username = %s
                WHERE id = %s
            """
            send_sql_command(query, (email, student[6]))
            return True
        return False

    @staticmethod
    def update_observation_and_image(student_id, observation, image):
        """
        Atualiza observação e imagem de um aluno

        Args:
            student_id (int): ID do aluno
            observation (str): Observação sobre o aluno
            image (str): Imagem do aluno

        Returns:
            bool: True se atualizado com sucesso
        """
        query = """
            UPDATE students 
            SET observation = %s , image = %s
            WHERE id = %s
        """
        send_sql_command(query, (observation, image, student_id))
        return True

    @staticmethod
    def delete_student(student_id):
        """
        Exclusão lógica - marca o usuario do aluno como inativo

        Args:
            student_id (int): ID do aluno

        Returns:
            bool: True se desativado com sucesso
        """
        return Student.update_student_status(student_id, 'inativo')

    @staticmethod
    def activate_student(student_id):
        """
        Ativação lógica - marca o usuario do aluno como ativo

        Args:
            student_id (int): ID do aluno

        Returns:
            bool: True se ativado com sucesso
        """
        return Student.update_student_status(student_id, 'ativo')



    @staticmethod
    def permanent_delete_student(student_id):
        """
        Exclusão física - remove o aluno do banco de dados
        CUIDADO: Esta operação não pode ser desfeita!

        Args:
            student_id (int): ID do aluno

        Returns:
            bool: True se removido com sucesso
        """
        query = "DELETE FROM students WHERE id = %s"
        result = send_sql_command(query, (student_id,))
        return result != 0

    @staticmethod
    def check_student_exists(student_id):
        """
        Verifica se um aluno existe

        Args:
            student_id (int): ID do aluno

        Returns:
            bool: True se o aluno existe
        """
        query = "SELECT id FROM students WHERE id = %s"
        result = send_sql_command(query, (student_id,))
        return result != 0

    @staticmethod
    def check_student_email_exists(email, student_id=None):
        """
        Verifica se já existe um aluno com o email informado

        Args:
            email (str): Email do aluno
            student_id (int, optional): ID do aluno

        Returns:
            bool: True se já existe um usuario com este email
        """
        if student_id:
            student = Student.select_student_by_id(student_id)
            if student:
                query = """
                    SELECT id FROM users 
                    WHERE username = %s AND id != %s
                """
                result = send_sql_command(query, (email, student[6]))
        else:
            query = """
                SELECT id FROM users 
                WHERE username = %s
            """
            result = send_sql_command(query, (email,))
        return result != 0

    @staticmethod
    def check_student_registration_exists(registration, student_id=None):
        """
        Verifica se já existe um aluno com o RA informado

        Args:
            registration (str): RA do aluno
            student_id (int, optional): ID do aluno

        Returns:
            bool: True se já existe um usuario com este RA
        """
        if student_id:
            query = """
                SELECT id FROM students 
                WHERE registration = %s AND id != %s
            """
            result = send_sql_command(query, (registration, student_id))
        else:
            query = """
                SELECT id FROM students 
                WHERE registration = %s
            """
            result = send_sql_command(query, (registration,))
        return result != 0

