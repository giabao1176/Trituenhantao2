import sys
import os
import random
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from algorithms import solve_vacuum, solve_and_or, solve_partially_observable

def draw_frame(M, N, grid, robot_pos, cell_size=60, algo_name="", step_num=0, total_steps=None, nodes_exp=0, nodes_gen=0, actions_taken=[]):
    width = N * cell_size
    grid_height = M * cell_size
    status_height = 100
    height = grid_height + status_height

    img = Image.new("RGBA", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)

    for r in range(M):
        for c in range(N):
            x1 = c * cell_size
            y1 = r * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            bg_color = "#f9f6f0" if (r + c) % 2 == 0 else "#f4efe6"
            draw.rectangle([x1, y1, x2, y2], fill=bg_color, outline="#dddddd")

            val = grid[r][c]
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            if val == -1:
                draw.rectangle([x1+4, y1+4, x2-4, y2-4], fill="#7f8c8d", outline="#34495e", width=2)
            elif val == 1:
                r_blob = cell_size * 0.22
                draw.ellipse([cx-r_blob, cy-r_blob, cx+r_blob, cy+r_blob], fill="#e67e22")

    robot_positions = list(robot_pos) if isinstance(robot_pos, (set, list, frozenset)) else [robot_pos]
    for r_robot, c_robot in robot_positions:
        rx1 = c_robot * cell_size + cell_size * 0.15
        ry1 = r_robot * cell_size + cell_size * 0.15
        rx2 = rx1 + cell_size * 0.7
        ry2 = ry1 + cell_size * 0.7
        draw.ellipse([rx1, ry1, rx2, ry2], fill="#2980b9", outline="#1f3a52", width=3)

        rcx = (rx1 + rx2) / 2
        rcy = (ry1 + ry2) / 2
        draw.ellipse([rcx-4, rcy-4, rcx+4, rcy+4], fill="#ffffff")

    draw.rectangle([0, grid_height, width, height], fill="#2c3e50")

    try:
        font_large = ImageFont.truetype("arial.ttf", 15)
        font_small = ImageFont.truetype("arial.ttf", 11)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    if total_steps is not None:
        line1 = f"Thuật toán: {algo_name} | Bước: {step_num}/{total_steps}"
    else:
        line1 = f"Thuật toán: {algo_name} | Bước: {step_num}"
    draw.text((12, grid_height + 10), line1, fill="#ffffff", font=font_large)

    line2 = f"Số ô đã duyệt (Expanded): {nodes_exp} | Đã tạo (Generated): {nodes_gen}"
    draw.text((12, grid_height + 34), line2, fill="#bdc3c7", font=font_small)

    action_seq_str = " -> ".join(actions_taken[-7:])
    if len(actions_taken) > 7:
        action_seq_str = "... -> " + action_seq_str
    if not actions_taken:
        action_seq_str = "Bắt đầu"
    line3 = f"Đã đi: {action_seq_str}"
    draw.text((12, grid_height + 56), line3, fill="#bdc3c7", font=font_small)

    line4 = f"Chú thích: U=Lên, D=Xuống, L=Trái, R=Phải, Suck=Hút"
    draw.text((12, grid_height + 76), line4, fill="#7f8c8d", font=font_small)

    return img

def generate_runnable_map_for_hill_climbing(M, N):
    print("Searching for a solvable map for Hill Climbing...")
    for attempt in range(1000):
        start_pos = (random.randint(0, M-1), random.randint(0, N-1))

        num_dirty = random.randint(5, 8)
        dirty_cells = set()
        while len(dirty_cells) < num_dirty:
            r = random.randint(0, M-1)
            c = random.randint(0, N-1)
            if (r, c) != start_pos:
                dirty_cells.add((r, c))

        num_obstacles = random.randint(5, 8)
        obstacles = set()
        while len(obstacles) < num_obstacles:
            r = random.randint(0, M-1)
            c = random.randint(0, N-1)
            if (r, c) != start_pos and (r, c) not in dirty_cells:
                obstacles.add((r, c))

        result = solve_vacuum(M, N, start_pos, dirty_cells, obstacles, "Hill Climbing", style=2)
        path = result.get("path", [])
        if path and len(path) >= 5 and len(path) <= 15:
            print(f"  -> Found working map on attempt {attempt+1}! Path length: {len(path)}")
            return start_pos, dirty_cells, obstacles

    print("  -> Could not find a suitable random map. Using fallback map.")
    return (3, 7), {(0,2),(1,6),(2,4),(3,1),(4,7),(5,2),(6,3),(7,5)}, {(1,1),(2,6),(4,2),(6,5),(7,3)}

def make_gif_for_standard_algo(algo, filename):
    M, N = 8, 8

    if algo == "Hill Climbing":
        start_pos, dirty_cells, obstacles = generate_runnable_map_for_hill_climbing(M, N)
    else:
        start_pos = (3, 7)
        dirty_cells = {(0,2),(1,6),(2,4),(3,1),(4,7),(5,2),(6,3),(7,5)}
        if start_pos in dirty_cells:
            dirty_cells.remove(start_pos)
        obstacles = {(1,1),(2,6),(4,2),(6,5),(7,3)}

    print(f"Solving and rendering Standard search for: {algo}...")
    result = solve_vacuum(M, N, start_pos, dirty_cells, obstacles, algo, style=2)

    path = result.get("path", [])
    directions = result.get("directions", [])
    nodes_exp = result.get("nodes_exp", 0)
    nodes_gen = result.get("nodes_gen", 0)

    if not path:
        print(f"  -> Skipping {algo}: No path returned.")
        return

    grid = [[0 for _ in range(N)] for _ in range(M)]
    for r, c in dirty_cells:
        grid[r][c] = 1
    for r, c in obstacles:
        grid[r][c] = -1

    total_steps = len(path) - 1
    frames = [draw_frame(M, N, grid, start_pos, algo_name=algo, step_num=0, total_steps=total_steps, nodes_exp=nodes_exp, nodes_gen=nodes_gen, actions_taken=[])]

    current_pos = start_pos
    step_num = 0
    for step_pos in path[1:]:
        step_num += 1
        current_pos = step_pos
        if grid[current_pos[0]][current_pos[1]] == 1:
            grid[current_pos[0]][current_pos[1]] = 0

        actions_taken = directions[:step_num]
        frames.append(draw_frame(M, N, grid, current_pos, algo_name=algo, step_num=step_num, total_steps=total_steps, nodes_exp=nodes_exp, nodes_gen=nodes_gen, actions_taken=actions_taken))

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs", "binh_thuong")
    os.makedirs(output_dir, exist_ok=True)
    frames[0].save(os.path.join(output_dir, filename), save_all=True, append_images=frames[1:], duration=450, loop=0)
    print(f"  -> Saved successfully at: gifs/binh_thuong/{filename} ({len(frames)} frames)")

def make_gif_for_sensorless(algo, filename):
    M, N = 3, 3
    start_pos = (0, 0)
    dirty_cells = {(0, 2)}
    obstacles = set()

    print(f"Solving and rendering Sensorless search for: {algo}...")
    result = solve_vacuum(M, N, start_pos, dirty_cells, obstacles, algo, style=2, sensorless=True)
    if not result["found"]:
        print(f"  -> Sensorless search failed for {algo}!")
        return

    nodes_exp = result.get("nodes_exp", 0)
    nodes_gen = result.get("nodes_gen", 0)
    directions = result.get("directions", [])
    total_steps = len(directions)

    from algorithms.sensorless import get_initial_belief_state
    b = get_initial_belief_state(M, N, dirty_cells, obstacles)
    grid = [[0 for _ in range(N)] for _ in range(M)]
    for r, c in dirty_cells:
        grid[r][c] = 1
    for r, c in obstacles:
        grid[r][c] = -1

    frames = []
    frames.append(draw_frame(M, N, grid, [pos for pos, d in b], algo_name=f"Sensorless ({algo})", step_num=0, total_steps=total_steps, nodes_exp=nodes_exp, nodes_gen=nodes_gen, actions_taken=[]))

    from algorithms.sensorless import transition_belief_state
    curr_b = b
    directions_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

    true_pos = start_pos
    true_dirty = set(dirty_cells)

    step_num = 0
    for step_dir in directions:
        step_num += 1
        dr, dc = directions_map.get(step_dir, (0, 0))
        nr, nc = true_pos[0] + dr, true_pos[1] + dc
        if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
            true_pos = (nr, nc)
        if true_pos in true_dirty:
            true_dirty.remove(true_pos)
            grid[true_pos[0]][true_pos[1]] = 0

        curr_b = transition_belief_state(curr_b, step_dir, M, N, obstacles)
        actions_taken = directions[:step_num]
        frames.append(draw_frame(M, N, grid, [pos for pos, d in curr_b], algo_name=f"Sensorless ({algo})", step_num=step_num, total_steps=total_steps, nodes_exp=nodes_exp, nodes_gen=nodes_gen, actions_taken=actions_taken))

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs", "khong_cam_bien")
    os.makedirs(output_dir, exist_ok=True)
    frames[0].save(os.path.join(output_dir, filename), save_all=True, append_images=frames[1:], duration=450, loop=0)
    print(f"  -> Saved successfully at: gifs/khong_cam_bien/{filename} ({len(frames)} frames)")

def make_gif_for_and_or(filename):
    M, N = 8, 8
    start_pos = (3, 7)
    dirty_cells = {(0,2),(1,6),(2,4),(3,1),(4,7),(5,2),(6,3),(7,5)}
    if start_pos in dirty_cells:
        dirty_cells.remove(start_pos)
    obstacles = {(1,1),(2,6),(4,2),(6,5),(7,3)}

    print("Solving and rendering for AND-OR Search...")
    result = solve_and_or(M, N, start_pos, dirty_cells, obstacles)
    if not result["found"]:
        print("  -> AND-OR Search failed!")
        return

    plan = result["plan"]
    problem = result["problem"]
    nodes_exp = result.get("nodes_exp", 0)
    nodes_gen = result.get("nodes_gen", 0)

    curr_state = (start_pos, frozenset(dirty_cells))

    grid = [[0 for _ in range(N)] for _ in range(M)]
    for r, c in dirty_cells:
        grid[r][c] = 1
    for r, c in obstacles:
        grid[r][c] = -1

    frames = [draw_frame(M, N, grid, start_pos, algo_name="AND-OR Search", step_num=0, total_steps=None, nodes_exp=nodes_exp, nodes_gen=nodes_gen, actions_taken=[])]
    curr_plan = plan

    step_num = 0
    actions_taken = []
    for _ in range(25):
        pos, dirty = curr_state
        if len(dirty) == 0 or curr_plan == [] or curr_plan is None:
            break
        action, plans_mapping = curr_plan
        step_num += 1
        actions_taken.append(action)

        possible_states = problem.results(curr_state, action)
        chosen_state = random.choice(possible_states)

        for r, c in dirty:
            if (r, c) not in chosen_state[1]:
                grid[r][c] = 0
        for r, c in chosen_state[1]:
            grid[r][c] = 1

        frames.append(draw_frame(M, N, grid, chosen_state[0], algo_name="AND-OR Search", step_num=step_num, total_steps=None, nodes_exp=nodes_exp, nodes_gen=nodes_gen, actions_taken=actions_taken))
        curr_state = chosen_state
        curr_plan = plans_mapping.get(chosen_state)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs", "quan_sat_mot_phan")
    os.makedirs(output_dir, exist_ok=True)
    frames[0].save(os.path.join(output_dir, filename), save_all=True, append_images=frames[1:], duration=450, loop=0)
    print(f"  -> Saved successfully at: gifs/quan_sat_mot_phan/{filename} ({len(frames)} frames)")

def make_gif_for_partially_observable(filename):
    M, N = 8, 8
    start_pos = (3, 7)
    dirty_cells = {(0,2),(1,6),(2,4),(3,1),(4,7),(5,2),(6,3),(7,5)}
    if start_pos in dirty_cells:
        dirty_cells.remove(start_pos)
    obstacles = {(1,1),(2,6),(4,2),(6,5),(7,3)}

    print("Solving and rendering for Partially Observable Search...")
    result = solve_partially_observable(M, N, start_pos, dirty_cells, obstacles)
    if not result["found"]:
        print("  -> Partially Observable Search failed!")
        return

    plan = result["plan"]
    curr_belief = result["b0"]
    nodes_exp = result.get("nodes_exp", 0)
    nodes_gen = result.get("nodes_gen", 0)

    true_pos = start_pos
    true_dirty = frozenset(dirty_cells)

    grid = [[0 for _ in range(N)] for _ in range(M)]
    for r, c in dirty_cells:
        grid[r][c] = 1
    for r, c in obstacles:
        grid[r][c] = -1

    frames = [draw_frame(M, N, grid, [pos for pos, d in curr_belief], algo_name="Partially Observable", step_num=0, total_steps=None, nodes_exp=nodes_exp, nodes_gen=nodes_gen, actions_taken=[])]
    curr_plan = plan

    from algorithms.partially_observable import get_percept, predict_belief_state, update_belief_state

    step_num = 0
    actions_taken = []
    for _ in range(100):
        if len(true_dirty) == 0 or curr_plan == [] or curr_plan is None:
            break
        action, plans_mapping = curr_plan
        step_num += 1
        actions_taken.append(action)

        directions_map = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
        if action == "Suck":
            if true_pos in true_dirty:
                true_dirty = true_dirty - {true_pos}
                grid[true_pos[0]][true_pos[1]] = 0
        else:
            dr, dc = directions_map[action]
            nr, nc = true_pos[0] + dr, true_pos[1] + dc
            if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                true_pos = (nr, nc)

        true_percept = get_percept(true_pos, true_dirty, M, N, obstacles)

        b_pred = predict_belief_state(curr_belief, action, M, N, obstacles)
        curr_belief = update_belief_state(b_pred, true_percept, M, N, obstacles)

        frames.append(draw_frame(M, N, grid, [pos for pos, d in curr_belief], algo_name="Partially Observable", step_num=step_num, total_steps=None, nodes_exp=nodes_exp, nodes_gen=nodes_gen, actions_taken=actions_taken))

        next_plan = None
        for p_key, p_val in plans_mapping.items():
            if p_key[0] == true_percept[0] and frozenset(p_key[1]) == frozenset(true_percept[1]):
                next_plan = p_val
                break
        curr_plan = next_plan

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gifs", "quan_sat_mot_phan")
    os.makedirs(output_dir, exist_ok=True)
    frames[0].save(os.path.join(output_dir, filename), save_all=True, append_images=frames[1:], duration=450, loop=0)
    print(f"  -> Saved successfully at: gifs/quan_sat_mot_phan/{filename} ({len(frames)} frames)")

def main():
    algos = ["BFS", "DFS", "IDS", "UCS", "A*", "Greedy", "IDA*", "Hill Climbing", "Random Restart Hill", "Local Beam Search", "Simulated Annealing"]
    for algo in algos:
        safe_name = algo.lower().replace("*", "_star").replace(" ", "_")
        filename = f"mayhutbui_{safe_name}.gif"

        make_gif_for_standard_algo(algo, filename)

        make_gif_for_sensorless(algo, filename)

    make_gif_for_and_or("mayhutbui_and_or.gif")
    make_gif_for_partially_observable("mayhutbui_partially_observable.gif")
    print("\nDone! All Vacuum cleaner GIFs created and categorized successfully.")

if __name__ == "__main__":
    main()
