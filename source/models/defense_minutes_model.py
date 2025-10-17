from utils.mysqlUtils import send_sql_command

class DefenseMinutes:
    @staticmethod
    def insert(project_id, file_id, student_name, title, result, location=None, started_at=None, created_by=None):
        query = """
            INSERT INTO defense_minutes (project_id, file_id, student_name, title, result, location, started_at, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return send_sql_command(query, (project_id, file_id, student_name, title, result, location, started_at, created_by))

    @staticmethod
    def list_by_project(project_id):
        query = """
            SELECT id, file_id, student_name, title, result, location, started_at, created_at
            FROM defense_minutes
            WHERE project_id = %s
            ORDER BY created_at DESC
        """
        return send_sql_command(query, (project_id,))

    @staticmethod
    def get_by_id(ata_id):
        query = """
            SELECT id, project_id, file_id, student_name, title, result, location, started_at, created_at, created_by
            FROM defense_minutes
            WHERE id = %s
        """
        result = send_sql_command(query, (ata_id,))
        return result[0] if result and result != "0" else None

    @staticmethod
    def delete_by_id(ata_id):
        query = "DELETE FROM defense_minutes WHERE id = %s"
        return send_sql_command(query, (ata_id,)) is not None

    @staticmethod
    def validate_file_ownership(project_id, file_id):
        query = "SELECT id FROM project_files WHERE id = %s AND project_id = %s"
        result = send_sql_command(query, (file_id, project_id))
        return bool(result and result != "0")
    
    @staticmethod
    def list_all_with_project():
        """Lista todas as atas com informações do projeto"""
        query = """
            SELECT dm.id, dm.project_id, dm.file_id, dm.student_name, dm.title, 
                   dm.result, dm.location, dm.started_at, dm.created_at, dm.created_by,
                   p.name as project_name
            FROM defense_minutes dm
            INNER JOIN projects p ON p.id = dm.project_id
            ORDER BY dm.created_at DESC
        """
        return send_sql_command(query, ())
