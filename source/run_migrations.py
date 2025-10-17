import importlib

migrations = [
    "001_create_user_table",
    "002_create_course_table",
    "003_create_students_table",
    "004_create_teachers_table",
    "005_create_projects_table",
    "006_create_student_course_table",
    "007_create_student_project_table",
    "008_create_teacher_course_table",
    "009_create_teacher_project_table",
    "010_create_report_table",
    "011_create_calendar_table",
    "012_create_project_files_table",
    "013_alter_teacher_project_add_role",
    "014_create_defense_minutes_table",
    "015_add_name_to_users",
    "016_alter_defense_minutes_student_name_nullable",

]

def run_all_migrations():
    for migration in migrations:
        print(f"Executando migração: {migration}")
        try:
            migration_module = importlib.import_module("migrations."+migration)
            migration_module.run_migration()
            print(f"Migração {migration} executada com sucesso.")
        except Exception as e:
            print(f"Erro ao executar a migração {migration}: {e}")

if __name__ == "__main__":
    run_all_migrations()