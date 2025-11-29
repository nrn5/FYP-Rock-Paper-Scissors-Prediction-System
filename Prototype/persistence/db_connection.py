import psycopg2
from psycopg2.pool import SimpleConnectionPool

DB_NAME = "rps_project"
DB_USER = "rps_user"
DB_PASSWORD = "rps_password"
DB_HOST = "localhost"
DB_PORT = "5432"

_connection_pool = None

def init_connection_pool():
    pass

def get_connection():
    pass

def return_connection():
    pass

def close_pool():
    pass