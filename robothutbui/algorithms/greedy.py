import heapq
from .astar import heuristic

def solve_greedy(M, N, start_pos, initial_dirty, obstacles, style):
    frontier = []
    initial_state = (start_pos, frozenset(initial_dirty))
    
    tie_breaker = 0
    h_init = heuristic(start_pos, initial_dirty)
    # Priority Queue stores: (h, tie_breaker, state)
    heapq.heappush(frontier, (h_init, tie_breaker, initial_state))
    
    visited = {initial_state}
    parent = {initial_state: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    def get_path(state):
        path, dirs = [], []
        while state is not None:
            path.append(state[0])
            p, d = parent[state]
            if d: dirs.append(d)
            state = p
        return path[::-1], dirs[::-1]

    if not initial_dirty:
        return {"found": True, "path": [start_pos], "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    expanded = set()

    while frontier:
        h, _, state = heapq.heappop(frontier)
        
        if state in expanded:
            continue
        expanded.add(state)
        
        nodes_expanded += 1
        r, c = state[0]
        dirty = state[1]

        step_log = f"Bước {nodes_expanded}: Xét node ({r},{c}) [h={h}], còn {len(dirty)} ô bụi"

        if style == 1 and not dirty:
            logs.append(step_log)
            path, dirs = get_path(state)
            return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        if nodes_expanded >= 100000:
            logs.append("Vượt quá giới hạn!")
            return {"found": False, "path": None, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        children = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                next_state = ((nr, nc), dirty - {(nr, nc)})

                if next_state not in visited:
                    visited.add(next_state)
                    parent[next_state] = (state, dir_names[(dr, dc)])
                    nodes_generated += 1
                    children.append(dir_names[(dr, dc)])

                    if style == 2 and not next_state[1]:
                        logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)} | ĐẠT ĐÍCH!")
                        path, dirs = get_path(next_state)
                        return {"found": True, "path": path, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                    tie_breaker += 1
                    next_h = heuristic((nr, nc), next_state[1])
                    heapq.heappush(frontier, (next_h, tie_breaker, next_state))

        logs.append(step_log + (f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."))

    return {"found": False, "path": None, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}


def solve_greedy_stepwise(M, N, start_pos, initial_dirty, obstacles, style):
    frontier = []
    initial_state = (start_pos, frozenset(initial_dirty))
    
    tie_breaker = 0
    h_init = heuristic(start_pos, initial_dirty)
    heapq.heappush(frontier, (h_init, tie_breaker, initial_state))
    
    visited = {initial_state}
    parent = {initial_state: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    def get_path(state):
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

    expanded = set()

    while frontier:
        h, _, state = heapq.heappop(frontier)
        
        if state in expanded:
            continue
        expanded.add(state)
        
        nodes_expanded += 1
        r, c = state[0]
        dirty = state[1]

        sorted_frontier = sorted(frontier, key=lambda x: x[0])
        frontier_show = ", ".join(f"({s[2][0][0]},{s[2][0][1]})[h={s[0]}]" for s in sorted_frontier[:5])
        if len(frontier) > 5:
            frontier_show += f" ... (+{len(frontier)-5} node)"

        log_text = f"Bước {nodes_expanded}: Xét node ({r},{c}) [h={h}], còn {len(dirty)} ô bụi\n  -> Frontier: [{frontier_show}]"

        if style == 1 and not dirty:
            path, dirs = get_path(state)
            yield {"pos": (r, c), "dirty": dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
            return

        if nodes_expanded >= 100000:
            yield {"pos": (r, c), "dirty": dirty, "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
            return

        children = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                next_state = ((nr, nc), dirty - {(nr, nc)})

                if next_state not in visited:
                    visited.add(next_state)
                    parent[next_state] = (state, dir_names[(dr, dc)])
                    nodes_generated += 1
                    children.append(dir_names[(dr, dc)])

                    if style == 2 and not next_state[1]:
                        path, dirs = get_path(next_state)
                        yield {"pos": (nr, nc), "dirty": next_state[1], "log": log_text + f"\n  -> Sinh con: {', '.join(children)} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": path, "directions": dirs}
                        return

                    tie_breaker += 1
                    next_h = heuristic((nr, nc), next_state[1])
                    heapq.heappush(frontier, (next_h, tie_breaker, next_state))

        log_text += f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."
        yield {"pos": (r, c), "dirty": dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}

    yield {"pos": start_pos, "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}
