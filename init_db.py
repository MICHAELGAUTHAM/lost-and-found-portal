import os
import pg8000.native
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_NAME = os.environ.get("DB_NAME", "lost_and_found")
DB_SSL = os.environ.get("DB_SSL", "false").lower() in ("true", "1", "yes")

def create_database():
    try:
        # Connect to default 'postgres' database to create the new one
        ssl_context = True if DB_SSL else None
        con = pg8000.native.Connection(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database="postgres",
            ssl_context=ssl_context
        )
        
        # Check if database exists
        dbs = con.run("SELECT datname FROM pg_database WHERE datname = :db", db=DB_NAME)
        if not dbs:
            con.run(f"CREATE DATABASE {DB_NAME}")
            print(f"Database {DB_NAME} created successfully.")
        else:
            print(f"Database {DB_NAME} already exists.")
        con.close()
    except Exception as e:
        print(f"Error creating database: {e}")

def run_schema():
    try:
        ssl_context = True if DB_SSL else None
        con = pg8000.native.Connection(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            ssl_context=ssl_context
        )
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
            
        # pg8000.native doesn't natively run multiple statements separated by semicolons
        # easily unless we split them.
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        for stmt in statements:
            con.run(stmt)
            
        print("Schema initialized successfully.")
        con.close()
    except Exception as e:
        print(f"Error initializing schema: {e}")

if __name__ == "__main__":
    create_database()
    run_schema()
