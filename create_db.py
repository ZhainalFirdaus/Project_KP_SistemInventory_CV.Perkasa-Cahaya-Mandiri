import pymysql

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': ''
}

try:
    # Connect to MySQL Server (not specific database)
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    
    # Create Database
    db_name = 'inventory_kp'
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"Database '{db_name}' berhasil dibuat atau sudah ada.")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
