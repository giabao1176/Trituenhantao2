import random
from .hill_climbing import heuristic

def solve_random_restart_hill(M, N, start_pos, initial_dirty, obstacles, style):
    max_restarts = 100
    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    
    style_name = {1: "Leo đồi ĐƠN GIẢN", 2: "Leo đồi DỐC NHẤT", 3: "Leo đồi NGẪU NHIÊN"}.get(style, "Hill Climbing")
    logs.append(f"--- BẮT ĐẦU Random Restart Hill Climbing ({style_name}) ---")
    
    current_pos = start_pos
    current_dirty = frozenset(initial_dirty)
    path = [start_pos]
    dirs = []
    
    # If starting position is in dirty, clean it
    if current_pos in current_dirty:
        current_dirty = current_dirty - {current_pos}
        
    if not current_dirty:
        return {"found": True, "path": path, "directions": dirs, "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}
        
    restart_count = 0
    
    while True:
        sub_path = [current_pos]
        sub_dirs = []
        sub_state = (current_pos, current_dirty)
        stuck = False
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}
        
        while True:
            r, c = sub_state[0]
            dirty = sub_state[1]
            h = heuristic((r, c), dirty)
            
            nodes_expanded += 1
            step_log = f"Lần restart {restart_count}: Bước {nodes_expanded}: Robot tại ({r},{c}) [h={h}], còn {len(dirty)} bụi"
            
            if not dirty:
                logs.append(step_log + " | ĐẠT ĐÍCH CHÍNH!")
                # Concatenate paths
                for p in sub_path[1:]:
                    path.append(p)
                for d in sub_dirs:
                    dirs.append(d)
                current_dirty = dirty
                break
                
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
                logs.append(step_log + f"\n  -> Bị kẹt! Không có ô lân cận hợp lệ.")
                stuck = True
                break
                
            next_step = None
            if style == 1:
                for neighbor in valid_neighbors:
                    if neighbor["h"] < h:
                        next_step = neighbor
                        break
                if next_step:
                    logs.append(step_log + f"\n  -> Chọn ngay {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]")
            elif style == 2:
                better_neighbors = [n for n in valid_neighbors if n["h"] < h]
                if better_neighbors:
                    better_neighbors.sort(key=lambda x: x["h"])
                    next_step = better_neighbors[0]
                    logs.append(step_log + f"\n  -> Chọn dốc nhất {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]")
            elif style == 3:
                better_neighbors = [n for n in valid_neighbors if n["h"] < h]
                if better_neighbors:
                    next_step = random.choice(better_neighbors)
                    logs.append(step_log + f"\n  -> Chọn ngẫu nhiên {next_step['dir']} ({next_step['pos'][0]},{next_step['pos'][1]}) [h={next_step['h']} < {h}]")
                    
            if next_step is None:
                logs.append(step_log + "\n  -> BỊ KẸT TẠI CỰC TRỊ ĐỊA PHƯƠNG! Không có ô lân cận nào tốt hơn.")
                stuck = True
                break
                
            sub_state = (next_step["pos"], next_step["dirty"])
            sub_path.append(next_step["pos"])
            sub_dirs.append(next_step["dir"])
            
        if not current_dirty:
            # We reached the goal!
            return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}
            
        if stuck:
            # Add partial path from this run
            for p in sub_path[1:]:
                path.append(p)
            for d in sub_dirs:
                dirs.append(d)
            current_pos = sub_path[-1]
            current_dirty = sub_state[1]
            
            if restart_count >= max_restarts:
                logs.append(f"--- ĐẠT GIỚI HẠN RESTARTS ({max_restarts}) ---")
                return {"found": False, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}
                
            # Find a random cell that is not an obstacle and not the current position
            all_cells = [(r, c) for r in range(M) for c in range(N) if (r, c) not in obstacles and (r, c) != current_pos]
            if not all_cells:
                logs.append("Không còn ô trống hợp lệ để restart!")
                return {"found": False, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}
                
            restart_pos = random.choice(all_cells)
            restart_count += 1
            logs.append(f"==> [RESTART] Bị kẹt tại {current_pos}. Reset vị trí ngẫu nhiên sang: {restart_pos} (Restart lần {restart_count})")
            
            # Teleport robot in path and directions
            path.append(restart_pos)
            dirs.append("JUMP")
            
            current_pos = restart_pos
            if current_pos in current_dirty:
                current_dirty = current_dirty - {current_pos}
                logs.append(f"  -> Ô restart trùng ô bụi! Đã tự động dọn dẹp bụi tại {current_pos}.")
                
            if not current_dirty:
                logs.append("==> ĐẠT ĐÍCH SAU KHI RESTART!")
                return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}


def solve_random_restart_hill_stepwise(M, N, start_pos, initial_dirty, obstacles, style):
    max_restarts = 100
    nodes_generated = 1
    nodes_expanded = 0
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}
    
    current_pos = start_pos
    current_dirty = frozenset(initial_dirty)
    path = [start_pos]
    dirs = []
    
    if current_pos in current_dirty:
        current_dirty = current_dirty - {current_pos}
        
    style_name = {1: "Leo đồi ĐƠN GIẢN", 2: "Leo đồi DỐC NHẤT", 3: "Leo đồi NGẪU NHIÊN"}.get(style, "Hill Climbing")
    yield {"pos": current_pos, "dirty": current_dirty, "log": f"--- BẮT ĐẦU Random Restart Hill Climbing ({style_name}) ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
    
    if not current_dirty:
        yield {"pos": current_pos, "dirty": current_dirty, "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "path": path, "directions": dirs}
        return
        
    restart_count = 0
    
    while True:
        sub_path = [current_pos]
        sub_dirs = []
        sub_state = (current_pos, current_dirty)
        stuck = False
        
        while True:
            r, c = sub_state[0]
            dirty = sub_state[1]
            h = heuristic((r, c), dirty)
            
            nodes_expanded += 1
            log_text = f"Lần restart {restart_count}: Bước {nodes_expanded}: Robot tại ({r},{c}) [h={h}], còn {len(dirty)} ô bụi"
            
            if not dirty:
                # Concatenate paths
                for p in sub_path[1:]:
                    path.append(p)
                for d in sub_dirs:
                    dirs.append(d)
                current_dirty = dirty
                yield {"pos": (r, c), "dirty": dirty, "log": log_text + " -> ĐẠT ĐÍCH CHÍNH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
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
                log_text += f"\n  -> Bị kẹt! Không có ô lân cận hợp lệ."
                stuck = True
                yield {"pos": (r, c), "dirty": dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
                break
                
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
                log_text += "\n  -> BỊ KẸT TẠI CỰC TRỊ ĐỊA PHƯƠNG! Không có ô lân cận nào tốt hơn."
                stuck = True
                yield {"pos": (r, c), "dirty": dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
                break
                
            sub_state = (next_step["pos"], next_step["dirty"])
            sub_path.append(next_step["pos"])
            sub_dirs.append(next_step["dir"])
            
            yield {"pos": (r, c), "dirty": dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
            
        if not current_dirty:
            return
            
        if stuck:
            # Add partial path from this run
            for p in sub_path[1:]:
                path.append(p)
            for d in sub_dirs:
                dirs.append(d)
            current_pos = sub_path[-1]
            current_dirty = sub_state[1]
            
            if restart_count >= max_restarts:
                yield {"pos": current_pos, "dirty": current_dirty, "log": f"--- ĐẠT GIỚI HẠN RESTARTS ({max_restarts}) ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
                return
                
            all_cells = [(r, c) for r in range(M) for c in range(N) if (r, c) not in obstacles and (r, c) != current_pos]
            if not all_cells:
                yield {"pos": current_pos, "dirty": current_dirty, "log": "Không còn ô trống hợp lệ để restart!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
                return
                
            restart_pos = random.choice(all_cells)
            restart_count += 1
            
            log_restart = f"==> [RESTART] Bị kẹt tại {current_pos}. Reset vị trí ngẫu nhiên sang: {restart_pos} (Restart lần {restart_count})"
            
            path.append(restart_pos)
            dirs.append("JUMP")
            
            current_pos = restart_pos
            if current_pos in current_dirty:
                current_dirty = current_dirty - {current_pos}
                log_restart += f"\n  -> Ô restart trùng ô bụi! Đã tự động dọn dẹp bụi tại {current_pos}."
                
            yield {"pos": current_pos, "dirty": current_dirty, "log": log_restart, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
            
            if not current_dirty:
                yield {"pos": current_pos, "dirty": current_dirty, "log": "==> ĐẠT ĐÍCH SAU KHI RESTART!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
                return
