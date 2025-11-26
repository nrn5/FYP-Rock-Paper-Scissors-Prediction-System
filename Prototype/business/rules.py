def determine_winner(player_move: str, computer_move: str) -> str:
    """ returns "win", "loss", or "draw" based on player move """
    if player_move == computer_move:
        return "draw"
    rules = {
        "rock":     "scissors",
        "paper":    "rock",
        "scissors": "paper"
    }
    if rules[player_move] == computer_move:
        return "win"
    else:
        return "loss"
