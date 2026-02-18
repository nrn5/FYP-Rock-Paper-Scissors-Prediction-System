from persistence.player_repo import PlayerRepository

class PlayerManager:
    def __init__(self):
        self.repo = PlayerRepository()
        self.current_player = None 

    def create_player(self, name: str):
        """ creates a player, returns a dict with status and player id """
        status, player_id = self.repo.create_player(name)
        if status == "created":
            # store logged in user
            self.current_player = (player_id, name)
        return {"status": status, "player_id": player_id}


    def login_player(self, name: str):
        """ logs in an existing player, returns player id or none """
        player = self.repo.get_player_by_name(name)
        if player:
            self.current_player = player
            return {"success": True, "player_id": player[0]}
        return {"success": False, "player_id": None}
    
    def get_current_player(self):
        return self.current_player
    