import psycopg2
from psycopg2.pool import SimpleConnectionPool

DB_NAME = "rps_project"
DB_USER = "rps_user"
DB_PASSWORD = "rps_password"
DB_HOST = "localhost"
DB_PORT = "5432"

_connection_pool = None

def init_connection_pool(minconn=1, maxconn=5):
    """ init PostgreSQL connection pool """
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = SimpleConnectionPool(
                minconn,
                maxconn,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME
            )
            print("\n[db_connection.py] Connection pool initialised\n")
        except Exception as e:
            print("\n[db_connection.py] Could not create connection pool: ", e)
            raise

def get_connection():
    """ retrives connection from the pool """
    if _connection_pool is None:
        init_connection_pool()
    try:
        return _connection_pool.getconn()
    except Exception as e:
        print("\n[db_connection.py] Failed to get connection: ", e)
        return None

def return_connection(conn):
    """ returns a connection form the pool """
    if _connection_pool and conn:
        _connection_pool.putconn(conn)

def close_pool():
    """ closes all connections in the pool """
    if _connection_pool:
        _connection_pool.closeall()
        print("\n[db_connection.py] Conneciton pool closed")