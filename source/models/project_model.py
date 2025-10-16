from utils.mysqlUtils import send_sql_command, connect_to_db


class Project:
    def __init__(self, id, name, description, course_id, observation, status):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.course_id = course_id
        self.observation = observation

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status
        }

    @staticmethod
    def select_all_projects(status='Pré-projeto'):
        """
        Busca todos os projetos

        Args:
            status (str): Status dos projetos a buscar ('Pré-projeto','Qualificação','Defesa','Finalizado','Trancado','all')

        Returns:
            list: Lista de tuplas com os dados dos projetos
        """
        if status == 'all':
            query = """
                SELECT id, name, description, course_id, observation, status, created_at, updated_at
                FROM projects 
                ORDER BY name ASC
            """
            return send_sql_command(query)
        else:
            query = """
                SELECT id, name, description, course_id, observation, status, created_at, updated_at 
                FROM projects 
                WHERE status = %s
                ORDER BY name ASC
            """
            return send_sql_command(query, (status,))


    @staticmethod
    def select_project_by_id(project_id):
        """
        Busca um projeto específico por ID

        Args:
            project_id (int): ID do projeto

        Returns:
            tuple: Dados do projeto ou None se não encontrado
        """
        query = """
            SELECT id, name, description, course_id, observation, status, created_at, updated_at 
            FROM projects 
            WHERE id = %s
            ORDER BY name ASC
        """
        result = send_sql_command(query, (project_id,))
        print("="* 60)
        print(result)
        return result[0] if result != 0 else None

    @staticmethod
    def get_project_course(project_id):
        """Busca o curso vinculado ao projeto"""
        query = """
            SELECT c.id, c.name, c.observation, c.status, c.created_at, c.updated_at
            FROM course c
            INNER JOIN projects p ON p.course_id = c.id
            WHERE p.id = %s
        """
        result = send_sql_command(query, (project_id,))
        return result[0] if result else None

    @staticmethod
    def get_project_teachers(project_id):
        """Busca todos os professores do projeto"""
        query = """
            SELECT t.id, t.name, t.observation, t.image, t.user_id,
                   t.created_at, t.updated_at
            FROM teachers t
            INNER JOIN teacher_project pt ON pt.teacher_id = t.id
            WHERE pt.project_id = %s
            ORDER BY t.name ASC
        """
        return send_sql_command(query, (project_id,))

    @staticmethod
    def get_project_students(project_id):
        """Busca todos os alunos do projeto"""
        query = """
            SELECT s.id, s.name, s.registration, s.observation, s.image,
                   s.status, s.user_id, s.created_at, s.updated_at
            FROM students s
            INNER JOIN student_project ps ON ps.student_id = s.id
            WHERE ps.project_id = %s
            ORDER BY s.name ASC
        """
        return send_sql_command(query, (project_id,))

    @staticmethod
    def get_project_reports(project_id):
        """Busca todos os relatórios do projeto"""
        query = """
            SELECT r.id, r.description, r.pendency, r.status, r.next_steps,
                   r.local, r.feedback, r.teacher_id, r.created_at, r.updated_at,
                   t.id as teacher_id, t.name as teacher_name, t.observation as teacher_obs,
                   t.image as teacher_image, t.user_id as teacher_user_id
            FROM report r
            LEFT JOIN teachers t ON r.teacher_id = t.id
            WHERE r.project_id = %s
            ORDER BY r.created_at DESC
        """
        return send_sql_command(query, (project_id,))

    @staticmethod
    def insert_project(name, description=None, course_id=None, observation=None, status='Pré-projeto'):
        """Insere um novo projeto"""
        query = """
            INSERT INTO projects (name, description, course_id, observation, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        result = send_sql_command(query, (name, description, course_id, observation, status))
        return result if result else None

    @staticmethod
    def update_project(project_id, name=None, description=None, course_id=None, observation=None, status=None):
        """Atualiza os dados de um projeto"""
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)

        if description is not None:
            updates.append("description = %s")
            params.append(description)

        if course_id is not None:
            updates.append("course_id = %s")
            params.append(course_id)

        if observation is not None:
            updates.append("observation = %s")
            params.append(observation)

        if status is not None:
            updates.append("status = %s")
            params.append(status)

        if not updates:
            return False

        params.append(project_id)
        query = f"""
            UPDATE projects
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """

        result = send_sql_command(query, tuple(params))
        return result is not None

    @staticmethod
    def delete_project(project_id):
        """Remove um projeto do banco de dados"""
        query = "DELETE FROM projects WHERE id = %s"
        result = send_sql_command(query, (project_id,))
        return result is not None

    @staticmethod
    def check_project_exists(project_id):
        """Verifica se um projeto existe"""
        query = "SELECT id FROM projects WHERE id = %s"
        result = send_sql_command(query, (project_id,))
        return len(result) > 0

    # ===== TEACHERS =====

    @staticmethod
    def add_teacher_to_project(project_id, teacher_id):
        """Adiciona um professor ao projeto"""
        query = """
            INSERT INTO teacher_project (project_id, teacher_id)
            VALUES (%s, %s)
        """
        result = send_sql_command(query, (project_id, teacher_id))
        return result is not None

    @staticmethod
    def remove_teacher_from_project(project_id, teacher_id):
        """Remove um professor do projeto"""
        query = """
            DELETE FROM teacher_project
            WHERE project_id = %s AND teacher_id = %s
        """
        result = send_sql_command(query, (project_id, teacher_id))
        return result is not None

    @staticmethod
    def check_teacher_in_project(project_id, teacher_id):
        """Verifica se um professor já está no projeto"""
        query = """
            SELECT id FROM teacher_project
            WHERE project_id = %s AND teacher_id = %s
        """
        result = send_sql_command(query, (project_id, teacher_id))
        return len(result) > 0

    # ===== STUDENTS =====

    @staticmethod
    def add_student_to_project(project_id, student_id):
        """Adiciona um aluno ao projeto"""
        query = """
            INSERT INTO student_project (project_id, student_id)
            VALUES (%s, %s)
        """
        result = send_sql_command(query, (project_id, student_id))
        return result is not None

    @staticmethod
    def remove_student_from_project(project_id, student_id):
        """Remove um aluno do projeto"""
        query = """
            DELETE FROM student_project
            WHERE project_id = %s AND student_id = %s
        """
        result = send_sql_command(query, (project_id, student_id))
        return result is not None

    @staticmethod
    def check_student_in_project(project_id, student_id):
        """Verifica se um aluno já está no projeto"""
        query = """
            SELECT id FROM student_project
            WHERE project_id = %s AND student_id = %s
        """
        result = send_sql_command(query, (project_id, student_id))
        return len(result) > 0

    # ===== REPORTS =====

    @staticmethod
    def insert_report(project_id, description, teacher_id=None, pendency=None,
                      status='pendente', next_steps=None, local=None, feedback=None):
        """Insere um novo relatório no projeto"""
        query = """
            INSERT INTO report (project_id, description, teacher_id, 
                                        pendency, status, next_steps, local, feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        result = send_sql_command(query, (project_id, description, teacher_id,
                                              pendency, status, next_steps, local, feedback))
        return result if result else None

    @staticmethod
    def update_report(report_id, description=None, pendency=None, status=None,
                      next_steps=None, local=None, feedback=None, teacher_id=None):
        """Atualiza um relatório"""
        updates = []
        params = []

        if description is not None:
            updates.append("description = %s")
            params.append(description)

        if pendency is not None:
            updates.append("pendency = %s")
            params.append(pendency)

        if status is not None:
            updates.append("status = %s")
            params.append(status)

        if next_steps is not None:
            updates.append("next_steps = %s")
            params.append(next_steps)

        if local is not None:
            updates.append("local = %s")
            params.append(local)

        if feedback is not None:
            updates.append("feedback = %s")
            params.append(feedback)
        print("teachar")
        print(teacher_id)
        if teacher_id is not None:
            updates.append("teacher_id = %s")
            params.append(teacher_id)

        if not updates:
            return False

        params.append(report_id)
        query = f"""
            UPDATE report
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """

        result = send_sql_command(query, tuple(params))
        return result is not None

    @staticmethod
    def delete_report(report_id):
        """Remove um relatório"""
        query = "DELETE FROM report WHERE id = %s"
        result = send_sql_command(query, (report_id,))
        return result is not None

    @staticmethod
    def get_report_by_id(report_id):
        """Busca um relatório específico"""
        query = """
            SELECT id, project_id, description, pendency, status, next_steps,
                   local, feedback, teacher_id, created_at, updated_at
            FROM report
            WHERE id = %s
        """
        result = send_sql_command(query, (report_id,))
        return result[0] if result else None

    # ===== STATISTICS =====

    @staticmethod
    def count_projects():
        """Conta o total de projetos"""
        query = "SELECT COUNT(*) FROM projects"
        result = send_sql_command(query)
        return result[0][0] if result else 0

    @staticmethod
    def count_projects_by_status(status):
        """Conta projetos por status"""
        query = "SELECT COUNT(*) FROM projects WHERE status = %s"
        result = send_sql_command(query, (status,))
        return result[0][0] if result else 0

    @staticmethod
    def get_project_statistics():
        """Retorna estatísticas dos projetos"""
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Pré-projeto' THEN 1 ELSE 0 END) as pre_project,
                SUM(CASE WHEN status = 'Qualificação' THEN 1 ELSE 0 END) as qualified,
                SUM(CASE WHEN status = 'Defesa' THEN 1 ELSE 0 END) as thesis_defense,
                SUM(CASE WHEN status = 'Finalizado' THEN 1 ELSE 0 END) as finalized,
                SUM(CASE WHEN status = 'Trancado' THEN 1 ELSE 0 END) as locked,
                MAX(created_at) as ultimo_cadastro
            FROM projects
        """
        result = send_sql_command(query)

        if result:
            row = result[0]
            return {
                'total': row[0],
                'pre_projeto': row[1],
                'qualificacao': row[2],
                'defesa': row[3],
                'finalizado': row[4],
                'trancado': row[5],
                'ultimo_cadastro': row[6]
            }
        return {
            'total': 0,
            'pre_projeto': 0,
            'qualificacao': 0,
            'defesa': 0,
            'finalizado': 0,
            'trancado': 0,
            'ultimo_cadastro': None
        }