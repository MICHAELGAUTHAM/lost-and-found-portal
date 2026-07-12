import os
import pg8000.native
from dotenv import load_dotenv

load_dotenv()

try:
    con = pg8000.native.Connection(
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 5432)),
        database=os.environ.get('DB_NAME', 'lost_and_found')
    )
    
    tables = con.run("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    print("========================================")
    print("Database: lost_and_found")
    print("========================================")
    for t in tables:
        table_name = t[0]
        print(f"\nTable: {table_name}")
        # Get column details
        cols = con.run(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table_name}'")
        for c in cols:
            print(f"  - {c[0]} ({c[1]})")
            
        # Get record count
        count = con.run(f"SELECT COUNT(*) FROM {table_name}")
        print(f"  -> Total records: {count[0][0]}")
        
    con.close()
except Exception as e:
    print(f"Error connecting to database: {e}")
