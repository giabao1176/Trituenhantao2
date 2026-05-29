import random

def heuristic(pos, dirty):
    if not dirty:
        return 0
    # Manhattan distance to the nearest dirty cell
    min_dist = min(abs(pos[0] - d[0]) + abs(pos[1] - d[1]) for d in dirty)
    return min_dist + len(dirty) - 1

def solve_hill_climbing(M, N, start_pos, initial_dirty, obstacles, style):
    nodes_generated = 1
    nodes_expanded = 0
    logs = []

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    current_state = (start_pos, frozenset(initial_dirty))
    path = [start_pos]
    dirs = []

    if not initial_dirty:
        return {"found": True, "path": path, "directions": dirs, "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    style_name = {1: "Leo đồi ĐƠN GIẢN", 2: "Leo đồi DỐC NHẤT", 3: "Leo đồi NGẪU NHIÊN"}.get(style, "Hill Climbing")
    logs.append(f"--- BẮT ĐẦU {style_name} ---")

    while True:
        r, c = current_state[0]
        dirty = current_state[1]
        h = heuristic((r, c), dirty)

        nodes_expanded += 1
        step_log = f"Bước {nodes_expanded}: Robot tại ({r},{c}) [h={h}], còn {len(dirty)} bụi"

        if not dirty:
            logs.append(step_log + " | ĐẠT ĐÍCH!")
            return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        # Generate all valid neighbors
        valid_neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                next_dirty = dirty - {(nr, nc)}
                next_h = heuristic((nr, nc), next_dirty)
                valid_neighbors.append({
                    "pos": (nr, nc),
                    "dirty": next_dirty,
                    "h": next_h,
                    "dir": dir_names[(dr, dc)]
                })
                nodes_generated += 1

        if not valid_neighbors:
            logs.append(step_log + "\n  -> Bị kẹt! Không có ô lân cận hợp lệ.")
            return {"found": False, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        next_step = None

        if style == 1:
            # Simple Hill Climbing: take the first neighbor with strictly better heuristic
            for neighbor in valid_neighbors:
                if neighbor["h"] < h:
                    next_step = neighbor
                    break
            if next_step:
                logs.append(step_log + f"\n  -> Chọn ngay {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]")

        elif style == 2:
            # Steepest-Ascent Hill Climbing: evaluate all neighbors, pick the absolute best with h_next < h
            better_neighbors = [n for n in valid_neighbors if n["h"] < h]
            if better_neighbors:
                better_neighbors.sort(key=lambda x: x["h"])
                # Take the one with the smallest h value
                next_step = better_neighbors[0]
                logs.append(step_log + f"\n  -> Chọn dốc nhất {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]")

        elif style == 3:
            # Stochastic Hill Climbing: pick a random neighbor among all strictly better neighbors
            better_neighbors = [n for n in valid_neighbors if n["h"] < h]
            if better_neighbors:
                next_step = random.choice(better_neighbors)
                logs.append(step_log + f"\n  -> Chọn ngẫu nhiên {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]")

        if next_step is None:
            # Stuck in local optimum / plateau
            logs.append(step_log + "\n  -> BỊ KẸT TẠI CỰC TRỊ ĐỊA PHƯƠNG! Không có ô lân cận nào tốt hơn.")
            return {"found": False, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        # Transition to next state
        current_state = (next_step["pos"], next_step["dirty"])
        path.append(next_step["pos"])
        dirs.append(next_step["dir"])


def solve_hill_climbing_stepwise(M, N, start_pos, initial_dirty, obstacles, style):
    nodes_generated = 1
    nodes_expanded = 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    current_state = (start_pos, frozenset(initial_dirty))
    path = [start_pos]
    dirs = []

    if not initial_dirty:
        yield {"pos": start_pos, "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "path": path, "directions": dirs}
        return

    style_name = {1: "Leo đồi ĐƠN GIẢN", 2: "Leo đồi DỐC NHẤT", 3: "Leo đồi NGẪU NHIÊN"}.get(style, "Hill Climbing")
    yield {"pos": start_pos, "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU {style_name} ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}

    while True:
        r, c = current_state[0]
        dirty = current_state[1]
        h = heuristic((r, c), dirty)

        nodes_expanded += 1
        log_text = f"Bước {nodes_expanded}: Robot tại ({r},{c}) [h={h}], còn {len(dirty)} ô bụi"

        if not dirty:
            yield {"pos": (r, c), "dirty": dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
            return

        valid_neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                next_dirty = dirty - {(nr, nc)}
                next_h = heuristic((nr, nc), next_dirty)
                valid_neighbors.append({
                    "pos": (nr, nc),
                    "dirty": next_dirty,
                    "h": next_h,
                    "dir": dir_names[(dr, dc)]
                })
                nodes_generated += 1

        if not valid_neighbors:
            yield {"pos": (r, c), "dirty": dirty, "log": log_text + "\n  -> Bị kẹt! Không có ô lân cận hợp lệ.", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
            return

        next_step = None

        if style == 1:
            for neighbor in valid_neighbors:
                if neighbor["h"] < h:
                    next_step = neighbor
                    break
            if next_step:
                log_text += f"\n  -> Chọn ngay {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]"

        elif style == 2:
            better_neighbors = [n for n in valid_neighbors if n["h"] < h]
            if better_neighbors:
                better_neighbors.sort(key=lambda x: x["h"])
                next_step = better_neighbors[0]
                log_text += f"\n  -> Chọn dốc nhất {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]"

        elif style == 3:
            better_neighbors = [n for n in valid_neighbors if n["h"] < h]
            if better_neighbors:
                next_step = random.choice(better_neighbors)
                log_text += f"\n  -> Chọn ngẫu nhiên {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]"

        if next_step is None:
            yield {"pos": (r, c), "dirty": dirty, "log": log_text + "\n  -> BỊ KẸT TẠI CỰC TRỊ ĐỊA PHƯƠNG! Không có ô lân cận nào tốt hơn.", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
            return

        current_state = (next_step["pos"], next_step["dirty"])
        path.append(next_step["pos"])
        dirs.append(next_step["dir"])

        yield {"pos": (r, c), "dirty": dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
