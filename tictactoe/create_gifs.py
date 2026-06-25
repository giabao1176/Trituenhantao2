import sys
import os
import random
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from algorithms import find_best_move_minimax, find_best_move_alphabeta, find_best_move_expectimax

def draw_board_frame(board, algo_name="", step_num=0, last_player="", last_move=-1, nodes_count=0):
    grid_size = 300
    status_height = 120
    width = grid_size
    height = grid_size + status_height

    img = Image.new("RGBA", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)

    draw.line([(100, 10), (100, 290)], fill="#7f8c8d", width=4)
    draw.line([(200, 10), (200, 290)], fill="#7f8c8d", width=4)
    draw.line([(10, 100), (290, 100)], fill="#7f8c8d", width=4)
    draw.line([(10, 200), (290, 200)], fill="#7f8c8d", width=4)

    for i in range(9):
        r, c = i // 3, i % 3
        mark = board[i]

        cx = c * 100 + 50
        cy = r * 100 + 50

        if mark == 'X':
            draw.line([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill="#e74c3c", width=6)
            draw.line([(cx + 30, cy - 30), (cx - 30, cy + 30)], fill="#e74c3c", width=6)
        elif mark == 'O':
            draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline="#3498db", width=6)

    draw.rectangle([0, grid_size, width, height], fill="#2c3e50")
    try:
        font_large = ImageFont.truetype("arial.ttf", 13)
        font_small = ImageFont.truetype("arial.ttf", 11)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    line1 = f"Vai trò: X (Người chơi - Đỏ) vs O ({algo_name} - Xanh)"
    draw.text((10, grid_size + 10), line1, fill="#ffffff", font=font_large)

    if last_player:
        row, col = last_move // 3 + 1, last_move % 3 + 1
        name = "Người chơi" if last_player == 'X' else f"AI {algo_name}"
        line2 = f"Bước: {step_num} | Quân {last_player} ({name}) đi ô ({row},{col})"
    else:
        line2 = f"Bước: {step_num} | Trận đấu bắt đầu"
    draw.text((10, grid_size + 36), line2, fill="#bdc3c7", font=font_small)

    if last_player == 'O' and nodes_count > 0:
        line3 = f"Số trạng thái duyệt ở nước này: {nodes_count}"
    else:
        line3 = "Số trạng thái duyệt ở nước này: N/A"
    draw.text((10, grid_size + 62), line3, fill="#bdc3c7", font=font_small)

    from algorithms.minimax import is_win, is_draw
    if is_win(board, 'X'):
        line4 = "Kết quả: X (Người chơi) THẮNG!"
        text_color = "#e74c3c"
    elif is_win(board, 'O'):
        line4 = f"Kết quả: O (AI {algo_name}) THẮNG!"
        text_color = "#3498db"
    elif is_draw(board):
        line4 = "Kết quả: HÒA!"
        text_color = "#2ecc71"
    else:
        line4 = "Trận đấu đang diễn ra..."
        text_color = "#95a5a6"

    draw.text((10, grid_size + 88), line4, fill=text_color, font=font_large)

    return img

def make_game_gif(algo_name, ai_func, filename):
    print(f"Generating GIF for Tic-Tac-Toe: Human (X) vs AI {algo_name} (O)...")
    random.seed(42 + len(algo_name))
    board = [' ' for _ in range(9)]

    frames = [draw_board_frame(board, algo_name=algo_name, step_num=0, last_player="", last_move=-1, nodes_count=0)]
    current_player = 'X'

    from algorithms.minimax import is_win, is_draw

    step_num = 0
    for step in range(9):
        if is_win(board, 'X') or is_win(board, 'O') or is_draw(board):
            break

        step_num += 1
        player_who_moved = current_player

        if current_player == 'X':
            empty_spots = [i for i in range(9) if board[i] == ' ']
            move = random.choice(empty_spots) if empty_spots else -1
            nodes_count = 0
            if move != -1:
                board[move] = 'X'
            current_player = 'O'
        else:
            if algo_name == "Expectimax":
                move, nodes_count = ai_func(board, 'O', p=0.7)
            else:
                res = ai_func(board, 'O')
                move = res[0]
                nodes_count = res[1]

            if move != -1:
                board[move] = 'O'
            current_player = 'X'

        frames.append(draw_board_frame(board, algo_name=algo_name, step_num=step_num, last_player=player_who_moved, last_move=move, nodes_count=nodes_count))

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=1000,
        loop=0
    )
    print(f"  -> Saved successfully at: gifs/{filename} ({len(frames)} frames)")

def main():
    make_game_gif("Minimax", find_best_move_minimax, "tictactoe_minimax.gif")
    make_game_gif("Alpha-Beta", find_best_move_alphabeta, "tictactoe_alphabeta.gif")
    make_game_gif("Expectimax", find_best_move_expectimax, "tictactoe_expectimax.gif")
    print("\nDone! All Tic-Tac-Toe game GIFs created successfully in 'gifs/' folder.")

if __name__ == "__main__":
    main()
