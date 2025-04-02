import os

DB_CONFIG = {
    "type": "postgres",
    "connection_string": (
        f"postgresql://"
        f"{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'postgres123')}@"
        f"{os.getenv('DB_HOST', 'db')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'meeting_scheduler')}"
    )
}

MCP_API_KEY = os.getenv('MCP_API_KEY')
