from utils.mysqlUtils import execute_migration


def run_migration():
    """Altera FK defense_minutes.file_id para ON DELETE SET NULL e permite NULL na coluna"""
    print("Ajustando FK defense_minutes_ibfk_2 para ON DELETE SET NULL...")

    # 1) Remover a FK atual (pode falhar se já não existir)
    execute_migration(
        """
        ALTER TABLE defense_minutes
        DROP FOREIGN KEY defense_minutes_ibfk_2
        """
    )

    # 2) Tornar a coluna file_id anulável
    execute_migration(
        """
        ALTER TABLE defense_minutes
        MODIFY COLUMN file_id INT NULL
        """
    )

    # 3) Recriar a FK com ON DELETE SET NULL
    execute_migration(
        """
        ALTER TABLE defense_minutes
        ADD CONSTRAINT defense_minutes_ibfk_2
        FOREIGN KEY (file_id) REFERENCES project_files(id)
        ON DELETE SET NULL
        """
    )

    print("FK ajustada com sucesso.")