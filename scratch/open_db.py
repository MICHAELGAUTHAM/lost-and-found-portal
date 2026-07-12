import os
import pg8000.native
from dotenv import load_dotenv

load_dotenv()

html_content = """
<!DOCTYPE html>
<html>
<head>
<title>Database Viewer: lost_and_found</title>
<style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f9; color: #333; }
    h1 { color: #2c3e50; }
    h2 { color: #34495e; margin-top: 30px; padding-bottom: 10px; border-bottom: 2px solid #bdc3c7; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
    th, td { padding: 12px 15px; text-align: left; border: 1px solid #ddd; }
    th { background-color: #2980b9; color: white; }
    tr:nth-child(even) { background-color: #f2f2f2; }
    .empty { font-style: italic; color: #7f8c8d; }
</style>
</head>
<body>
    <h1>Database: lost_and_found</h1>
"""

try:
    con = pg8000.native.Connection(
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 5432)),
        database=os.environ.get('DB_NAME', 'lost_and_found')
    )
    
    tables = con.run("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    
    for t in tables:
        table_name = t[0]
        html_content += f"<h2>Table: {table_name}</h2>"
        
        # Get column details
        cols = con.run(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' ORDER BY ordinal_position")
        col_names = [c[0] for c in cols]
        
        html_content += "<table><thead><tr>"
        for col_name in col_names:
            html_content += f"<th>{col_name}</th>"
        html_content += "</tr></thead><tbody>"
        
        # Get records
        records = con.run(f"SELECT * FROM {table_name}")
        
        if not records:
            html_content += f"<tr><td colspan='{len(col_names)}' class='empty'>No records found in this table.</td></tr>"
        else:
            for record in records:
                html_content += "<tr>"
                for val in record:
                    html_content += f"<td>{str(val)}</td>"
                html_content += "</tr>"
                
        html_content += "</tbody></table>"
        
    con.close()
except Exception as e:
    html_content += f"<p>Error connecting to database: {e}</p>"

html_content += """
</body>
</html>
"""

html_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'db_dump.html'))
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Opening {html_file}...")
os.startfile(html_file)

