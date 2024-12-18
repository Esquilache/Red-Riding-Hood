from db import get_connection

def initialize_tables():
    query_warnings = """
    CREATE TABLE IF NOT EXISTS user_warnings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        guild_id BIGINT NOT NULL,
        reason VARCHAR(255) NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """

    query_logs = """
    CREATE TABLE IF NOT EXISTS command_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        command VARCHAR(255) NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """

    query_configs = """
    CREATE TABLE IF NOT EXISTS server_configs (
        guild_id BIGINT NOT NULL,
        config_key VARCHAR(255) NOT NULL,
        config_value TEXT NOT NULL,
        PRIMARY KEY (guild_id, config_key)
    );
    """

    # Execute queries
    connection = get_connection()
    cursor = connection.cursor()
    for query in [query_warnings, query_logs, query_configs]:
        cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    initialize_tables()
