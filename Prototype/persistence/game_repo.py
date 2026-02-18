from persistence.db_connection import get_connection, return_connection

class GameRepository:
    def save_round(self, player_id, player_move, computer_move, outcome):
        conn = get_connection()
        if conn is None:
            print("\n[game_repo.py] Connection failure")
            return
        
        try:
            with conn.cursor() as cur:
                cur.execute(""" INSERT INTO game_history (player_id, player_move, computer_move, outcome)
                                VALUES (%s, %s, %s, %s); """, 
                            (player_id, player_move, computer_move, outcome))
                conn.commit()
                print("\n[game_repo.py] Round saved")
                return True
        except Exception as e:
            conn.rollback()
            print("\n[game_repo.py] Error saving round: ", e)  
            return False
        finally:
            return_connection(conn)  

    def get_history(self, player_id):
        conn = get_connection()
        if conn is None:
            print("\n[game_repo.py] Connection failure")
            return []
        
        try:
            with conn.cursor() as cur:
                cur.execute(""" SELECT player_move, computer_move, outcome, played_at
                                FROM game_history
                                WHERE player_id = %s
                                ORDER BY played_at ASC; """,
                            (player_id, ))
                # get all returned rows
                rows = cur.fetchall()
                return rows
        except Exception as e:
            print("\n[game_repo.py] Error fetching history: ", e)
            return []
        finally:
            return_connection(conn)
