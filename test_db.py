import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
print(f"Testing connection to: {db_url}")

# Basic parsing of DATABASE_URL: mysql+pymysql://root:root@localhost/club_robotica
try:
    # Attempt to extract connection details
    # This is a bit naive but should work for the standard format in .env
    conn_str = db_url.split('://')[1]
    user_pass, host_db = conn_str.split('@')
    user, password = user_pass.split(':')
    host, db = host_db.split('/')
    
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connection successful!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")
