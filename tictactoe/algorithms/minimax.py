def is_win(board, player):
    win_states = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for win in win_states:
        if board[win[0]] == player and board[win[1]] == player and board[win[2]] == player:
            return True
    return False

def is_draw(board):
    return ' ' not in board

def evaluate(board, ai_player, opponent):
    if is_win(board, ai_player):
        return 1
    elif is_win(board, opponent):
        return -1
    return 0

def find_best_move_minimax(board, ai_player):
    opponent = 'O' if ai_player == 'X' else 'X'
    nodes_count = 0

    def minimax(board, is_max):
        nonlocal nodes_count
        nodes_count += 1

        score = evaluate(board, ai_player, opponent)
        if score == 1 or score == -1:
            return score
        if is_draw(board):
            return 0

        if is_max:
            best_val = -1000
            for i in range(9):
                if board[i] == ' ':
                    board[i] = ai_player
                    val = minimax(board, False)
                    board[i] = ' '
                    best_val = max(best_val, val)
            return best_val
        else:
            best_val = 1000
            for i in range(9):
                if board[i] == ' ':
                    board[i] = opponent
                    val = minimax(board, True)
                    board[i] = ' '
                    best_val = min(best_val, val)
            return best_val

    best_val = -1000
    best_move = -1
    for i in range(9):
        if board[i] == ' ':
            board[i] = ai_player
            move_val = minimax(board, False)
            board[i] = ' '
            if move_val > best_val:
                best_val = move_val
                best_move = i

    return best_move, nodes_count
