def tim_o_trong(board):
    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:
                return r, c

def lay_hanh_dong(r, c):
    actions = []
    if r > 0: actions.append('U')
    if r < 2: actions.append('D')
    if c > 0: actions.append('L')
    if c < 2: actions.append('R')
    return actions

def di_chuyen(board, action):
    new_board = [row[:] for row in board]
    r, c = tim_o_trong(new_board)
    if action == 'U': new_board[r][c], new_board[r-1][c] = new_board[r-1][c], new_board[r][c]
    if action == 'D': new_board[r][c], new_board[r+1][c] = new_board[r+1][c], new_board[r][c]
    if action == 'L': new_board[r][c], new_board[r][c-1] = new_board[r][c-1], new_board[r][c]
    if action == 'R': new_board[r][c], new_board[r][c+1] = new_board[r][c+1], new_board[r][c]
    return new_board