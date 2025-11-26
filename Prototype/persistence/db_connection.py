import psycopg2

DB_NAME = "rps_project"
DB_USER = "rps_user"
DB_PASSWORD = "rps_password"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("\nSuccessfully connected to database")
        return conn
    except Exception as e:
        print("\nFailed to connect to database:")
        print(e)
        return None
    