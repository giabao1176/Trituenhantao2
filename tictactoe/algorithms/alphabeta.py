from .minimax import evaluate, is_draw

def find_best_move_alphabeta(board, ai_player):
    opponent = 'O' if ai_player == 'X' else 'X'
    nodes_count = 0
    prune_count = 0

    def alphabeta(board, depth, alpha, beta, is_max):
        nonlocal nodes_count, prune_count
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
                    val = alphabeta(board, depth + 1, alpha, beta, False)
                    board[i] = ' '
                    best_val = max(best_val, val)
                    alpha = max(alpha, best_val)
                    if beta <= alpha:
                        prune_count += 1
                        break
            return best_val
        else:
            best_val = 1000
            for i in range(9):
                if board[i] == ' ':
                    board[i] = opponent
                    val = alphabeta(board, depth + 1, alpha, beta, True)
                    board[i] = ' '
                    best_val = min(best_val, val)
                    beta = min(beta, best_val)
                    if beta <= alpha:
                        prune_count += 1
                        break
            return best_val

    best_val = -1000
    best_move = -1
    alpha = -1000
    beta = 1000

    for i in range(9):
        if board[i] == ' ':
            board[i] = ai_player
            move_val = alphabeta(board, 0, alpha, beta, False)
            board[i] = ' '
            if move_val > best_val:
                best_val = move_val
                best_move = i
            alpha = max(alpha, best_val)

    return best_move, nodes_count, prune_count
