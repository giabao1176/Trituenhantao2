def solve_ids(M, N, start_pos, initial_dirty, obstacles, style):
    nodes_generated = 1
    nodes_expanded = 0
    logs = []

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    def get_path(state, parent):
        path, dirs = [], []
        while state is not None:
            path.append(state[0])
            p, d = parent[state]
            if d: dirs.append(d)
            state = p
        return path[::-1], dirs[::-1]

    if not initial_dirty:
        return {"found": True, "path": [start_pos], "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    initial_state = (start_pos, frozenset(initial_dirty))

    for depth_limit in range(1000):
        logs.append(f"--- BẮT ĐẦU DLS VỚI ĐỘ SÂU LIMIT = {depth_limit} ---")
        frontier = [(initial_state, 0)]
        visited = {initial_state: 0} # state -> min_depth
        parent = {initial_state: (None, None)}

        while frontier:
            state, depth = frontier.pop()
            nodes_expanded += 1
            r, c = state[0]
            dirty = state[1]

            step_log = f"Bước {nodes_expanded} (depth={depth}): Xét ({r},{c}), còn {len(dirty)} bụi"

            if style == 1 and not dirty:
                logs.append(step_log)
                path, dirs = get_path(state, parent)
                return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            if nodes_expanded >= 1000000:
                logs.append("Vượt quá giới hạn!")
                return {"found": False, "path": None, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            if depth < depth_limit:
                children = []
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                        next_state = ((nr, nc), dirty - {(nr, nc)})
                        next_depth = depth + 1

                        if next_state not in visited or next_depth < visited[next_state]:
                            visited[next_state] = next_depth
                            parent[next_state] = (state, dir_names[(dr, dc)])
                            nodes_generated += 1
                            children.append(dir_names[(dr, dc)])

                            if style == 2 and not next_state[1]:
                                logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)} | ĐẠT ĐÍCH!")
                                path, dirs = get_path(next_state, parent)
                                return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                            frontier.append((next_state, next_depth))

                logs.append(step_log + (f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."))
            else:
                logs.append(step_log + f"\n  -> Chạm giới hạn độ sâu {depth_limit}. Cắt nhánh!")

    return {"found": False, "path": None, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}


def solve_ids_stepwise(M, N, start_pos, initial_dirty, obstacles, style):
    nodes_generated = 1
    nodes_expanded = 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    def get_path(state, parent):
        path, dirs = [], []
        while state is not None:
            path.append(state[0])
            p, d = parent[state]
            if d: dirs.append(d)
            state = p
        return path[::-1], dirs[::-1]

    if not initial_dirty:
        yield {"pos": start_pos, "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "path": [start_pos], "directions": []}
        return

    initial_state = (start_pos, frozenset(initial_dirty))

    for depth_limit in range(1000):
        yield {"pos": start_pos, "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU DLS VỚI ĐỘ SÂU LIMIT = {depth_limit} ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}

        frontier = [(initial_state, 0)]
        visited = {initial_state: 0}
        parent = {initial_state: (None, None)}

        while frontier:
            state, depth = frontier.pop()
            nodes_expanded += 1
            r, c = state[0]
            dirty = state[1]

            frontier_show = ", ".join(f"({s[0][0]},{s[0][1]})[d={s[1]}]" for s in frontier[:5])
            if len(frontier) > 5:
                frontier_show += f" ... (+{len(frontier)-5} node)"
                
            log_text = f"Bước {nodes_expanded} (depth={depth}): Xét node ({r},{c}), còn {len(dirty)} ô bụi\n  -> Frontier: [{frontier_show}]"

            if style == 1 and not dirty:
                path, dirs = get_path(state, parent)
                yield {"pos": (r, c), "dirty": dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
                return

            if nodes_expanded >= 1000000:
                yield {"pos": (r, c), "dirty": dirty, "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
                return

            if depth < depth_limit:
                children = []
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                        next_state = ((nr, nc), dirty - {(nr, nc)})
                        next_depth = depth + 1

                        if next_state not in visited or next_depth < visited[next_state]:
                            visited[next_state] = next_depth
                            parent[next_state] = (state, dir_names[(dr, dc)])
                            nodes_generated += 1
                            children.append(dir_names[(dr, dc)])

                            if style == 2 and not next_state[1]:
                                path, dirs = get_path(next_state, parent)
                                yield {"pos": (nr, nc), "dirty": next_state[1], "log": log_text + f"\n  -> Sinh con: {', '.join(children)} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
                                return

                            frontier.append((next_state, next_depth))

                log_text += f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."
            else:
                log_text += f"\n  -> Chạm giới hạn độ sâu {depth_limit}. Cắt nhánh!"

            yield {"pos": (r, c), "dirty": dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}

    yield {"pos": start_pos, "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
