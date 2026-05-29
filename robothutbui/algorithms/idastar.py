def heuristic(pos, dirty):
    if not dirty:
        return 0
    # Manhattan distance to the nearest dirty cell
    min_dist = min(abs(pos[0] - d[0]) + abs(pos[1] - d[1]) for d in dirty)
    return min_dist + len(dirty) - 1

def solve_idastar(M, N, start_pos, initial_dirty, obstacles, style):
    nodes_generated = 1
    nodes_expanded = 0
    logs = []

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    if not initial_dirty:
        return {"found": True, "path": [start_pos], "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    initial_state = (start_pos, frozenset(initial_dirty))
    limit = heuristic(start_pos, initial_dirty)

    while True:
        logs.append(f"--- BẮT ĐẦU IDA* VỚI F-LIMIT = {limit} ---")
        # stack stores: (state, g, path_list, directions_list)
        stack = [(initial_state, 0, [initial_state], [])]
        next_limit = float('inf')
        
        # Keep track of states visited within the current iteration to prune suboptimal paths
        visited = {initial_state: 0} # state -> min_g
        
        while stack:
            state, g, path_list, dirs = stack.pop()
            nodes_expanded += 1
            r, c = state[0]
            dirty = state[1]

            h = heuristic((r, c), dirty)
            f = g + h
            
            step_log = f"Bước {nodes_expanded} (limit={limit}): Xét ({r},{c}) [f={f}, g={g}, h={h}], còn {len(dirty)} bụi"

            if style == 1 and not dirty:
                logs.append(step_log + " | ĐẠT ĐÍCH!")
                return {"found": True, "path": [s[0] for s in path_list], "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            if nodes_expanded >= 100000:
                logs.append("Vượt quá giới hạn!")
                return {"found": False, "path": None, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            if f > limit:
                next_limit = min(next_limit, f)
                logs.append(step_log + f"\n  -> f={f} > limit={limit}. Cắt nhánh!")
                continue

            children = []
            # We push onto stack in reverse directions so they are popped in U, D, L, R order
            for dr, dc in reversed(directions):
                nr, nc = r + dr, c + dc
                if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                    next_state = ((nr, nc), dirty - {(nr, nc)})
                    next_g = g + 1
                    
                    if next_state in path_list:
                        continue
                        
                    if next_state not in visited or next_g < visited[next_state]:
                        visited[next_state] = next_g
                        nodes_generated += 1
                        children.append(dir_names[(dr, dc)])
                        
                        if style == 2 and not next_state[1]:
                            logs.append(step_log + f"\n  -> Sinh con: {dir_names[(dr, dc)]} | ĐẠT ĐÍCH!")
                            return {"found": True, "path": [s[0] for s in path_list] + [(nr, nc)], "directions": dirs + [dir_names[(dr, dc)]], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}
                            
                        stack.append((next_state, next_g, path_list + [next_state], dirs + [dir_names[(dr, dc)]]))

            if children:
                children.reverse()
                logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)}")
            else:
                logs.append(step_log + "\n  -> Không sinh thêm con.")

        if next_limit == float('inf'):
            break
        limit = next_limit

    return {"found": False, "path": None, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}


def solve_idastar_stepwise(M, N, start_pos, initial_dirty, obstacles, style):
    nodes_generated = 1
    nodes_expanded = 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    if not initial_dirty:
        yield {"pos": start_pos, "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "path": [start_pos], "directions": []}
        return

    initial_state = (start_pos, frozenset(initial_dirty))
    limit = heuristic(start_pos, initial_dirty)

    while True:
        yield {"pos": start_pos, "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU IDA* VỚI F-LIMIT = {limit} ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}

        stack = [(initial_state, 0, [initial_state], [])]
        next_limit = float('inf')
        visited = {initial_state: 0}

        while stack:
            state, g, path_list, dirs = stack.pop()
            nodes_expanded += 1
            r, c = state[0]
            dirty = state[1]

            h = heuristic((r, c), dirty)
            f = g + h

            # Show active stack
            sorted_stack = list(reversed(stack))
            stack_show = ", ".join(f"({s[0][0][0]},{s[0][0][1]})[f={s[1]+heuristic(s[0][0], s[0][1])},g={s[1]}]" for s in sorted_stack[:4])
            if len(stack) > 4:
                stack_show += f" ... (+{len(stack)-4} node)"

            log_text = f"Bước {nodes_expanded} (limit={limit}): Xét ({r},{c}) [f={f}, g={g}, h={h}], còn {len(dirty)} ô bụi\n  -> Stack: [{stack_show}]"

            if style == 1 and not dirty:
                yield {"pos": (r, c), "dirty": dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": [s[0] for s in path_list], "directions": dirs}
                return

            if nodes_expanded >= 100000:
                yield {"pos": (r, c), "dirty": dirty, "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
                return

            if f > limit:
                next_limit = min(next_limit, f)
                yield {"pos": (r, c), "dirty": dirty, "log": log_text + f"\n  -> f={f} > limit={limit}. Cắt nhánh!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
                continue

            children = []
            for dr, dc in reversed(directions):
                nr, nc = r + dr, c + dc
                if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                    next_state = ((nr, nc), dirty - {(nr, nc)})
                    next_g = g + 1

                    if next_state in path_list:
                        continue

                    if next_state not in visited or next_g < visited[next_state]:
                        visited[next_state] = next_g
                        nodes_generated += 1
                        children.append(dir_names[(dr, dc)])

                        if style == 2 and not next_state[1]:
                            yield {"pos": (nr, nc), "dirty": next_state[1], "log": log_text + f"\n  -> Sinh con: {dir_names[(dr, dc)]} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": [s[0] for s in path_list] + [(nr, nc)], "directions": dirs + [dir_names[(dr, dc)]]}
                            return

                        stack.append((next_state, next_g, path_list + [next_state], dirs + [dir_names[(dr, dc)]]))

            if children:
                children.reverse()
                log_text += f"\n  -> Sinh con: {', '.join(children)}"
            else:
                log_text += "\n  -> Không sinh thêm con."

            yield {"pos": (r, c), "dirty": dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}

        if next_limit == float('inf'):
            break
        limit = next_limit

    yield {"pos": start_pos, "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
