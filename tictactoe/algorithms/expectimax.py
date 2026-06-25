from .minimax import evaluate, is_draw

def find_best_move_expectimax(board, ai_player, p=0.7):
    opponent = 'O' if ai_player == 'X' else 'X'
    nodes_count = 0

    def expectimax(board, is_max):
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
                    val = expectimax(board, False)
                    board[i] = ' '
                    best_val = max(best_val, val)
            return best_val
        else:
            empty_spots = [i for i in range(9) if board[i] == ' ']
            if not empty_spots:
                return 0

            utilities = []
            for i in empty_spots:
                board[i] = opponent
                val = expectimax(board, True)
                board[i] = ' '
                utilities.append((i, val))

            utilities.sort(key=lambda x: x[1])
            min_val = utilities[0][1]

            avg_val = sum(x[1] for x in utilities) / len(utilities)

            expected_val = p * min_val + (1 - p) * avg_val
            return expected_val

    best_val = -1000
    best_move = -1
    for i in range(9):
        if board[i] == ' ':
            board[i] = ai_player
            move_val = expectimax(board, False)
            board[i] = ' '
            if move_val > best_val:
                best_val = move_val
                best_move = i

    return best_move, nodes_count
