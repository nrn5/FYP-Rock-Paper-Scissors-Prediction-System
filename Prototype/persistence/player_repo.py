from persistence.db_connection import get_connection, return_connection
import psycopg2

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
                # Insert new player
                cur.execute(""" INSERT INTO players (name) 
                                VALUES (%s)
                                RETURNING player_id; """,
                            (name, ))
                # Fetch the new player's ID
                player_id = cur.fetchone()[0]
                conn.commit()
                print(f"\n[player_repo.py] Player '{name}' created")
                
                # Create default settings for this player
                self.create_default_settings(player_id)
                
                return "created", player_id
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            print(f"\n[player_repo.py] Player '{name}' already exists")
            return "exists", None
        except Exception as e:
            conn.rollback()
            print(f"[player_repo.py] Error: {e}")
            return "error", None
        finally:
            return_connection(conn)

    def create_default_settings(self, player_id):
        conn = get_connection()
        if conn is None:
            print("\n[player_repo.py] Connection failure")
            return
        try:
            with conn.cursor() as cur:
                cur.execute(""" INSERT INTO user_settings (player_id)
                                VALUES (%s) """,
                    (player_id,))
                conn.commit()
                print(f"\n[player_repo.py] Default settings created for player {player_id}")
        except Exception as e:
            conn.rollback()
            print(f"\n[player_repo.py] Error creating default settings: {e}")
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
                                WHERE name = %s """, 
                                (name, ))
                # get player
                player = cur.fetchone()
                return player 
        except Exception as e:
            print(f"\n[player_repo.py] Error retrieving player: {e}")
            return None
        finally:
            return_connection(conn)
