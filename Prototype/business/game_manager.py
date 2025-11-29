from business.random import get_computer_move
from business.rules import determine_winner
from persistence.game_repo import GameRepository

class GameManager:
    def __init__(self, player_id=None):
        self.player_id = player_id
        # local counts
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def play_round(self, move_key: str):
        key_map = {"r": "rock", "p": "paper", "s": "scissors"}
        player_move = key_map[move_key]
        computer_move = get_computer_move()
        result = determine_winner(player_move, computer_move)

        # update local statistics
        if result == "win":
            self.wins+=1
        elif result == "loss":
            self.losses+=1
        else:
            self.draws+=1

        return {
            "player_move": player_move,
            "computer_move": computer_move,
            "result": result,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws
        }  
