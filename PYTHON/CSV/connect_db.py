import psycopg2

DB_NAME = 'xxxx'
DB_USER = 'xxxxx'
DB_PASSWORD = 'xxxxxxxxx'
DB_HOST = 'xxxxx'
DB_PORT = 'xxxx'


try:
    print("Connecting to the PostgreSQL database...")
    conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASSWORD,host=DB_HOST,port=DB_PORT)
    print("Connection successful!")
    print("Creating a cursor object...")
    cursor = conn.cursor()
    print("Cursor created!")
    print("Executing the query...")
    query = '''
        SELECT code 
        FROM rules_package rp 
        WHERE rp."type" = 'ams' 
        ORDER BY created_at DESC 
        LIMIT 2;
    '''
    cursor.execute(query)
    print("Query executed!")
    print("Fetching all rows from the executed query...")
    rows = cursor.fetchall()
    print("Data fetched!")
    print("Printing the fetched data:")
    for row in rows:
        print(row)

except Exception as e:
    print(f"An error occurred: {e}")
