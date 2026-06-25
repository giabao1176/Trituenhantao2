import math
import random

def heuristic(pos, dirty):
    if not dirty:
        return 0
    min_dist = min(abs(pos[0] - d[0]) + abs(pos[1] - d[1]) for d in dirty)
    return min_dist + len(dirty) - 1

def solve_simulated_annealing(M, N, start_pos, initial_dirty, obstacles, style):
    initial_dirty = frozenset(initial_dirty)
    current_pos = start_pos
    current_dirty = initial_dirty

    if current_pos in current_dirty:
        current_dirty = current_dirty - {current_pos}

    path = [current_pos]
    dirs = []

    if not current_dirty:
        return {"found": True, "path": path, "directions": dirs, "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    T0 = 100.0
    T = T0
    max_steps = 1000

    nodes_generated = 1
    nodes_expanded = 0
    logs = []

    style_name = "Tuyến tính" if style == 1 else "Mũ"
    logs.append(f"--- BẮT ĐẦU Simulated Annealing (Luyện kim giả lập - Hạ nhiệt {style_name}) ---")

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    step = 0
    while step < max_steps:
        step += 1
        nodes_expanded += 1

        if style == 1:
            T = T0 * (1.0 - step / max_steps)
        else:
            T = T0 * (0.98 ** step)

        if T <= 1e-4:
            logs.append(f"Bước {step}: Nhiệt độ quá thấp (T = {T:.6f} <= 1e-4). Kết thúc tìm kiếm.")
            break

        r, c = current_pos
        h_curr = heuristic(current_pos, current_dirty)
        step_log = f"Bước {step}: Robot tại ({r},{c}) [h={h_curr}], T={T:.4f}, còn {len(current_dirty)} bụi"

        if not current_dirty:
            logs.append(step_log + " | ĐẠT ĐÍCH!")
            return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        valid_neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                next_dirty = current_dirty - {(nr, nc)}
                h_next = heuristic((nr, nc), next_dirty)
                valid_neighbors.append({
                    "pos": (nr, nc),
                    "dirty": next_dirty,
                    "h": h_next,
                    "dir": dir_names[(dr, dc)]
                })
                nodes_generated += 1

        if not valid_neighbors:
            logs.append(step_log + " | Bị kẹt! Không có ô lân cận hợp lệ.")
            break

        neighbor = random.choice(valid_neighbors)
        delta_E = neighbor["h"] - h_curr

        if delta_E <= 0:
            current_pos = neighbor["pos"]
            current_dirty = neighbor["dirty"]
            path.append(current_pos)
            dirs.append(neighbor["dir"])
            logs.append(step_log + f"\n  -> [Chấp nhận] Đi {neighbor['dir']} ({neighbor['pos'][0]},{neighbor['pos'][1]}) [h={neighbor['h']} <= {h_curr}]")
        else:
            p = math.exp(-delta_E / T)
            if random.random() < p:
                current_pos = neighbor["pos"]
                current_dirty = neighbor["dirty"]
                path.append(current_pos)
                dirs.append(neighbor["dir"])
                logs.append(step_log + f"\n  -> [Chấp nhận tệ hơn] Đi {neighbor['dir']} ({neighbor['pos'][0]},{neighbor['pos'][1]}) [h={neighbor['h']} > {h_curr}] với p={p:.4f}")
            else:
                logs.append(step_log + f"\n  -> [Từ chối] Giữ nguyên vị trí tại ({r},{c}) [h={neighbor['h']} > {h_curr}] với p={p:.4f}")

    if not current_dirty:
        return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

    logs.append(f"Không thể dọn sạch toàn bộ bụi sau {step} bước.")
    return {"found": False, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_simulated_annealing_stepwise(M, N, start_pos, initial_dirty, obstacles, style):
    initial_dirty = frozenset(initial_dirty)
    current_pos = start_pos
    current_dirty = initial_dirty

    if current_pos in current_dirty:
        current_dirty = current_dirty - {current_pos}

    path = [current_pos]
    dirs = []

    style_name = "Tuyến tính" if style == 1 else "Mũ"
    yield {"pos": current_pos, "dirty": current_dirty, "log": f"--- BẮT ĐẦU Simulated Annealing (Luyện kim giả lập - Hạ nhiệt {style_name}) ---", "is_goal": False, "nodes_gen": 1, "nodes_exp": 0, "path": None, "directions": []}

    if not current_dirty:
        yield {"pos": current_pos, "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "path": path, "directions": []}
        return

    T0 = 100.0
    T = T0
    max_steps = 1000

    nodes_generated = 1
    nodes_expanded = 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    step = 0
    while step < max_steps:
        step += 1
        nodes_expanded += 1

        if style == 1:
            T = T0 * (1.0 - step / max_steps)
        else:
            T = T0 * (0.98 ** step)

        r, c = current_pos
        h_curr = heuristic(current_pos, current_dirty)
        log_text = f"Bước {step}: Robot tại ({r},{c}) [h={h_curr}], T={T:.4f}, còn {len(current_dirty)} ô bụi"

        if not current_dirty:
            yield {"pos": current_pos, "dirty": current_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
            return

        if T <= 1e-4:
            yield {"pos": current_pos, "dirty": current_dirty, "log": log_text + f"\n  -> Nhiệt độ quá thấp (T = {T:.6f} <= 1e-4). Dừng tìm kiếm.", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
            return

        valid_neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                next_dirty = current_dirty - {(nr, nc)}
                h_next = heuristic((nr, nc), next_dirty)
                valid_neighbors.append({
                    "pos": (nr, nc),
                    "dirty": next_dirty,
                    "h": h_next,
                    "dir": dir_names[(dr, dc)]
                })
                nodes_generated += 1

        if not valid_neighbors:
            yield {"pos": current_pos, "dirty": current_dirty, "log": log_text + "\n  -> Bị kẹt! Không có ô lân cận hợp lệ.", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
            return

        neighbor = random.choice(valid_neighbors)
        delta_E = neighbor["h"] - h_curr

        if delta_E <= 0:
            current_pos = neighbor["pos"]
            current_dirty = neighbor["dirty"]
            path.append(current_pos)
            dirs.append(neighbor["dir"])
            log_text += f"\n  -> [Chấp nhận] Đi {neighbor['dir']} ({neighbor['pos'][0]},{neighbor['pos'][1]}) [h={neighbor['h']} <= {h_curr}]"
        else:
            p = math.exp(-delta_E / T)
            if random.random() < p:
                current_pos = neighbor["pos"]
                current_dirty = neighbor["dirty"]
                path.append(current_pos)
                dirs.append(neighbor["dir"])
                log_text += f"\n  -> [Chấp nhận tệ hơn] Đi {neighbor['dir']} ({neighbor['pos'][0]},{neighbor['pos'][1]}) [h={neighbor['h']} > {h_curr}] với p={p:.4f}"
            else:
                log_text += f"\n  -> [Từ chối] Giữ nguyên vị trí tại ({r},{c}) [h={neighbor['h']} > {h_curr}] với p={p:.4f}"

        yield {"pos": current_pos, "dirty": current_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}

    if not current_dirty:
        yield {"pos": current_pos, "dirty": current_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
    else:
        yield {"pos": current_pos, "dirty": current_dirty, "log": log_text + f"\n  -> Kết thúc mà không dọn sạch bụi sau {step} bước.", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
