from utils.mysqlUtils import send_sql_command


class ProjectFile:
    @staticmethod
    def insert_file(project_id, original_name, stored_name, mime_type=None, size=None, uploaded_by=None):
        query = (
            """
            INSERT INTO project_files (project_id, original_name, stored_name, mime_type, size, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        )
        return send_sql_command(query, (project_id, original_name, stored_name, mime_type, size, uploaded_by))

    @staticmethod
    def list_by_project(project_id):
        query = (
            """
            SELECT id, project_id, original_name, stored_name, mime_type, size, uploaded_by, created_at
            FROM project_files
            WHERE project_id = %s
            ORDER BY created_at DESC
            """
        )
        return send_sql_command(query, (project_id,))

    @staticmethod
    def get_by_id(file_id):
        query = (
            """
            SELECT id, project_id, original_name, stored_name, mime_type, size, uploaded_by, created_at
            FROM project_files
            WHERE id = %s
            """
        )
        result = send_sql_command(query, (file_id,))
        return result[0] if result and result != "0" else None

    @staticmethod
    def delete_by_id(file_id):
        query = "DELETE FROM project_files WHERE id = %s"
        return send_sql_command(query, (file_id,)) is not None
