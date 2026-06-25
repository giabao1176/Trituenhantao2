import tkinter as tk
from tkinter import ttk, messagebox
import random
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
from algorithms import solve_vacuum, solve_vacuum_stepwise, solve_and_or, solve_partially_observable

class RobotVacuumGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Hút Bụi - BFS/DFS/IDS/UCS/Greedy/A*/IDA*/Hill Climbing/Random Restart Hill/Local Beam/Simulated Annealing")
        self.root.geometry("1100x700")

        self.M = 8
        self.N = 8
        self.grid = [[0 for _ in range(self.N)] for _ in range(self.M)]
        self.robot_pos = (3, 7)

        dirty_cells = [(0,2),(1,6),(2,4),(3,1),(4,7),(5,2),(6,3),(7,5)]
        for (r, c) in dirty_cells:
            self.grid[r][c] = 1

        obstacle_cells = [(1,1),(2,6),(4,2),(6,5),(7,3)]
        for (r, c) in obstacle_cells:
            self.grid[r][c] = -1

        rr, rc = self.robot_pos
        if self.grid[rr][rc] == 1:
            self.grid[rr][rc] = 0

        self.initial_state = (self.robot_pos, [row[:] for row in self.grid])

        self.running = False
        self.solver_gen = None

        self.create_widgets()
        self.draw_grid()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(left_panel, bg="#ffffff", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.canvas.bind("<Configure>", lambda e: self.draw_grid())
        self.canvas.bind("<Button-1>", self.on_canvas_left_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)

        ctrl_frame = ttk.Frame(left_panel)
        ctrl_frame.pack(fill=tk.X, pady=5)

        tk.Label(ctrl_frame, text="Nhóm:").grid(row=0, column=0, sticky="w", padx=2)
        self.group_var = tk.StringVar(value="Có trạng thái ban đầu")
        self.group_combo = ttk.Combobox(ctrl_frame, textvariable=self.group_var, values=["Có trạng thái ban đầu", "Không trạng thái ban đầu"], state="readonly", width=22)
        self.group_combo.grid(row=0, column=1, sticky="w", padx=2)

        tk.Label(ctrl_frame, text="Thuật toán:").grid(row=0, column=2, sticky="w", padx=10)
        self.algo_var = tk.StringVar(value="BFS")
        self.algo_combo = ttk.Combobox(ctrl_frame, textvariable=self.algo_var, values=["BFS", "DFS", "IDS", "UCS", "Greedy", "A*", "IDA*", "Hill Climbing", "Random Restart Hill", "Local Beam Search", "Simulated Annealing"], state="readonly", width=16)
        self.algo_combo.grid(row=0, column=3, sticky="w", padx=2)
        self.algo_combo.bind("<<ComboboxSelected>>", self.on_algo_changed)

        tk.Label(ctrl_frame, text="Kiểu:").grid(row=0, column=4, sticky="w", padx=10)
        self.style_var = tk.StringVar(value="Style 2")
        self.style_combo = ttk.Combobox(ctrl_frame, textvariable=self.style_var, values=["Style 1", "Style 2"], state="readonly", width=12)
        self.style_combo.grid(row=0, column=5, sticky="w", padx=2)

        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=5)

        self.btn_run = ttk.Button(btn_frame, text="Chạy", command=self.start_current_tab)
        self.btn_run.pack(side=tk.LEFT, padx=2)

        self.btn_stop = ttk.Button(btn_frame, text="Dừng", command=self.stop_solving, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=2)

        self.btn_random = ttk.Button(btn_frame, text="Ngẫu nhiên", command=self.randomize_grid)
        self.btn_random.pack(side=tk.LEFT, padx=2)

        lbl_info = tk.Label(btn_frame, text="Trái-Click đổi ô, Phải-Click đặt Robot", font=("Segoe UI", 8), fg="#777777")
        lbl_info.pack(side=tk.RIGHT, padx=5)

        legend_frame = ttk.LabelFrame(left_panel, text=" Chú thích giao diện & Thuật toán ")
        legend_frame.pack(fill=tk.X, pady=5, padx=2)

        legend_text = (
            "• Máy hút bụi: Vị trí Robot hút bụi hiện tại\n"
            "• Vật cản: Chướng ngại vật robot không thể đi qua\n"
            "• Bụi(Ngôi sao): Các điểm bẩn cần làm sạch\n"
            "• Style 1: Kiểm tra Goal khi lấy trạng thái NODE con ra khỏi Frontier\n"
            "• Style 2: Kiểm tra Goal ngay khi sinh trạng thái NODE con (thường nhanh hơn)\n"
            "• Đơn giản/Dốc nhất/Ngẫu nhiên: Các kiểu leo đồi (Hill Climbing & Random Restart Hill)\n"
            "• AND-OR Search: Tìm kế hoạch có điều kiện cho môi trường không đơn định (Tab 3)"
        )
        tk.Label(legend_frame, text=legend_text, justify=tk.LEFT, anchor="w", font=("Segoe UI", 9), fg="#333333").pack(fill=tk.X, padx=5, pady=5)

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        tab_auto = ttk.Frame(self.notebook)
        self.notebook.add(tab_auto, text="Tự động (giải trước)")

        tk.Label(tab_auto, text="Nhật ký - Giải hoàn tất rồi robot chạy", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 5))

        auto_log_frame = ttk.Frame(tab_auto)
        auto_log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_auto = tk.Text(
            auto_log_frame, wrap=tk.WORD, bg="#ffffff", fg="#000000",
            relief="sunken", font=("Consolas", 10), state=tk.DISABLED, width=50
        )
        self.log_auto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb_auto = ttk.Scrollbar(auto_log_frame, orient=tk.VERTICAL, command=self.log_auto.yview)
        sb_auto.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_auto.config(yscrollcommand=sb_auto.set)

        tab_step = ttk.Frame(self.notebook)
        self.notebook.add(tab_step, text="Từng bước (real-time)")

        tk.Label(tab_step, text="Nhật ký - Robot duyệt từng bước liên tục", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 5))

        step_log_frame = ttk.Frame(tab_step)
        step_log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_step = tk.Text(
            step_log_frame, wrap=tk.WORD, bg="#ffffff", fg="#000000",
            relief="sunken", font=("Consolas", 10), state=tk.DISABLED, width=50
        )
        self.log_step.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb_step = ttk.Scrollbar(step_log_frame, orient=tk.VERTICAL, command=self.log_step.yview)
        sb_step.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_step.config(yscrollcommand=sb_step.set)

        tab_and_or = ttk.Frame(self.notebook)
        self.notebook.add(tab_and_or, text="AND-OR Search (Không đơn định)")

        tk.Label(tab_and_or, text="Nhật ký - AND-OR Graph Search & Mô phỏng", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 5))

        and_or_log_frame = ttk.Frame(tab_and_or)
        and_or_log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_and_or = tk.Text(
            and_or_log_frame, wrap=tk.WORD, bg="#ffffff", fg="#000000",
            relief="sunken", font=("Consolas", 10), state=tk.DISABLED, width=50
        )
        self.log_and_or.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb_and_or = ttk.Scrollbar(and_or_log_frame, orient=tk.VERTICAL, command=self.log_and_or.yview)
        sb_and_or.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_and_or.config(yscrollcommand=sb_and_or.set)

        tab_partially = ttk.Frame(self.notebook)
        self.notebook.add(tab_partially, text="Partially Observable (Quan sát một phần)")

        tk.Label(tab_partially, text="Nhật ký - Partially Observable Search & Mô phỏng", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 5))

        partially_log_frame = ttk.Frame(tab_partially)
        partially_log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_partially = tk.Text(
            partially_log_frame, wrap=tk.WORD, bg="#ffffff", fg="#000000",
            relief="sunken", font=("Consolas", 10), state=tk.DISABLED, width=50
        )
        self.log_partially.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb_partially = ttk.Scrollbar(partially_log_frame, orient=tk.VERTICAL, command=self.log_partially.yview)
        sb_partially.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_partially.config(yscrollcommand=sb_partially.set)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_algo_changed(self, event=None):
        algo = self.algo_var.get()
        if algo in ["Hill Climbing", "Random Restart Hill"]:
            self.style_combo.config(values=["Đơn giản", "Dốc nhất", "Ngẫu nhiên"])
            self.style_var.set("Đơn giản")
        elif algo == "Local Beam Search":
            self.style_combo.config(values=["k = 2", "k = 3", "k = 4"])
            self.style_var.set("k = 3")
        elif algo == "Simulated Annealing":
            self.style_combo.config(values=["Tuyến tính", "Mũ"])
            self.style_var.set("Mũ")
        else:
            self.style_combo.config(values=["Style 1", "Style 2"])
            if self.style_var.get() not in ["Style 1", "Style 2"]:
                self.style_var.set("Style 2")

    def write_log(self, widget, text, clear=False):
        widget.config(state=tk.NORMAL)
        if clear:
            widget.delete("1.0", tk.END)
        widget.insert(tk.END, text + "\n")

        num_lines = int(widget.index('end-1c').split('.')[0])
        if num_lines > 200:
            widget.delete("1.0", f"{num_lines - 200}.0")

        widget.see(tk.END)
        widget.config(state=tk.DISABLED)

    def load_and_resize_images(self, w, h):
        import os
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

        paths = {
            "floor":    os.path.join(base_dir, "sàn.png"),
            "robot":    os.path.join(base_dir, "computer.png"),
            "dirt":     os.path.join(base_dir, "bụi.png"),
            "obstacle": os.path.join(base_dir, "vatcan.png"),
        }

        self.tk_images = {}
        pad = max(6, min(w, h) // 8)
        inner_w = max(1, w - pad * 2)
        inner_h = max(1, h - pad * 2)

        sizes = {
            "floor":    (w, h),
            "obstacle": (w, h),
            "dirt":     (inner_w, inner_h),
            "robot":    (inner_w, inner_h),
        }

        for key, path in paths.items():
            sw, sh = sizes[key]
            if HAS_PIL:
                try:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((sw, sh), Image.Resampling.LANCZOS)
                    self.tk_images[key] = ImageTk.PhotoImage(img)
                except Exception:
                    self.tk_images[key] = None
            else:
                try:
                    self.tk_images[key] = tk.PhotoImage(file=path)
                except Exception:
                    self.tk_images[key] = None

        self._img_pad = pad

    def draw_grid(self):
        if not self.canvas.winfo_width() or not self.canvas.winfo_height():
            return

        self.canvas.delete("all")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        self.cell_w = cw / self.N
        self.cell_h = ch / self.M

        cell_size = (int(self.cell_w), int(self.cell_h))
        if not hasattr(self, '_cached_cell_size') or self._cached_cell_size != cell_size:
            self._cached_cell_size = cell_size
            self.load_and_resize_images(cell_size[0], cell_size[1])

        for r in range(self.M):
            for c in range(self.N):
                x1 = c * self.cell_w
                y1 = r * self.cell_h
                x2 = x1 + self.cell_w
                y2 = y1 + self.cell_h
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                val = self.grid[r][c]

                if self.tk_images.get("floor"):
                    self.canvas.create_image(x1, y1, image=self.tk_images["floor"], anchor="nw")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#e8dcc8", outline="#ccc", width=1)

                if val == -1:
                    if self.tk_images.get("obstacle"):
                        self.canvas.create_image(x1, y1, image=self.tk_images["obstacle"], anchor="nw")
                    else:
                        self.canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill="#7f8c8d", outline="#555")

                elif val == 1:
                    if self.tk_images.get("dirt"):
                        self.canvas.create_image(cx, cy, image=self.tk_images["dirt"], anchor="center")
                    else:
                        r_blob = min(self.cell_w, self.cell_h) * 0.25
                        self.canvas.create_oval(cx-r_blob, cy-r_blob, cx+r_blob, cy+r_blob, fill="#d35400", outline="")

        robot_positions = list(self.robot_pos) if isinstance(self.robot_pos, (set, list, frozenset)) else [self.robot_pos]
        for r_robot, c_robot in robot_positions:
            rx1 = c_robot * self.cell_w
            ry1 = r_robot * self.cell_h
            rcx = rx1 + self.cell_w / 2
            rcy = ry1 + self.cell_h / 2

            if self.tk_images.get("robot"):
                self.canvas.create_image(rcx, rcy, image=self.tk_images["robot"], anchor="center")
            else:
                rx1_f = rx1 + self.cell_w * 0.15
                ry1_f = ry1 + self.cell_h * 0.15
                rx2_f = rx1 + self.cell_w * 0.85
                ry2_f = ry1 + self.cell_h * 0.85
                self.canvas.create_oval(rx1_f, ry1_f, rx2_f, ry2_f, fill="#2980b9", outline="#1a5276", width=2)
                self.canvas.create_oval(rcx-3, rcy-3, rcx+3, rcy+3, fill="#ffffff", outline="")

    def on_canvas_left_click(self, event):
        if self.running:
            return
        c = int(event.x // self.cell_w)
        r = int(event.y // self.cell_h)
        if 0 <= r < self.M and 0 <= c < self.N:
            if (r, c) != self.robot_pos:
                curr = self.grid[r][c]
                if curr == 0:
                    self.grid[r][c] = -1
                elif curr == -1:
                    self.grid[r][c] = 1
                else:
                    self.grid[r][c] = 0
                self.initial_state = (self.robot_pos, [row[:] for row in self.grid])
                self.draw_grid()

    def on_canvas_right_click(self, event):
        if self.running:
            return
        c = int(event.x // self.cell_w)
        r = int(event.y // self.cell_h)
        if 0 <= r < self.M and 0 <= c < self.N:
            if self.grid[r][c] != -1:
                self.robot_pos = (r, c)
                self.initial_state = (self.robot_pos, [row[:] for row in self.grid])
                self.draw_grid()

    def randomize_grid(self):
        if self.running:
            return
        self.grid = [[0 for _ in range(self.N)] for _ in range(self.M)]
        self.robot_pos = (random.randint(0, self.M - 1), random.randint(0, self.N - 1))

        for _ in range(5):
            r = random.randint(0, self.M - 1)
            c = random.randint(0, self.N - 1)
            if (r, c) != self.robot_pos:
                self.grid[r][c] = -1

        for _ in range(8):
            r = random.randint(0, self.M - 1)
            c = random.randint(0, self.N - 1)
            if (r, c) != self.robot_pos and self.grid[r][c] == 0:
                self.grid[r][c] = 1

        self.initial_state = (self.robot_pos, [row[:] for row in self.grid])
        self.draw_grid()
        self.write_log(self.log_auto, "Đã ngẫu nhiên bản đồ.", clear=True)
        self.write_log(self.log_step, "Đã ngẫu nhiên bản đồ.", clear=True)
        if hasattr(self, 'log_and_or'):
            self.write_log(self.log_and_or, "Đã ngẫu nhiên bản đồ.", clear=True)

    def _get_search_params(self):
        r_start, c_start = self.initial_state[0]
        self.robot_pos = (r_start, c_start)
        self.grid = [row[:] for row in self.initial_state[1]]
        self.draw_grid()

        initial_dirty = set()
        obstacles = set()
        for r in range(self.M):
            for c in range(self.N):
                if self.grid[r][c] == 1:
                    initial_dirty.add((r, c))
                elif self.grid[r][c] == -1:
                    obstacles.add((r, c))

        if (r_start, c_start) in initial_dirty:
            initial_dirty.remove((r_start, c_start))

        algo = self.algo_var.get()
        style_str = self.style_var.get()
        if algo in ["Hill Climbing", "Random Restart Hill"]:
            if style_str == "Đơn giản":
                style = 1
            elif style_str == "Dốc nhất":
                style = 2
            else:
                style = 3
        elif algo == "Local Beam Search":
            if style_str == "k = 2":
                style = 2
            elif style_str == "k = 4":
                style = 4
            else:
                style = 3
        elif algo == "Simulated Annealing":
            if style_str == "Tuyến tính":
                style = 1
            else:
                style = 2
        else:
            style = 1 if "Style 1" in style_str else 2
        sensorless = (self.group_var.get() == "Không trạng thái ban đầu")
        return r_start, c_start, initial_dirty, obstacles, algo, style, style_str, sensorless

    def _lock_controls(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.btn_random.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.algo_combo.config(state=tk.DISABLED)
        self.style_combo.config(state=tk.DISABLED)
        self.group_combo.config(state=tk.DISABLED)

    def start_current_tab(self):
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:
            self.start_auto_mode()
        elif current_tab == 1:
            self.start_step_mode()
        elif current_tab == 2:
            self.start_and_or_mode()
        elif current_tab == 3:
            self.start_partially_mode()

    def start_auto_mode(self):
        self._lock_controls()
        r_start, c_start, initial_dirty, obstacles, algo, style, style_str, sensorless = self._get_search_params()

        self.write_log(self.log_auto, f"Bắt đầu giải bằng {algo} ({style_str})...", clear=True)

        result = solve_vacuum(
            self.M, self.N, (r_start, c_start), initial_dirty, obstacles, algo, style, sensorless=sensorless
        )

        if sensorless and result["found"]:
            path = [(r_start, c_start)]
            curr_pos = (r_start, c_start)
            directions_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
            for step_dir in result["directions"]:
                dr, dc = directions_map.get(step_dir, (0, 0))
                nr, nc = curr_pos[0] + dr, curr_pos[1] + dc
                if 0 <= nr < self.M and 0 <= nc < self.N and (nr, nc) not in obstacles:
                    curr_pos = (nr, nc)
                path.append(curr_pos)
            result["path"] = path

        if result["found"]:
            self.write_log(self.log_auto, f"Tổng node đã sinh: {result['nodes_gen']}")
            self.write_log(self.log_auto, f"Tổng node đã duyệt: {result['nodes_exp']}")
            self.write_log(self.log_auto, "==== QUÁ TRÌNH DUYỆT ====")
            if len(result["exploration_log"]) > 200:
                for log_line in result["exploration_log"][:50]:
                    self.write_log(self.log_auto, log_line)
                self.write_log(self.log_auto, "\n... [ĐÃ ẨN ĐI CÁC BƯỚC Ở GIỮA VÌ QUÁ DÀI] ...\n")
                for log_line in result["exploration_log"][-50:]:
                    self.write_log(self.log_auto, log_line)
            else:
                for log_line in result["exploration_log"]:
                    self.write_log(self.log_auto, log_line)

            self.write_log(self.log_auto, "==== ĐƯỜNG ĐI TỐI ƯU ====")
            if result["directions"]:
                self.write_log(self.log_auto, " -> ".join(result["directions"]))
            else:
                self.write_log(self.log_auto, "Đã đứng tại đích ngay từ đầu.")
            self.solution_path = result["path"]
            self.solution_dirs = result["directions"]
            self.anim_step = 0
            self.animate_path()
        else:
            self.write_log(self.log_auto, "Không thể tìm thấy đường đi.")
            self.reset_controls()

    def animate_path(self):
        if not self.running:
            return

        if self.anim_step >= len(self.solution_path):
            self.running = False
            messagebox.showinfo("Hoàn tất", "Đã hoàn thành di chuyển theo đường đi!")
            self.reset_controls()
            return

        pos = self.solution_path[self.anim_step]
        self.robot_pos = pos
        if self.grid[pos[0]][pos[1]] == 1:
            self.grid[pos[0]][pos[1]] = 0

        self.draw_grid()

        if self.anim_step > 0:
            direction = self.solution_dirs[self.anim_step - 1]
            self.write_log(self.log_auto, f"Bước {self.anim_step}: Đi {direction}, vị trí hiện tại: {pos}")
        else:
            self.write_log(self.log_auto, f"Vị trí ban đầu: {pos}")

        self.anim_step += 1
        self.root.after(300, self.animate_path)

    def start_step_mode(self):
        self._lock_controls()
        r_start, c_start, initial_dirty, obstacles, algo, style, style_str, sensorless = self._get_search_params()

        self.write_log(self.log_step, f"Bắt đầu duyệt từng bước bằng {algo} ({style_str})...", clear=True)

        self.solver_gen = solve_vacuum_stepwise(
            self.M, self.N, (r_start, c_start), initial_dirty, obstacles, algo, style, sensorless=sensorless
        )
        self.explore_next_step()

    def explore_next_step(self):
        if not self.running:
            return

        BATCH = 1

        last_step = None
        for _ in range(BATCH):
            if not self.running:
                return
            try:
                step_info = next(self.solver_gen)
                last_step = step_info
                if step_info["is_goal"]:
                    break
            except StopIteration:
                self.running = False
                self.write_log(self.log_step, "Đã hoàn tất duyệt tất cả node.")
                self.reset_controls()
                return

        if last_step is None:
            return

        self.robot_pos = last_step["pos"]
        dirty = last_step["dirty"]
        init_grid = self.initial_state[1]
        for r in range(self.M):
            for c in range(self.N):
                if init_grid[r][c] == 1:
                    if (r, c) in dirty:
                        self.grid[r][c] = 1
                    else:
                        self.grid[r][c] = 0
        self.draw_grid()
        self.write_log(self.log_step, last_step["log"])

        if last_step["is_goal"]:
            self.running = False
            is_sensorless = (self.group_var.get() == "Không trạng thái ban đầu")

            if is_sensorless and last_step["directions"]:
                r_start, c_start = self.initial_state[0]
                curr_pos = (r_start, c_start)
                directions_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
                obstacles = { (r, c) for r in range(self.M) for c in range(self.N) if self.initial_state[1][r][c] == -1 }
                for step_dir in last_step["directions"]:
                    dr, dc = directions_map.get(step_dir, (0, 0))
                    nr, nc = curr_pos[0] + dr, curr_pos[1] + dc
                    if 0 <= nr < self.M and 0 <= nc < self.N and (nr, nc) not in obstacles:
                        curr_pos = (nr, nc)
                self.robot_pos = curr_pos
                self.grid = [row[:] for row in self.initial_state[1]]
                for r in range(self.M):
                    for c in range(self.N):
                        if self.grid[r][c] == 1:
                            self.grid[r][c] = 0
                self.draw_grid()

            if last_step["directions"] or (not is_sensorless and last_step["path"]):
                self.write_log(self.log_step, f"\n==== KẾT QUẢ ====")
                self.write_log(self.log_step, f"Tổng node đã sinh: {last_step['nodes_gen']}")
                self.write_log(self.log_step, f"Tổng node đã duyệt: {last_step['nodes_exp']}")
                self.write_log(self.log_step, "Đường đi: " + " -> ".join(last_step["directions"]))
                messagebox.showinfo("Hoàn tất", f"Đã tìm thấy đường đi!\nSố bước: {len(last_step['directions'])}\nNode duyệt: {last_step['nodes_exp']}")
            else:
                self.write_log(self.log_step, "Không tìm thấy đường đi!")
            self.reset_controls()
            return

        self.root.after(50, self.explore_next_step)

    def stop_solving(self):
        self.running = False
        self.write_log(self.log_auto, "\n[ĐÃ DỪNG]")
        self.write_log(self.log_step, "\n[ĐÃ DỪNG]")
        if hasattr(self, 'log_and_or'):
            self.write_log(self.log_and_or, "\n[ĐÃ DỪNG]")
        if hasattr(self, 'log_partially'):
            self.write_log(self.log_partially, "\n[ĐÃ DỪNG]")
        self.reset_controls()

    def reset_controls(self):
        self.btn_run.config(state=tk.NORMAL)
        self.btn_random.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.algo_combo.config(state="readonly")
        self.style_combo.config(state="readonly")
        self.group_combo.config(state="readonly")
        if isinstance(self.robot_pos, (set, list, frozenset)):
            self.robot_pos = self.initial_state[0]
            self.grid = [row[:] for row in self.initial_state[1]]
            self.draw_grid()

    def on_tab_changed(self, event=None):
        if not hasattr(self, 'notebook'):
            return
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab in [2, 3]:
            self.algo_combo.config(state=tk.DISABLED)
            self.style_combo.config(state=tk.DISABLED)
            self.group_combo.config(state=tk.DISABLED)
        else:
            if not self.running:
                self.algo_combo.config(state="readonly")
                self.style_combo.config(state="readonly")
                self.group_combo.config(state="readonly")

    def start_and_or_mode(self):
        self._lock_controls()
        r_start, c_start, initial_dirty, obstacles, _, _, _, _ = self._get_search_params()

        self.write_log(self.log_and_or, "Bắt đầu giải bằng AND-OR Graph Search...", clear=True)

        result = solve_and_or(self.M, self.N, (r_start, c_start), initial_dirty, obstacles)

        if result["found"]:
            self.write_log(self.log_and_or, f"Tổng node đã sinh: {result['nodes_gen']}")
            self.write_log(self.log_and_or, f"Tổng node đã duyệt: {result['nodes_exp']}")
            self.write_log(self.log_and_or, "==== QUÁ TRÌNH DUYỆT (OR NODES) ====")
            for log_line in result["exploration_log"]:
                self.write_log(self.log_and_or, log_line)

            self.write_log(self.log_and_or, "\n==== KẾ HOẠCH HÀNH ĐỘNG (CONDITIONAL PLAN) ====")
            formatted_plan = self._format_plan(result["plan"], indent=0)
            self.write_log(self.log_and_or, formatted_plan)

            self.write_log(self.log_and_or, "\n==== BẮT ĐẦU MÔ PHỎNG KHÔNG ĐƠN ĐỊNH ====")
            self.and_or_plan = result["plan"]
            self.and_or_problem = result["problem"]
            self.and_or_state = ((r_start, c_start), frozenset(initial_dirty))
            self.and_or_step = 0

            self.animate_and_or_step()
        else:
            self.write_log(self.log_and_or, "Không tìm thấy kế hoạch hành động nào hợp lệ!")
            self.reset_controls()

    def _format_plan(self, plan, indent=0):
        if plan == []:
            return " " * indent + "-> ĐẠT ĐÍCH"
        if plan is None:
            return " " * indent + "-> THẤT BẠI"

        action, plans_mapping = plan
        result_str = " " * indent + f"Hành động: {action}\n"
        for state, subplan in plans_mapping.items():
            pos, dirty = state
            result_str += " " * (indent + 2) + f"Nếu chuyển sang: {pos} (còn {len(dirty)} ô bụi):\n"
            result_str += self._format_plan(subplan, indent + 4) + "\n"
        return result_str.rstrip()

    def animate_and_or_step(self):
        if not self.running:
            return

        curr_state = self.and_or_state
        curr_plan = self.and_or_plan

        pos, dirty = curr_state

        self.robot_pos = pos
        for r in range(self.M):
            for c in range(self.N):
                if self.initial_state[1][r][c] == 1:
                    if (r, c) in dirty:
                        self.grid[r][c] = 1
                    else:
                        self.grid[r][c] = 0
        self.draw_grid()

        if len(dirty) == 0:
            self.write_log(self.log_and_or, f"\n[Hoàn tất] Đã làm sạch toàn bộ ngôi nhà sau {self.and_or_step} bước!")
            messagebox.showinfo("Hoàn tất", f"AND-OR Search hoàn thành!\nSố bước đã chạy: {self.and_or_step}")
            self.running = False
            self.reset_controls()
            return

        if curr_plan == [] or curr_plan is None:
            self.write_log(self.log_and_or, "\n[Lỗi] Kế hoạch kết thúc sớm hoặc thất bại!")
            self.running = False
            self.reset_controls()
            return

        action, plans_mapping = curr_plan
        self.and_or_step += 1

        possible_states = self.and_or_problem.results(curr_state, action)
        chosen_state = random.choice(possible_states)

        log_msg = f"Bước {self.and_or_step}: Tại {pos}, thực hiện '{action}'"
        if action == "Suck":
            if pos in dirty:
                if len(chosen_state[1]) < len(dirty) - 1:
                    cleaned_adj = (dirty - {pos}) - chosen_state[1]
                    adj_str = ", ".join(f"({r},{c})" for r, c in cleaned_adj)
                    log_msg += f"\n  -> Kết quả ngẫu nhiên: Hút sạch tại {pos} và cả ô bên cạnh: {adj_str}!"
                elif len(chosen_state[1]) == len(dirty) - 1:
                    log_msg += f"\n  -> Kết quả ngẫu nhiên: Hút sạch tại {pos}."
                else:
                    log_msg += f"\n  -> Kết quả ngẫu nhiên: Hút thất bại tại {pos}."
            else:
                if pos in chosen_state[1]:
                    log_msg += f"\n  -> Kết quả ngẫu nhiên: Làm bẩn thêm ô {pos}!"
                else:
                    log_msg += f"\n  -> Kết quả ngẫu nhiên: Không thay đổi gì."
        else:
            log_msg += f" -> Di chuyển đến {chosen_state[0]}."

        self.write_log(self.log_and_or, log_msg)

        if chosen_state in plans_mapping:
            next_plan = plans_mapping[chosen_state]
        else:
            self.write_log(self.log_and_or, f"\n[Lỗi] Không tìm thấy nhánh kế hoạch cho trạng thái: {chosen_state}!")
            self.running = False
            self.reset_controls()
            return

        self.and_or_state = chosen_state
        self.and_or_plan = next_plan

        self.root.after(800, self.animate_and_or_step)

    def start_partially_mode(self):
        self._lock_controls()
        r_start, c_start, initial_dirty, obstacles, _, _, _, _ = self._get_search_params()

        self.write_log(self.log_partially, "Bắt đầu giải bằng Partially Observable Search...", clear=True)

        result = solve_partially_observable(self.M, self.N, (r_start, c_start), initial_dirty, obstacles)

        if result["found"]:
            self.write_log(self.log_partially, f"Tổng node đã sinh: {result['nodes_gen']}")
            self.write_log(self.log_partially, f"Tổng node đã duyệt: {result['nodes_exp']}")
            self.write_log(self.log_partially, "==== QUÁ TRÌNH DUYỆT (OR NODES) ====")
            for log_line in result["exploration_log"]:
                self.write_log(self.log_partially, log_line)

            self.write_log(self.log_partially, "\n==== KẾ HOẠCH HÀNH ĐỘNG (CONDITIONAL PLAN) ====")
            formatted_plan = self._format_plan_partially(result["plan"], indent=0)
            self.write_log(self.log_partially, formatted_plan)

            self.write_log(self.log_partially, "\n==== BẮT ĐẦU MÔ PHỎNG QUAN SÁT MỘT PHẦN ====")
            self.partially_plan = result["plan"]
            self.partially_true_pos = (r_start, c_start)
            self.partially_true_dirty = frozenset(initial_dirty)
            self.partially_belief = result["b0"]
            self.partially_step = 0

            self.animate_partially_step()
        else:
            self.write_log(self.log_partially, "Không tìm thấy kế hoạch hành động nào hợp lệ!")
            self.reset_controls()

    def _format_plan_partially(self, plan, indent=0):
        if plan == []:
            return " " * indent + "-> ĐẠT ĐÍCH"
        if plan is None:
            return " " * indent + "-> THẤT BẠI"

        action, plans_mapping = plan
        result_str = " " * indent + f"Hành động: {action}\n"
        for percept, subplan in plans_mapping.items():
            is_dirty, blocked_dirs = percept
            blocked_str = ",".join(sorted(blocked_dirs)) if blocked_dirs else "Không"
            result_str += " " * (indent + 2) + f"Nếu nhận cảm biến [Bụi: {is_dirty}, Tường kề: {blocked_str}]:\n"
            result_str += self._format_plan_partially(subplan, indent + 4) + "\n"
        return result_str.rstrip()

    def animate_partially_step(self):
        if not self.running:
            return

        curr_plan = self.partially_plan
        curr_true_pos = self.partially_true_pos
        curr_true_dirty = self.partially_true_dirty
        curr_belief = self.partially_belief

        self.robot_pos = frozenset(pos for pos, dirty in curr_belief)

        for r in range(self.M):
            for c in range(self.N):
                if self.initial_state[1][r][c] == 1:
                    if (r, c) in curr_true_dirty:
                        self.grid[r][c] = 1
                    else:
                        self.grid[r][c] = 0
        self.draw_grid()

        if len(curr_true_dirty) == 0:
            self.write_log(self.log_partially, f"\n[Hoàn tất] Đã làm sạch toàn bộ ngôi nhà sau {self.partially_step} bước!")
            messagebox.showinfo("Hoàn tất", f"Partially Observable Search hoàn thành!\nSố bước đã chạy: {self.partially_step}")
            self.running = False
            self.reset_controls()
            return

        if curr_plan == [] or curr_plan is None:
            self.write_log(self.log_partially, "\n[Lỗi] Kế hoạch kết thúc sớm hoặc thất bại!")
            self.running = False
            self.reset_controls()
            return

        action, plans_mapping = curr_plan
        self.partially_step += 1

        from algorithms.partially_observable import get_percept, predict_belief_state, update_belief_state
        obstacles = { (r, c) for r in range(self.M) for c in range(self.N) if self.initial_state[1][r][c] == -1 }

        directions_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
        if action == "Suck":
            next_true_pos = curr_true_pos
            next_true_dirty = curr_true_dirty - {curr_true_pos}
        else:
            dr, dc = directions_map[action]
            nr, nc = curr_true_pos[0] + dr, curr_true_pos[1] + dc
            if 0 <= nr < self.M and 0 <= nc < self.N and (nr, nc) not in obstacles:
                next_true_pos = (nr, nc)
            else:
                next_true_pos = curr_true_pos
            next_true_dirty = curr_true_dirty

        true_percept = get_percept(next_true_pos, next_true_dirty, self.M, self.N, obstacles)

        is_dirty, blocked_dirs = true_percept
        blocked_str = ",".join(sorted(blocked_dirs)) if blocked_dirs else "Không"
        log_msg = f"Bước {self.partially_step}: Cỡ Belief State = {len(curr_belief)}. Robot thực tế tại {curr_true_pos}.\n"
        log_msg += f"  -> Cảm nhận: [Bụi: {is_dirty}, Tường kề: {blocked_str}]. Thực hiện '{action}'"
        self.write_log(self.log_partially, log_msg)

        b_pred = predict_belief_state(curr_belief, action, self.M, self.N, obstacles)
        next_belief = update_belief_state(b_pred, true_percept, self.M, self.N, obstacles)

        next_plan = None
        for p_key, p_val in plans_mapping.items():
            if p_key[0] == true_percept[0] and frozenset(p_key[1]) == frozenset(true_percept[1]):
                next_plan = p_val
                break

        if next_plan is None:
            self.write_log(self.log_partially, f"\n[Lỗi] Không tìm thấy nhánh kế hoạch cho cảm nhận: {true_percept}!")
            self.running = False
            self.reset_controls()
            return

        self.partially_true_pos = next_true_pos
        self.partially_true_dirty = next_true_dirty
        self.partially_belief = next_belief
        self.partially_plan = next_plan

        self.root.after(800, self.animate_partially_step)
