import tkinter as tk
from tkinter import ttk, messagebox
import random
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
from algorithms import solve_vacuum, solve_vacuum_stepwise

class RobotVacuumGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Hút Bụi - BFS/DFS/IDS/UCS/Greedy/A*")
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
        
        # Left Panel
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(left_panel, bg="#ffffff", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.canvas.bind("<Configure>", lambda e: self.draw_grid())
        self.canvas.bind("<Button-1>", self.on_canvas_left_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        
        # Controls
        ctrl_frame = ttk.Frame(left_panel)
        ctrl_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ctrl_frame, text="Thuật toán:").grid(row=0, column=0, sticky="w", padx=2)
        self.algo_var = tk.StringVar(value="BFS")
        self.algo_combo = ttk.Combobox(ctrl_frame, textvariable=self.algo_var, values=["BFS", "DFS", "IDS", "UCS", "Greedy", "A*"], state="readonly", width=8)
        self.algo_combo.grid(row=0, column=1, sticky="w", padx=2)
        
        tk.Label(ctrl_frame, text="Kiểu:").grid(row=0, column=2, sticky="w", padx=10)
        self.style_var = tk.StringVar(value="Style 2")
        self.style_combo = ttk.Combobox(ctrl_frame, textvariable=self.style_var, values=["Style 1", "Style 2"], state="readonly", width=8)
        self.style_combo.grid(row=0, column=3, sticky="w", padx=2)
        
        # Buttons
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

        # Legend
        legend_frame = ttk.LabelFrame(left_panel, text=" Chú thích giao diện & Thuật toán ")
        legend_frame.pack(fill=tk.X, pady=5, padx=2)
        
        legend_text = (
            "• Máy hút bụi: Vị trí Robot hút bụi hiện tại\n"
            "• Vật cản: Chướng ngại vật robot không thể đi qua\n"
            "• Bụi(Ngôi sao): Các điểm bẩn cần làm sạch\n"
            "• Style 1: Kiểm tra Goal khi lấy trạng thái NODE con ra khỏi Frontier\n"
            "• Style 2: Kiểm tra Goal ngay khi sinh trạng thái NODE con (thường nhanh hơn)"
        )
        tk.Label(legend_frame, text=legend_text, justify=tk.LEFT, anchor="w", font=("Segoe UI", 9), fg="#333333").pack(fill=tk.X, padx=5, pady=5)
        
        # Right Panel with Tabs
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Tự động (giải xong rồi chạy)
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
        
        # Tab 2: Từng bước (chạy real-time)
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

    def write_log(self, widget, text, clear=False):
        widget.config(state=tk.NORMAL)
        if clear:
            widget.delete("1.0", tk.END)
        widget.insert(tk.END, text + "\n")
        
        # Giới hạn số dòng để tránh quá tải bộ nhớ & gây đơ giao diện
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

        r_robot, c_robot = self.robot_pos
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
        style = 1 if "Style 1" in style_str else 2
        return r_start, c_start, initial_dirty, obstacles, algo, style, style_str

    def _lock_controls(self):
        self.running = True
        self.btn_run.config(state=tk.DISABLED)
        self.btn_random.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.algo_combo.config(state=tk.DISABLED)
        self.style_combo.config(state=tk.DISABLED)

    def start_current_tab(self):
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:
            self.start_auto_mode()
        else:
            self.start_step_mode()

    # ==================== TAB 1: TỰ ĐỘNG ====================
    def start_auto_mode(self):
        self._lock_controls()
        r_start, c_start, initial_dirty, obstacles, algo, style, style_str = self._get_search_params()
        
        self.write_log(self.log_auto, f"Bắt đầu giải bằng {algo} ({style_str})...", clear=True)
        
        result = solve_vacuum(
            self.M, self.N, (r_start, c_start), initial_dirty, obstacles, algo, style
        )
        
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

    # ==================== TAB 2: TỪNG BƯỚC ====================
    def start_step_mode(self):
        self._lock_controls()
        r_start, c_start, initial_dirty, obstacles, algo, style, style_str = self._get_search_params()
        
        self.write_log(self.log_step, f"Bắt đầu duyệt từng bước bằng {algo} ({style_str})...", clear=True)
        
        self.solver_gen = solve_vacuum_stepwise(
            self.M, self.N, (r_start, c_start), initial_dirty, obstacles, algo, style
        )
        self.explore_next_step()

    def explore_next_step(self):
        if not self.running:
            return

        # Robot hút bụi có không gian trạng thái nhỏ, luôn chạy 1 bước/frame để trực quan
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

        # Cập nhật giao diện một lần duy nhất cho cả batch
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
            if last_step["path"]:
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
        self.reset_controls()

    def reset_controls(self):
        self.btn_run.config(state=tk.NORMAL)
        self.btn_random.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.algo_combo.config(state="readonly")
        self.style_combo.config(state="readonly")
