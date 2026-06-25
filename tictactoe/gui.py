import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
from algorithms import find_best_move_minimax, find_best_move_alphabeta, find_best_move_expectimax

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Tic-Tac-Toe - Adversarial Search")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.game_over = False

        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.Frame(self.root, padding=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(self.root, padding=20, width=320)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_frame.pack_propagate(False)

        tk.Label(left_frame, text="Tic-Tac-Toe", font=("Segoe UI", 24, "bold"), fg="#2c3e50").pack(pady=(0, 20))

        self.grid_frame = ttk.Frame(left_frame)
        self.grid_frame.pack(pady=10)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                self.grid_frame, text=" ", font=("Segoe UI", 36, "bold"),
                width=4, height=2, bg="#ffffff", fg="#2c3e50", relief="groove", bd=2,
                command=lambda index=i: self.on_cell_click(index)
            )
            r, c = i // 3, i % 3
            btn.grid(row=r, column=c, padx=5, pady=5)
            self.buttons.append(btn)

        self.lbl_status = tk.Label(left_frame, text="Lượt chơi: Người (X)", font=("Segoe UI", 12, "bold"), fg="#7f8c8d")
        self.lbl_status.pack(pady=15)

        tk.Label(right_frame, text="Cấu Hình Trò Chơi", font=("Segoe UI", 14, "bold"), fg="#2c3e50").pack(pady=(0, 15))

        tk.Label(right_frame, text="Chế độ chơi:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.mode_var = tk.StringVar(value="Human vs AI")
        self.mode_combo = ttk.Combobox(right_frame, textvariable=self.mode_var, values=["Human vs AI", "AI vs AI"], state="readonly")
        self.mode_combo.pack(fill=tk.X, pady=(0, 15))
        self.mode_combo.bind("<<ComboboxSelected>>", self.on_mode_changed)

        tk.Label(right_frame, text="Thuật toán AI (O):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.algo_var = tk.StringVar(value="Alpha-Beta Pruning")
        self.algo_combo = ttk.Combobox(right_frame, textvariable=self.algo_var, values=["Minimax", "Alpha-Beta Pruning", "Expectimax"], state="readonly")
        self.algo_combo.pack(fill=tk.X, pady=(0, 15))

        self.btn_reset = ttk.Button(right_frame, text="Chơi lại / Reset", command=self.reset_game)
        self.btn_reset.pack(fill=tk.X, pady=5)

        log_label_frame = ttk.LabelFrame(right_frame, text=" Nhật ký tính toán AI ", padding=10)
        log_label_frame.pack(fill=tk.BOTH, expand=True, pady=15)

        self.log_text = tk.Text(log_label_frame, wrap=tk.WORD, bg="#ffffff", fg="#000000", font=("Consolas", 9), state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_label_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def write_log(self, text, clear=False):
        self.log_text.config(state=tk.NORMAL)
        if clear:
            self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_cell_click(self, index):
        if self.game_over or self.board[index] != ' ' or self.mode_var.get() == "AI vs AI":
            return

        self.make_move(index, 'X')
        if not self.check_game_end():
            self.current_player = 'O'
            self.lbl_status.config(text="Lượt chơi: AI (O)...")
            self.root.after(500, self.ai_move)

    def on_mode_changed(self, event=None):
        self.reset_game()
        if self.mode_var.get() == "AI vs AI":
            self.lbl_status.config(text="Chế độ AI vs AI. Nhấn chơi lại để bắt đầu.")
            self.root.after(500, self.ai_vs_ai_loop)

    def make_move(self, index, player):
        self.board[index] = player
        color = "#e74c3c" if player == 'X' else "#3498db"
        self.buttons[index].config(text=player, fg=color, disabledforeground=color, state=tk.DISABLED)

    def ai_move(self):
        if self.game_over:
            return

        algo = self.algo_var.get()
        start_time = time.time()

        if algo == "Minimax":
            move, nodes = find_best_move_minimax(self.board, 'O')
            prunes = None
        elif algo == "Alpha-Beta Pruning":
            move, nodes, prunes = find_best_move_alphabeta(self.board, 'O')
        else:
            move, nodes = find_best_move_expectimax(self.board, 'O', p=0.7)
            prunes = None

        elapsed = time.time() - start_time

        log_msg = f"AI ({algo}):\n"
        log_msg += f"  - Ô chọn: {move} ({move // 3}, {move % 3})\n"
        log_msg += f"  - Node duyệt: {nodes}\n"
        if prunes is not None:
            log_msg += f"  - Cắt tỉa: {prunes} lần\n"
        log_msg += f"  - Thời gian: {elapsed:.5f} s\n"
        self.write_log(log_msg)

        if move != -1:
            self.make_move(move, 'O')

        if not self.check_game_end():
            self.current_player = 'X'
            if self.mode_var.get() == "Human vs AI":
                self.lbl_status.config(text="Lượt chơi: Người (X)")
            else:
                self.root.after(800, self.ai_vs_ai_loop)

    def ai_vs_ai_loop(self):
        if self.game_over or self.mode_var.get() != "AI vs AI":
            return

        if self.current_player == 'X':
            empty_spots = [i for i in range(9) if self.board[i] == ' ']
            if empty_spots:
                move, _ = find_best_move_minimax(self.board, 'X')
                self.make_move(move, 'X')
                self.write_log(f"AI (X) đi ô: {move}")
            if not self.check_game_end():
                self.current_player = 'O'
                self.lbl_status.config(text="Lượt chơi: AI (O)...")
                self.root.after(800, self.ai_move)
        else:
            self.ai_move()

    def check_game_end(self):
        from algorithms.minimax import is_win, is_draw
        if is_win(self.board, 'X'):
            self.lbl_status.config(text="NGƯỜI (X) THẮNG!", fg="#e74c3c")
            self.game_over = True
            messagebox.showinfo("Kết quả", "Người (X) Thắng!")
            return True
        elif is_win(self.board, 'O'):
            self.lbl_status.config(text="AI (O) THẮNG!", fg="#3498db")
            self.game_over = True
            messagebox.showinfo("Kết quả", "AI (O) Thắng!")
            return True
        elif is_draw(self.board):
            self.lbl_status.config(text="HÒA!", fg="#7f8c8d")
            self.game_over = True
            messagebox.showinfo("Kết quả", "Hòa!")
            return True
        return False

    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        self.game_over = False
        self.current_player = 'X'
        self.write_log("Trận đấu mới bắt đầu.", clear=True)

        for btn in self.buttons:
            btn.config(text=" ", state=tk.NORMAL, bg="#ffffff")

        if self.mode_var.get() == "Human vs AI":
            self.lbl_status.config(text="Lượt chơi: Người (X)", fg="#7f8c8d")
        else:
            self.lbl_status.config(text="AI vs AI đang chạy...", fg="#7f8c8d")
            self.root.after(500, self.ai_vs_ai_loop)
