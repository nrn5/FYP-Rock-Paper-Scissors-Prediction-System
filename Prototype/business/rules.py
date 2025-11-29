def determine_winner(player_move, computer_move):
    if player_move == computer_move:
        return "draw"

    beats = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }

    return "win" if beats[player_move] == computer_move else "loss"
