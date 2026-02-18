from persistence.db_connection import get_connection, return_connection
import psycopg2

class PlayerRepository:
    def create_player(self, name: str):
        conn = get_connection()
        if conn is None:
            print("\n[player_repo.py] Connection failure")
            return None
        
        try:
            with conn.cursor() as cur:
                cur.execute(""" INSERT INTO players (name) 
                                VALUES (%s)
                                RETURNING player_id; """,
                            (name, ))
                # get returned player id
                player_id = cur.fetchone()[0]
                conn.commit()
                print(f"\n[player_repo.py] Player '{name}' created")
                return "created", player_id
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            print(f"\n[player_repo.py] Player '{name} already exists")
            return "exists", player_id
        except Exception as e:
            conn.rollback()
            print(f"[player_repo.py] Error: {e}")
            return "error", None
        finally:
            return_connection(conn)

    def get_player_by_name(self, name: str):
        conn = get_connection()
        if conn is None:
            print("\n[player_repo.py] Connection failure")
            return False
        
        try:
            with conn.cursor() as cur:
                cur.execute(""" SELECT player_id, name
                                FROM players
                                WHERE name = %s""", 
                                (name, ))
                # get player
                player = cur.fetchone()
                return player 
        except Exception as e:
            print(f"\n[player_repo.py] Error retrieving player: {e}")
            return None
        finally:
            return_connection(conn)
