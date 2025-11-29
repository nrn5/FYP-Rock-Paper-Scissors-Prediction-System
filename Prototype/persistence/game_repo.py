from persistence.db_connection import get_connection, return_connection

class GameRepository:
    @staticmethod
    def save_round(player_id, player_move, computer_move, outcome):
        """ insert a single round into the database """
        conn = get_connection()
        if conn is None:
            print("\n[game_repo.py] Connection failure")
            return
        
        try:
            cur = conn.cursor()
            cur.execute(""" INSERT INTO game_history (player_id, player_move, computer_move, outcome)
                            VALUES (%s, %s, %s, %s); """, 
                        (player_id, player_move, computer_move, outcome))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print("\n[game_repo.py] Failed to save round: ", e)  
            return False
        finally:
            return_connection(conn)  

    @staticmethod
    def create_player(name):
        """ inserts a new player """
        conn = get_connection()
        if conn is None:
            print("\n[game_repo.py] Connection failure")
            return
        
        try:
            cur = conn.cursor()
            cur.execute(""" INSERT INTO players (name)
                            VALUES (%s)
                            RETURNING player_id; """,
                        (name, ))
            # get returned player id
            player_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return player_id
        except Exception as e:
            print("\n[game_repo.py] Failed to create player: ", e)
            return None
        finally:
            return_connection(conn)

    @staticmethod
    def get_history(player_id):
        """ get all previous rounds for a player, returns a list of tuples """
        conn = get_connection()
        if conn is None:
            print("\n[game_repo.py] Connection failure")
            return []
        
        try:
            cur = conn.cursor()
            cur.execute(""" SELECT player_move, computer_move, outcome, played_at
                            FROM game_history
                            WHERE player_id = %s
                            ORDER BY played_at ASC; """,
                        (player_id, ))
            # get all returned rows
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print("\n[game_repo.py] Could not fetch history: ", e)
            return []
        finally:
            return_connection(conn)
