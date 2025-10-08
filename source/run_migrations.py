import importlib

migrations = [
    "001_create_user_table",
    "002_create_course_table",
    # "003_create_device_table",
    # "004_create_config_table",
    # "005_create_display_table",
    # "006_create_device_event_table",
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