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