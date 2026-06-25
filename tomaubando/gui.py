import tkinter as tk
from tkinter import ttk, messagebox
import time
from algorithms import (
    solve_backtracking, solve_backtracking_stepwise,
    solve_forward_checking, solve_forward_checking_stepwise,
    solve_ac3, solve_ac3_stepwise,
    solve_min_conflicts, solve_min_conflicts_stepwise
)

districts = [
    "Quận 1", "Quận 3", "Quận 4", "Quận 5", "Quận 6", "Quận 7", "Quận 8",
    "Quận 10", "Quận 11", "Quận 12", "Bình Tân", "Bình Thạnh", "Phú Nhuận",
    "Gò Vấp", "Tân Bình", "Tân Phú", "Thủ Đức", "Nhà Bè", "Bình Chánh",
    "Hóc Môn", "Củ Chi", "Cần Giờ"
]

neighbors = {
    "Quận 1": ["Quận 3", "Quận 4", "Quận 5", "Bình Thạnh", "Thủ Đức"],
    "Quận 3": ["Quận 1", "Quận 10", "Phú Nhuận"],
    "Quận 4": ["Quận 1", "Quận 7", "Thủ Đức"],
    "Quận 5": ["Quận 1", "Quận 6", "Quận 8", "Quận 10", "Quận 11"],
    "Quận 6": ["Quận 5", "Quận 8", "Quận 11", "Bình Tân", "Tân Phú"],
    "Quận 7": ["Quận 4", "Quận 8", "Nhà Bè", "Bình Chánh", "Thủ Đức"],
    "Quận 8": ["Quận 5", "Quận 6", "Quận 7", "Bình Chánh"],
    "Quận 10": ["Quận 3", "Quận 5", "Quận 11", "Tân Bình"],
    "Quận 11": ["Quận 5", "Quận 6", "Quận 10", "Tân Bình", "Tân Phú"],
    "Quận 12": ["Hóc Môn", "Gò Vấp", "Bình Thạnh", "Thủ Đức", "Tân Bình", "Tân Phú", "Bình Tân"],
    "Bình Tân": ["Quận 6", "Tân Phú", "Quận 12", "Bình Chánh"],
    "Bình Thạnh": ["Quận 1", "Quận 12", "Phú Nhuận", "Gò Vấp", "Thủ Đức"],
    "Phú Nhuận": ["Quận 3", "Quận 1", "Bình Thạnh", "Gò Vấp", "Tân Bình"],
    "Gò Vấp": ["Quận 12", "Bình Thạnh", "Phú Nhuận", "Tân Bình"],
    "Tân Bình": ["Quận 10", "Quận 11", "Quận 12", "Phú Nhuận", "Gò Vấp", "Tân Phú"],
    "Tân Phú": ["Quận 6", "Quận 11", "Quận 12", "Tân Bình", "Bình Tân"],
    "Thủ Đức": ["Quận 1", "Quận 4", "Quận 7", "Bình Thạnh", "Quận 12"],
    "Nhà Bè": ["Quận 7", "Bình Chánh", "Cần Giờ"],
    "Bình Chánh": ["Quận 7", "Quận 8", "Quận 6", "Bình Tân", "Nhà Bè", "Hóc Môn"],
    "Hóc Môn": ["Củ Chi", "Quận 12", "Bình Chánh"],
    "Củ Chi": ["Hóc Môn"],
    "Cần Giờ": ["Nhà Bè"]
}

coordinates = {
    "Củ Chi": (150, 70),
    "Hóc Môn": (220, 140),
    "Quận 12": (280, 200),
    "Gò Vấp": (360, 210),
    "Bình Thạnh": (450, 250),
    "Thủ Đức": (530, 200),
    "Phú Nhuận": (380, 270),
    "Tân Bình": (300, 280),
    "Tân Phú": (230, 290),
    "Bình Tân": (170, 360),
    "Quận 3": (380, 330),
    "Quận 10": (320, 340),
    "Quận 11": (270, 350),
    "Quận 1": (430, 350),
    "Quận 4": (440, 400),
    "Quận 5": (310, 400),
    "Quận 6": (250, 410),
    "Quận 8": (280, 480),
    "Quận 7": (480, 470),
    "Bình Chánh": (130, 450),
    "Nhà Bè": (500, 560),
    "Cần Giờ": (580, 650)
}

colors = ["Đỏ", "Xanh lá", "Xanh dương", "Vàng"]

color_hex = {
    "Đỏ": "#ff4d4d",
    "Xanh lá": "#2ecc71",
    "Xanh dương": "#3498db",
    "Vàng": "#f1c40f"
}

class ColoringGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tô màu bản đồ TP.HCM - CSP Solver")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        self.current_assignment = {}
        self.current_domains = {var: list(colors) for var in districts}
        self.current_var = None
        self.animation_gen = None
        self.is_playing = False
        self.speed = 300
        self.highlight_nodes = []

        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(left_frame, bg="#f8f9fa", width=680, height=720, relief="solid", bd=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(self.root, padding=10, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_frame.pack_propagate(False)

        tk.Label(right_frame, text="Tô Màu Bản Đồ TP.HCM (CSP)", font=("Segoe UI", 12, "bold")).pack(pady=5)

        info_frame = ttk.LabelFrame(right_frame, text=" So sánh Hiệu năng ", padding=10)
        info_frame.pack(fill=tk.X, pady=5)

        self.lbl_bt = tk.Label(info_frame, text="1. Backtracking:\n  Gán: ---  |  Quay lui: ---  |  Time: ---", justify=tk.LEFT, anchor="w", font=("Segoe UI", 9))
        self.lbl_bt.pack(fill=tk.X, pady=2)

        self.lbl_fc = tk.Label(info_frame, text="2. Forward Checking:\n  Gán: ---  |  Quay lui: ---  |  Time: ---", justify=tk.LEFT, anchor="w", font=("Segoe UI", 9))
        self.lbl_fc.pack(fill=tk.X, pady=2)

        self.lbl_ac3 = tk.Label(info_frame, text="3. AC-3 + MAC:\n  Gán: ---  |  Quay lui: ---  |  Time: ---", justify=tk.LEFT, anchor="w", font=("Segoe UI", 9))
        self.lbl_ac3.pack(fill=tk.X, pady=2)

        self.lbl_mc = tk.Label(info_frame, text="4. Min-Conflicts:\n  Gán: ---  |  Sửa: ---  |  Time: ---", justify=tk.LEFT, anchor="w", font=("Segoe UI", 9))
        self.lbl_mc.pack(fill=tk.X, pady=2)

        ctrl_frame = ttk.LabelFrame(right_frame, text=" Điều khiển mô phỏng ", padding=10)
        ctrl_frame.pack(fill=tk.X, pady=5)

        fast_btn_frame = ttk.Frame(ctrl_frame)
        fast_btn_frame.pack(fill=tk.X, pady=2)

        ttk.Button(fast_btn_frame, text="Giải nhanh", command=self.run_all_fast).pack(fill=tk.X)

        ttk.Separator(ctrl_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        tk.Label(ctrl_frame, text="Chọn thuật toán mô phỏng:").pack(anchor="w")
        self.algo_var = tk.StringVar(value="Backtracking")
        self.algo_combo = ttk.Combobox(ctrl_frame, textvariable=self.algo_var, values=["Backtracking", "Forward Checking", "AC-3 + MAC", "Min-Conflicts"], state="readonly")
        self.algo_combo.pack(fill=tk.X, pady=2)

        step_btn_frame = ttk.Frame(ctrl_frame)
        step_btn_frame.pack(fill=tk.X, pady=5)

        self.btn_step = ttk.Button(step_btn_frame, text="Mô phỏng từng bước", command=self.start_step_simulation)
        self.btn_step.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.btn_stop = ttk.Button(step_btn_frame, text="Dừng / Xóa", command=self.stop_and_clear)
        self.btn_stop.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        speed_frame = ttk.Frame(ctrl_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        tk.Label(speed_frame, text="Tốc độ:").pack(side=tk.LEFT)
        self.slider_speed = ttk.Scale(speed_frame, from_=50, to=1500, value=300, orient=tk.HORIZONTAL, command=self.update_speed)
        self.slider_speed.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        log_label_frame = ttk.LabelFrame(right_frame, text=" Nhật ký gán nhãn từng bước ", padding=10)
        log_label_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(log_label_frame, wrap=tk.WORD, bg="#ffffff", fg="#000000", font=("Consolas", 9), state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_label_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.draw_graph()

    def update_speed(self, val):
        self.speed = int(float(val))

    def write_log(self, text, clear=False):
        self.log_text.config(state=tk.NORMAL)
        if clear:
            self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def draw_graph(self):
        self.canvas.delete("all")

        for node, adjs in neighbors.items():
            if node in coordinates:
                x1, y1 = coordinates[node]
                for adj in adjs:
                    if adj in coordinates:
                        x2, y2 = coordinates[adj]
                        self.canvas.create_line(x1, y1, x2, y2, fill="#bdc3c7", width=1.5, dash=(4, 4))

        r = 18
        for node, (x, y) in coordinates.items():
            color = self.current_assignment.get(node, None)
            fill_color = color_hex.get(color, "#ffffff")

            if node == self.current_var:
                outline_color = "#e74c3c"
                outline_width = 4
            elif node in self.highlight_nodes:
                outline_color = "#f39c12"
                outline_width = 3
            else:
                outline_color = "#34495e" if color else "#7f8c8d"
                outline_width = 3 if color else 1.5

            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill_color, outline=outline_color, width=outline_width)

            domain_size = len(self.current_domains.get(node, []))
            lbl_text = f"{node}\n(D:{domain_size})" if not color else node

            self.canvas.create_text(x, y + r + 13, text=lbl_text, font=("Segoe UI", 8, "bold"), fill="#2c3e50", justify=tk.CENTER)

    def run_all_fast(self):
        self.stop_and_clear()

        s1, a1, m1 = solve_backtracking(districts, neighbors, colors)
        if s1:
            self.lbl_bt.config(text=f"1. Backtracking:\n  Gán: {m1.assignments}  |  Quay lui: {m1.backtracks}  |  Time: {m1.end_time - m1.start_time:.5f} s")

        s2, a2, m2 = solve_forward_checking(districts, neighbors, colors)
        if s2:
            self.lbl_fc.config(text=f"2. Forward Checking:\n  Gán: {m2.assignments}  |  Quay lui: {m2.backtracks}  |  Time: {m2.end_time - m2.start_time:.5f} s")

        s3, a3, m3 = solve_ac3(districts, neighbors, colors)
        if s3:
            self.lbl_ac3.config(text=f"3. AC-3 + MAC:\n  Gán: {m3.assignments}  |  Quay lui: {m3.backtracks}  |  Time: {m3.end_time - m3.start_time:.5f} s")

        s4, a4, m4 = solve_min_conflicts(districts, neighbors, colors)
        if s4:
            self.lbl_mc.config(text=f"4. Min-Conflicts:\n  Gán màu: {m4.assignments}  |  Thời gian: {m4.end_time - m4.start_time:.5f} s")

        if s1:
            self.current_assignment = a1
            self.draw_graph()
            self.write_log("Đã giải nhanh thành công tất cả thuật toán để so sánh. Hiển thị lời giải của Backtracking thuần túy.", clear=True)

    def stop_and_clear(self):
        self.is_playing = False
        self.current_assignment = {}
        self.current_domains = {var: list(colors) for var in districts}
        self.current_var = None
        self.highlight_nodes = []
        self.draw_graph()
        self.write_log("Đã dừng và xóa cấu hình màu.", clear=True)

    def start_step_simulation(self):
        self.stop_and_clear()
        self.is_playing = True

        algo = self.algo_var.get()
        self.write_log(f"BẮT ĐẦU MÔ PHỎNG: {algo.upper()}...", clear=True)

        if algo == "Backtracking":
            self.animation_gen = solve_backtracking_stepwise(districts, neighbors, colors)
        elif algo == "Forward Checking":
            self.animation_gen = solve_forward_checking_stepwise(districts, neighbors, colors)
        elif algo == "AC-3 + MAC":
            self.animation_gen = solve_ac3_stepwise(districts, neighbors, colors)
        elif algo == "Min-Conflicts":
            self.animation_gen = solve_min_conflicts_stepwise(districts, neighbors, colors)

        self.animate_next_step()

    def animate_next_step(self):
        if not self.is_playing:
            return
        try:
            step = next(self.animation_gen)
            self.current_assignment = step.get("assignment", {})
            self.current_domains = step.get("domains", {var: list(colors) for var in districts})
            self.current_var = step.get("var", None)

            if self.algo_var.get() == "Min-Conflicts" and self.current_var:
                self.highlight_nodes = [nb for nb in neighbors.get(self.current_var, []) if self.current_assignment.get(nb) == step.get("color")]
            else:
                self.highlight_nodes = []

            self.draw_graph()

            action = step.get("action", "")
            log_msg = step.get("log", None)

            if not log_msg:
                var = step.get("var")
                col = step.get("color")
                metrics = step.get("metrics")
                if action == "try":
                    log_msg = f"Thử gán '{var}' = {col}..."
                elif action == "assign":
                    log_msg = f"-> GÁN THÀNH CÔNG: '{var}' = {col}"
                elif action == "fail_constraint":
                    log_msg = f"  -> Thất bại: Xung đột màu với láng giềng kề của {var}."
                elif action == "fail_fc":
                    log_msg = f"  -> Thất bại: Forward Checking phát hiện miền giá trị quận kề bị rỗng!"
                elif action == "fail_mac":
                    log_msg = f"  -> Thất bại: AC-3 phát hiện vi phạm tính nhất quán cung!"
                elif action == "backtrack":
                    log_msg = f"<- QUAY LUI (Backtrack) từ {var}."
                elif action == "success":
                    log_msg = f"== GIẢI THÀNH CÔNG! =="

            if log_msg:
                self.write_log(log_msg)

            self.root.after(self.speed, self.animate_next_step)
        except StopIteration:
            self.is_playing = False
            self.write_log("== MÔ PHỎNG HOÀN TẤT ==")
