import random
import heapq
import math
from collections import deque

def heuristic(pos, dirty):
    if not dirty:
        return 0
    min_dist = min(abs(pos[0] - d[0]) + abs(pos[1] - d[1]) for d in dirty)
    return min_dist + len(dirty) - 1

def heuristic_belief_state(b):
    if not b:
        return 0
    return max(heuristic(pos, dirty) for pos, dirty in b)

def get_initial_belief_state(M, N, initial_dirty, obstacles):
    initial_dirty = frozenset(initial_dirty)
    b0 = []
    for r in range(M):
        for c in range(N):
            if (r, c) not in obstacles:
                dirty = initial_dirty - {(r, c)}
                b0.append(((r, c), frozenset(dirty)))
    return frozenset(b0)

def transition_belief_state(b, action, M, N, obstacles):
    directions = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    dr, dc = directions[action]
    new_states = []
    for pos, dirty in b:
        r, c = pos
        nr, nc = r + dr, c + dc
        if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
            new_pos = (nr, nc)
        else:
            new_pos = pos
        new_dirty = dirty - {new_pos}
        new_states.append((new_pos, frozenset(new_dirty)))
    return frozenset(new_states)

def is_goal_belief_state(b):
    return all(len(dirty) == 0 for pos, dirty in b)


def solve_bfs_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    frontier = deque([b0])
    visited = {b0}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        b = frontier.popleft()
        nodes_expanded += 1

        step_log = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}), còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa"

        if style == 1 and is_goal_belief_state(b):
            logs.append(step_log)
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        if nodes_expanded >= 20000:
            logs.append("Vượt quá giới hạn!")
            return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        children = []
        for act in actions:
            next_b = transition_belief_state(b, act, M, N, obstacles)
            if next_b not in visited:
                visited.add(next_b)
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)} | ĐẠT ĐÍCH!")
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                frontier.append(next_b)

        logs.append(step_log + (f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."))

    return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_bfs_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    frontier = deque([b0])
    visited = {b0}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        b = frontier.popleft()
        nodes_expanded += 1

        frontier_show = ", ".join(f"[cỡ {len(s)}]" for s in list(frontier)[:5])
        if len(frontier) > 5:
            frontier_show += f" ... (+{len(frontier)-5} belief states)"

        log_text = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}), {max(len(dirty) for pos, dirty in b)} ô bụi tối đa\n  -> Frontier: [{frontier_show}]"

        if style == 1 and is_goal_belief_state(b):
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            union_dirty = frozenset().union(*(d for p, d in b))
            yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
            return

        if nodes_expanded >= 20000:
            yield {"pos": frozenset(p for p, d in b), "dirty": frozenset().union(*(d for p, d in b)), "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
            return

        children = []
        for act in actions:
            next_b = transition_belief_state(b, act, M, N, obstacles)
            if next_b not in visited:
                visited.add(next_b)
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    union_dirty = frozenset().union(*(d for p, d in next_b))
                    yield {"pos": frozenset(p for p, d in next_b), "dirty": union_dirty, "log": log_text + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                    return

                frontier.append(next_b)

        log_text += f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."
        union_dirty = frozenset().union(*(d for p, d in b))
        yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_dfs_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    frontier = [b0]
    visited = {b0}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        b = frontier.pop()
        nodes_expanded += 1

        step_log = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}), còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa"

        if style == 1 and is_goal_belief_state(b):
            logs.append(step_log)
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        if nodes_expanded >= 20000:
            logs.append("Vượt quá giới hạn!")
            return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        children = []
        for act in reversed(actions):
            next_b = transition_belief_state(b, act, M, N, obstacles)
            if next_b not in visited:
                visited.add(next_b)
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    logs.append(step_log + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!")
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                frontier.append(next_b)

        if children:
            children.reverse()
            logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)}")
        else:
            logs.append(step_log + "\n  -> Không sinh thêm con.")

    return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_dfs_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    frontier = [b0]
    visited = {b0}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        b = frontier.pop()
        nodes_expanded += 1

        frontier_show = ", ".join(f"[cỡ {len(s)}]" for s in reversed(frontier[-5:]))
        if len(frontier) > 5:
            frontier_show += f" ... (+{len(frontier)-5} belief states)"

        log_text = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}), {max(len(dirty) for pos, dirty in b)} ô bụi tối đa\n  -> Frontier: [{frontier_show}]"

        if style == 1 and is_goal_belief_state(b):
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            union_dirty = frozenset().union(*(d for p, d in b))
            yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
            return

        if nodes_expanded >= 20000:
            yield {"pos": frozenset(p for p, d in b), "dirty": frozenset().union(*(d for p, d in b)), "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
            return

        children = []
        for act in reversed(actions):
            next_b = transition_belief_state(b, act, M, N, obstacles)
            if next_b not in visited:
                visited.add(next_b)
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    union_dirty = frozenset().union(*(d for p, d in next_b))
                    yield {"pos": frozenset(p for p, d in next_b), "dirty": union_dirty, "log": log_text + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                    return

                frontier.append(next_b)

        if children:
            children.reverse()
            log_text += f"\n  -> Sinh con: {', '.join(children)}"
        else:
            log_text += "\n  -> Không sinh thêm con."

        union_dirty = frozenset().union(*(d for p, d in b))
        yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_ids_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    actions = ['U', 'D', 'L', 'R']

    limit = 0
    max_limit = 50

    while limit <= max_limit:
        logs.append(f"--- BẮT ĐẦU IDS VỚI LIMIT = {limit} ---")
        stack = [(b0, 0, [b0], [])]

        while stack:
            b, depth, path_list, dirs = stack.pop()
            nodes_expanded += 1

            step_log = f"Bước {nodes_expanded} (limit={limit}, depth={depth}): Xét belief state (cỡ {len(b)}), còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa"

            if style == 1 and is_goal_belief_state(b):
                logs.append(step_log + " | ĐẠT ĐÍCH!")
                return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            if nodes_expanded >= 20000:
                logs.append("Vượt quá giới hạn!")
                return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            if depth >= limit:
                continue

            children = []
            for act in reversed(actions):
                next_b = transition_belief_state(b, act, M, N, obstacles)
                if next_b not in path_list:
                    nodes_generated += 1
                    children.append(act)

                    if style == 2 and is_goal_belief_state(next_b):
                        logs.append(step_log + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!")
                        return {"found": True, "directions": dirs + [act], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                    stack.append((next_b, depth + 1, path_list + [next_b], dirs + [act]))

            if children:
                children.reverse()
                logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)}")
            else:
                logs.append(step_log + "\n  -> Không sinh thêm con.")

        limit += 1

    return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_ids_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    nodes_generated = 1
    nodes_expanded = 0
    actions = ['U', 'D', 'L', 'R']

    limit = 0
    max_limit = 50

    while limit <= max_limit:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU IDS VỚI LIMIT = {limit} ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

        stack = [(b0, 0, [b0], [])]

        while stack:
            b, depth, path_list, dirs = stack.pop()
            nodes_expanded += 1

            stack_show = ", ".join(f"[cỡ {len(s[0])}]" for s in reversed(stack[-4:]))
            if len(stack) > 4:
                stack_show += f" ... (+{len(stack)-4} belief states)"

            log_text = f"Bước {nodes_expanded} (limit={limit}, depth={depth}): Xét belief state (cỡ {len(b)}), còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa\n  -> Stack: [{stack_show}]"

            if style == 1 and is_goal_belief_state(b):
                union_dirty = frozenset().union(*(d for p, d in b))
                yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                return

            if nodes_expanded >= 20000:
                yield {"pos": frozenset(p for p, d in b), "dirty": frozenset().union(*(d for p, d in b)), "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
                return

            if depth >= limit:
                union_dirty = frozenset().union(*(d for p, d in b))
                yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + f"\n  -> Đạt độ sâu limit={limit}. Quay lui!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
                continue

            children = []
            for act in reversed(actions):
                next_b = transition_belief_state(b, act, M, N, obstacles)
                if next_b not in path_list:
                    nodes_generated += 1
                    children.append(act)

                    if style == 2 and is_goal_belief_state(next_b):
                        union_dirty = frozenset().union(*(d for p, d in next_b))
                        yield {"pos": frozenset(p for p, d in next_b), "dirty": union_dirty, "log": log_text + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs + [act]}
                        return

                    stack.append((next_b, depth + 1, path_list + [next_b], dirs + [act]))

            if children:
                children.reverse()
                log_text += f"\n  -> Sinh con: {', '.join(children)}"
            else:
                log_text += "\n  -> Không sinh thêm con."

            union_dirty = frozenset().union(*(d for p, d in b))
            yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

        limit += 1

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_ucs_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    frontier = []
    tie_breaker = 0
    heapq.heappush(frontier, (0, tie_breaker, b0))
    best_cost = {b0: 0}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    expanded = set()
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        cost, _, b = heapq.heappop(frontier)
        if b in expanded:
            continue
        expanded.add(b)
        nodes_expanded += 1

        step_log = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}) [g={cost}], còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa"

        if style == 1 and is_goal_belief_state(b):
            logs.append(step_log)
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        if nodes_expanded >= 20000:
            logs.append("Vượt quá giới hạn!")
            return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        children = []
        for act in actions:
            next_b = transition_belief_state(b, act, M, N, obstacles)
            next_cost = cost + 1
            if next_b not in best_cost or next_cost < best_cost[next_b]:
                best_cost[next_b] = next_cost
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)} | ĐẠT ĐÍCH!")
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                tie_breaker += 1
                heapq.heappush(frontier, (next_cost, tie_breaker, next_b))

        logs.append(step_log + (f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."))

    return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_ucs_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    frontier = []
    tie_breaker = 0
    heapq.heappush(frontier, (0, tie_breaker, b0))
    best_cost = {b0: 0}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    expanded = set()
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        cost, _, b = heapq.heappop(frontier)
        if b in expanded:
            continue
        expanded.add(b)
        nodes_expanded += 1

        sorted_frontier = sorted(frontier, key=lambda x: x[0])
        frontier_show = ", ".join(f"[cỡ {len(s[2])}][g={s[0]}]" for s in sorted_frontier[:5])
        if len(frontier) > 5:
            frontier_show += f" ... (+{len(frontier)-5} belief states)"

        log_text = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}) [g={cost}], còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa\n  -> Frontier: [{frontier_show}]"

        if style == 1 and is_goal_belief_state(b):
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            union_dirty = frozenset().union(*(d for p, d in b))
            yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
            return

        if nodes_expanded >= 20000:
            yield {"pos": frozenset(p for p, d in b), "dirty": frozenset().union(*(d for p, d in b)), "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
            return

        children = []
        for act in actions:
            next_b = transition_belief_state(b, act, M, N, obstacles)
            next_cost = cost + 1
            if next_b not in best_cost or next_cost < best_cost[next_b]:
                best_cost[next_b] = next_cost
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    union_dirty = frozenset().union(*(d for p, d in next_b))
                    yield {"pos": frozenset(p for p, d in next_b), "dirty": union_dirty, "log": log_text + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                    return

                tie_breaker += 1
                heapq.heappush(frontier, (next_cost, tie_breaker, next_b))

        log_text += f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."
        union_dirty = frozenset().union(*(d for p, d in b))
        yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_astar_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    frontier = []
    tie_breaker = 0
    h_init = heuristic_belief_state(b0)
    heapq.heappush(frontier, (h_init, tie_breaker, 0, b0))
    best_cost = {b0: 0}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    expanded = set()
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        f, _, g, b = heapq.heappop(frontier)
        if b in expanded:
            continue
        expanded.add(b)
        nodes_expanded += 1

        h = heuristic_belief_state(b)
        step_log = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}) [f={f}, g={g}, h={h}], còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa"

        if style == 1 and is_goal_belief_state(b):
            logs.append(step_log)
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        if nodes_expanded >= 20000:
            logs.append("Vượt quá giới hạn!")
            return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        children = []
        for act in actions:
            next_b = transition_belief_state(b, act, M, N, obstacles)
            next_g = g + 1
            if next_b not in best_cost or next_g < best_cost[next_b]:
                best_cost[next_b] = next_g
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)} | ĐẠT ĐÍCH!")
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                tie_breaker += 1
                next_h = heuristic_belief_state(next_b)
                next_f = next_g + next_h
                heapq.heappush(frontier, (next_f, tie_breaker, next_g, next_b))

        logs.append(step_log + (f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."))

    return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_astar_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    frontier = []
    tie_breaker = 0
    h_init = heuristic_belief_state(b0)
    heapq.heappush(frontier, (h_init, tie_breaker, 0, b0))
    best_cost = {b0: 0}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    expanded = set()
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        f, _, g, b = heapq.heappop(frontier)
        if b in expanded:
            continue
        expanded.add(b)
        nodes_expanded += 1

        h = heuristic_belief_state(b)
        sorted_frontier = sorted(frontier, key=lambda x: x[0])
        frontier_show = ", ".join(f"[cỡ {len(s[3])}][f={s[0]},g={s[2]}]" for s in sorted_frontier[:5])
        if len(frontier) > 5:
            frontier_show += f" ... (+{len(frontier)-5} belief states)"

        log_text = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}) [f={f}, g={g}, h={h}], còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa\n  -> Frontier: [{frontier_show}]"

        if style == 1 and is_goal_belief_state(b):
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            union_dirty = frozenset().union(*(d for p, d in b))
            yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
            return

        if nodes_expanded >= 20000:
            yield {"pos": frozenset(p for p, d in b), "dirty": frozenset().union(*(d for p, d in b)), "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
            return

        children = []
        for act in actions:
            next_b = transition_belief_state(b, act, M, N, obstacles)
            next_g = g + 1
            if next_b not in best_cost or next_g < best_cost[next_b]:
                best_cost[next_b] = next_g
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    union_dirty = frozenset().union(*(d for p, d in next_b))
                    yield {"pos": frozenset(p for p, d in next_b), "dirty": union_dirty, "log": log_text + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                    return

                tie_breaker += 1
                next_h = heuristic_belief_state(next_b)
                next_f = next_g + next_h
                heapq.heappush(frontier, (next_f, tie_breaker, next_g, next_b))

        log_text += f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."
        union_dirty = frozenset().union(*(d for p, d in b))
        yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_greedy_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    frontier = []
    tie_breaker = 0
    h_init = heuristic_belief_state(b0)
    heapq.heappush(frontier, (h_init, tie_breaker, b0))
    best_h = {b0: h_init}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    expanded = set()
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        h, _, b = heapq.heappop(frontier)
        if b in expanded:
            continue
        expanded.add(b)
        nodes_expanded += 1

        step_log = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}) [h={h}], còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa"

        if style == 1 and is_goal_belief_state(b):
            logs.append(step_log)
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        if nodes_expanded >= 20000:
            logs.append("Vượt quá giới hạn!")
            return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        children = []
        for act in actions:
            next_b = transition_belief_state(b, act, M, N, obstacles)
            next_h = heuristic_belief_state(next_b)
            if next_b not in best_h or next_h < best_h[next_b]:
                best_h[next_b] = next_h
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)} | ĐẠT ĐÍCH!")
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                tie_breaker += 1
                heapq.heappush(frontier, (next_h, tie_breaker, next_b))

        logs.append(step_log + (f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."))

    return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_greedy_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    frontier = []
    tie_breaker = 0
    h_init = heuristic_belief_state(b0)
    heapq.heappush(frontier, (h_init, tie_breaker, b0))
    best_h = {b0: h_init}
    parent = {b0: (None, None)}

    nodes_generated = 1
    nodes_expanded = 0
    expanded = set()
    actions = ['U', 'D', 'L', 'R']

    while frontier:
        h, _, b = heapq.heappop(frontier)
        if b in expanded:
            continue
        expanded.add(b)
        nodes_expanded += 1

        sorted_frontier = sorted(frontier, key=lambda x: x[0])
        frontier_show = ", ".join(f"[cỡ {len(s[2])}][h={s[0]}]" for s in sorted_frontier[:5])
        if len(frontier) > 5:
            frontier_show += f" ... (+{len(frontier)-5} belief states)"

        log_text = f"Bước {nodes_expanded}: Xét belief state (cỡ {len(b)}) [h={h}], còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa\n  -> Frontier: [{frontier_show}]"

        if style == 1 and is_goal_belief_state(b):
            dirs = []
            curr = b
            while curr in parent and parent[curr][0] is not None:
                p, act = parent[curr]
                dirs.append(act)
                curr = p
            dirs.reverse()
            union_dirty = frozenset().union(*(d for p, d in b))
            yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
            return

        if nodes_expanded >= 20000:
            yield {"pos": frozenset(p for p, d in b), "dirty": frozenset().union(*(d for p, d in b)), "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
            return

        children = []
        for act in actions:
            next_b = transition_belief_state(b, act, M, N, obstacles)
            next_h = heuristic_belief_state(next_b)
            if next_b not in best_h or next_h < best_h[next_b]:
                best_h[next_b] = next_h
                parent[next_b] = (b, act)
                nodes_generated += 1
                children.append(act)

                if style == 2 and is_goal_belief_state(next_b):
                    dirs = []
                    curr = next_b
                    while curr in parent and parent[curr][0] is not None:
                        p, act_p = parent[curr]
                        dirs.append(act_p)
                        curr = p
                    dirs.reverse()
                    union_dirty = frozenset().union(*(d for p, d in next_b))
                    yield {"pos": frozenset(p for p, d in next_b), "dirty": union_dirty, "log": log_text + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                    return

                tie_breaker += 1
                heapq.heappush(frontier, (next_h, tie_breaker, next_b))

        log_text += f"\n  -> Sinh con: {', '.join(children)}" if children else "\n  -> Không sinh thêm con."
        union_dirty = frozenset().union(*(d for p, d in b))
        yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_idastar_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    limit = heuristic_belief_state(b0)
    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    actions = ['U', 'D', 'L', 'R']

    while True:
        logs.append(f"--- BẮT ĐẦU IDA* VỚI F-LIMIT = {limit} ---")
        stack = [(b0, 0, [b0], [])]
        next_limit = float('inf')
        visited = {b0: 0}

        while stack:
            b, g, path_list, dirs = stack.pop()
            nodes_expanded += 1

            h = heuristic_belief_state(b)
            f = g + h

            step_log = f"Bước {nodes_expanded} (limit={limit}): Xét belief state (cỡ {len(b)}) [f={f}, g={g}, h={h}], còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa"

            if style == 1 and is_goal_belief_state(b):
                logs.append(step_log + " | ĐẠT ĐÍCH!")
                return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            if nodes_expanded >= 20000:
                logs.append("Vượt quá giới hạn!")
                return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            if f > limit:
                next_limit = min(next_limit, f)
                logs.append(step_log + f"\n  -> f={f} > limit={limit}. Cắt nhánh!")
                continue

            children = []
            for act in reversed(actions):
                next_b = transition_belief_state(b, act, M, N, obstacles)
                next_g = g + 1
                if next_b not in path_list:
                    if next_b not in visited or next_g < visited[next_b]:
                        visited[next_b] = next_g
                        nodes_generated += 1
                        children.append(act)

                        if style == 2 and is_goal_belief_state(next_b):
                            logs.append(step_log + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!")
                            return {"found": True, "directions": dirs + [act], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

                        stack.append((next_b, next_g, path_list + [next_b], dirs + [act]))

            if children:
                children.reverse()
                logs.append(step_log + f"\n  -> Sinh con: {', '.join(children)}")
            else:
                logs.append(step_log + "\n  -> Không sinh thêm con.")

        if next_limit == float('inf'):
            break
        limit = next_limit

    return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_idastar_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    limit = heuristic_belief_state(b0)
    nodes_generated = 1
    nodes_expanded = 0
    actions = ['U', 'D', 'L', 'R']

    while True:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU IDA* VỚI F-LIMIT = {limit} ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

        stack = [(b0, 0, [b0], [])]
        next_limit = float('inf')
        visited = {b0: 0}

        while stack:
            b, g, path_list, dirs = stack.pop()
            nodes_expanded += 1

            h = heuristic_belief_state(b)
            f = g + h

            stack_show = ", ".join(f"[cỡ {len(s[0])}][f={s[1]+heuristic_belief_state(s[0])}]" for s in reversed(stack[-4:]))
            if len(stack) > 4:
                stack_show += f" ... (+{len(stack)-4} belief states)"

            log_text = f"Bước {nodes_expanded} (limit={limit}): Xét belief state (cỡ {len(b)}) [f={f}, g={g}, h={h}], còn {max(len(dirty) for pos, dirty in b)} ô bụi tối đa\n  -> Stack: [{stack_show}]"

            if style == 1 and is_goal_belief_state(b):
                union_dirty = frozenset().union(*(d for p, d in b))
                yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                return

            if nodes_expanded >= 20000:
                yield {"pos": frozenset(p for p, d in b), "dirty": frozenset().union(*(d for p, d in b)), "log": log_text + " -> Vượt quá giới hạn!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
                return

            if f > limit:
                next_limit = min(next_limit, f)
                union_dirty = frozenset().union(*(d for p, d in b))
                yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text + f"\n  -> f={f} > limit={limit}. Cắt nhánh!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
                continue

            children = []
            for act in reversed(actions):
                next_b = transition_belief_state(b, act, M, N, obstacles)
                next_g = g + 1
                if next_b not in path_list:
                    if next_b not in visited or next_g < visited[next_b]:
                        visited[next_b] = next_g
                        nodes_generated += 1
                        children.append(act)

                        if style == 2 and is_goal_belief_state(next_b):
                            union_dirty = frozenset().union(*(d for p, d in next_b))
                            yield {"pos": frozenset(p for p, d in next_b), "dirty": union_dirty, "log": log_text + f"\n  -> Sinh con: {act} | ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs + [act]}
                            return

                        stack.append((next_b, next_g, path_list + [next_b], dirs + [act]))

            if children:
                children.reverse()
                log_text += f"\n  -> Sinh con: {', '.join(children)}"
            else:
                log_text += "\n  -> Không sinh thêm con."

            union_dirty = frozenset().union(*(d for p, d in b))
            yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

        if next_limit == float('inf'):
            break
        limit = next_limit

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_hill_climbing_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    actions = ['U', 'D', 'L', 'R']

    current_b = b0
    dirs = []

    style_name = {1: "Leo đồi ĐƠN GIẢN", 2: "Leo đồi DỐC NHẤT", 3: "Leo đồi NGẪU NHIÊN"}.get(style, "Hill Climbing")
    logs.append(f"--- BẮT ĐẦU {style_name} (Không trạng thái ban đầu) ---")

    while True:
        h = heuristic_belief_state(current_b)
        nodes_expanded += 1
        step_log = f"Bước {nodes_expanded}: Belief state cỡ {len(current_b)} [h={h}], còn {max(len(dirty) for pos, dirty in current_b)} ô bụi tối đa"

        if is_goal_belief_state(current_b):
            logs.append(step_log + " | ĐẠT ĐÍCH!")
            return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        valid_neighbors = []
        for act in actions:
            next_b = transition_belief_state(current_b, act, M, N, obstacles)
            next_h = heuristic_belief_state(next_b)
            valid_neighbors.append({
                "b": next_b,
                "h": next_h,
                "dir": act
            })
            nodes_generated += 1

        next_step = None
        if style == 1:
            for neighbor in valid_neighbors:
                if neighbor["h"] < h:
                    next_step = neighbor
                    break
            if next_step:
                logs.append(step_log + f"\n  -> Chọn ngay {next_step['dir']} [h={next_step['h']} < {h}]")
        elif style == 2:
            better = [n for n in valid_neighbors if n["h"] < h]
            if better:
                better.sort(key=lambda x: x["h"])
                next_step = better[0]
                logs.append(step_log + f"\n  -> Chọn dốc nhất {next_step['dir']} [h={next_step['h']} < {h}]")
        elif style == 3:
            better = [n for n in valid_neighbors if n["h"] < h]
            if better:
                next_step = random.choice(better)
                logs.append(step_log + f"\n  -> Chọn ngẫu nhiên {next_step['dir']} [h={next_step['h']} < {h}]")

        if next_step is None:
            logs.append(step_log + "\n  -> BỊ KẸT TẠI CỰC TRỊ ĐỊA PHƯƠNG! Không có hướng nào tốt hơn.")
            return {"found": False, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        current_b = next_step["b"]
        dirs.append(next_step["dir"])

def solve_hill_climbing_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    nodes_generated = 1
    nodes_expanded = 0
    actions = ['U', 'D', 'L', 'R']

    current_b = b0
    dirs = []

    style_name = {1: "Leo đồi ĐƠN GIẢN", 2: "Leo đồi DỐC NHẤT", 3: "Leo đồi NGẪU NHIÊN"}.get(style, "Hill Climbing")
    yield {"pos": frozenset(p for p, d in current_b), "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU {style_name} (Không trạng thái ban đầu) ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    while True:
        h = heuristic_belief_state(current_b)
        nodes_expanded += 1
        log_text = f"Bước {nodes_expanded}: Belief state cỡ {len(current_b)} [h={h}], còn {max(len(dirty) for pos, dirty in current_b)} ô bụi tối đa"

        if is_goal_belief_state(current_b):
            union_dirty = frozenset().union(*(d for p, d in current_b))
            yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
            return

        valid_neighbors = []
        for act in actions:
            next_b = transition_belief_state(current_b, act, M, N, obstacles)
            next_h = heuristic_belief_state(next_b)
            valid_neighbors.append({
                "b": next_b,
                "h": next_h,
                "dir": act
            })
            nodes_generated += 1

        next_step = None
        if style == 1:
            for neighbor in valid_neighbors:
                if neighbor["h"] < h:
                    next_step = neighbor
                    break
            if next_step:
                log_text += f"\n  -> Chọn ngay {next_step['dir']} [h={next_step['h']} < {h}]"
        elif style == 2:
            better = [n for n in valid_neighbors if n["h"] < h]
            if better:
                better.sort(key=lambda x: x["h"])
                next_step = better[0]
                log_text += f"\n  -> Chọn dốc nhất {next_step['dir']} [h={next_step['h']} < {h}]"
        elif style == 3:
            better = [n for n in valid_neighbors if n["h"] < h]
            if better:
                next_step = random.choice(better)
                log_text += f"\n  -> Chọn ngẫu nhiên {next_step['dir']} [h={next_step['h']} < {h}]"

        if next_step is None:
            union_dirty = frozenset().union(*(d for p, d in current_b))
            yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_text + "\n  -> BỊ KẸT TẠI CỰC TRỊ ĐỊA PHƯƠNG! Không có hướng nào tốt hơn.", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
            return

        current_b = next_step["b"]
        dirs.append(next_step["dir"])
        union_dirty = frozenset().union(*(d for p, d in current_b))
        yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_random_restart_hill_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    max_restarts = 20
    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    actions = ['U', 'D', 'L', 'R']

    style_name = {1: "Leo đồi ĐƠN GIẢN", 2: "Leo đồi DỐC NHẤT", 3: "Leo đồi NGẪU NHIÊN"}.get(style, "Hill Climbing")
    logs.append(f"--- BẮT ĐẦU Random Restart Hill Climbing ({style_name}) (Không trạng thái ban đầu) ---")

    current_b = b0
    dirs = []
    restart_count = 0

    while True:
        sub_dirs = []
        sub_b = current_b
        stuck = False

        while True:
            h = heuristic_belief_state(sub_b)
            nodes_expanded += 1
            step_log = f"Restart {restart_count}: Bước {nodes_expanded}: Belief state cỡ {len(sub_b)} [h={h}], còn {max(len(dirty) for pos, dirty in sub_b)} ô bụi tối đa"

            if is_goal_belief_state(sub_b):
                logs.append(step_log + " | ĐẠT ĐÍCH CHÍNH!")
                dirs.extend(sub_dirs)
                return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            valid_neighbors = []
            for act in actions:
                next_b = transition_belief_state(sub_b, act, M, N, obstacles)
                next_h = heuristic_belief_state(next_b)
                valid_neighbors.append({
                    "b": next_b,
                    "h": next_h,
                    "dir": act
                })
                nodes_generated += 1

            next_step = None
            if style == 1:
                for neighbor in valid_neighbors:
                    if neighbor["h"] < h:
                        next_step = neighbor
                        break
                if next_step:
                    logs.append(step_log + f"\n  -> Chọn ngay {next_step['dir']} [h={next_step['h']} < {h}]")
            elif style == 2:
                better = [n for n in valid_neighbors if n["h"] < h]
                if better:
                    better.sort(key=lambda x: x["h"])
                    next_step = better[0]
                    logs.append(step_log + f"\n  -> Chọn dốc nhất {next_step['dir']} [h={next_step['h']} < {h}]")
            elif style == 3:
                better = [n for n in valid_neighbors if n["h"] < h]
                if better:
                    next_step = random.choice(better)
                    logs.append(step_log + f"\n  -> Chọn ngẫu nhiên {next_step['dir']} [h={next_step['h']} < {h}]")

            if next_step is None:
                logs.append(step_log + "\n  -> BỊ KẸT TẠI CỰC TRỊ ĐỊA PHƯƠNG!")
                stuck = True
                break

            sub_b = next_step["b"]
            sub_dirs.append(next_step["dir"])

        if stuck:
            dirs.extend(sub_dirs)
            current_b = sub_b

            if restart_count >= max_restarts:
                logs.append(f"--- ĐẠT GIỚI HẠN RESTARTS ({max_restarts}) ---")
                return {"found": False, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

            restart_count += 1
            logs.append(f"==> [RESTART LẦN {restart_count}] Perturbing initial belief state...")
            current_b = b0
            perturb_steps = random.randint(3, 6)
            perturb_actions = []
            for _ in range(perturb_steps):
                act = random.choice(actions)
                current_b = transition_belief_state(current_b, act, M, N, obstacles)
                perturb_actions.append(act)

            dirs.extend(perturb_actions)
            logs.append(f"  -> Áp dụng các bước ngẫu nhiên: {' -> '.join(perturb_actions)}")

            if is_goal_belief_state(current_b):
                logs.append("==> ĐẠT ĐÍCH SAU KHI RESTART!")
                return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_random_restart_hill_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    max_restarts = 20
    nodes_generated = 1
    nodes_expanded = 0
    actions = ['U', 'D', 'L', 'R']

    style_name = {1: "Leo đồi ĐƠN GIẢN", 2: "Leo đồi DỐC NHẤT", 3: "Leo đồi NGẪU NHIÊN"}.get(style, "Hill Climbing")
    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU Random Restart Hill Climbing ({style_name}) (Không trạng thái ban đầu) ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    current_b = b0
    dirs = []
    restart_count = 0

    while True:
        sub_dirs = []
        sub_b = current_b
        stuck = False

        while True:
            h = heuristic_belief_state(sub_b)
            nodes_expanded += 1
            log_text = f"Restart {restart_count}: Bước {nodes_expanded}: Belief state cỡ {len(sub_b)} [h={h}], còn {max(len(dirty) for pos, dirty in sub_b)} ô bụi tối đa"

            if is_goal_belief_state(sub_b):
                dirs.extend(sub_dirs)
                union_dirty = frozenset().union(*(d for p, d in sub_b))
                yield {"pos": frozenset(p for p, d in sub_b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH CHÍNH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                return

            valid_neighbors = []
            for act in actions:
                next_b = transition_belief_state(sub_b, act, M, N, obstacles)
                next_h = heuristic_belief_state(next_b)
                valid_neighbors.append({
                    "b": next_b,
                    "h": next_h,
                    "dir": act
                })
                nodes_generated += 1

            next_step = None
            if style == 1:
                for neighbor in valid_neighbors:
                    if neighbor["h"] < h:
                        next_step = neighbor
                        break
                if next_step:
                    log_text += f"\n  -> Chọn ngay {next_step['dir']} [h={next_step['h']} < {h}]"
            elif style == 2:
                better = [n for n in valid_neighbors if n["h"] < h]
                if better:
                    better.sort(key=lambda x: x["h"])
                    next_step = better[0]
                    log_text += f"\n  -> Chọn dốc nhất {next_step['dir']} [h={next_step['h']} < {h}]"
            elif style == 3:
                better = [n for n in valid_neighbors if n["h"] < h]
                if better:
                    next_step = random.choice(better)
                    log_text += f"\n  -> Chọn ngẫu nhiên {next_step['dir']} [h={next_step['h']} < {h}]"

            if next_step is None:
                log_text += "\n  -> BỊ KẸT TẠI CỰC TRỊ ĐỊA PHƯƠNG!"
                stuck = True
                union_dirty = frozenset().union(*(d for p, d in sub_b))
                yield {"pos": frozenset(p for p, d in sub_b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
                break

            sub_b = next_step["b"]
            sub_dirs.append(next_step["dir"])
            union_dirty = frozenset().union(*(d for p, d in sub_b))
            yield {"pos": frozenset(p for p, d in sub_b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

        if stuck:
            dirs.extend(sub_dirs)
            current_b = sub_b

            if restart_count >= max_restarts:
                union_dirty = frozenset().union(*(d for p, d in current_b))
                yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": f"--- ĐẠT GIỚI HẠN RESTARTS ({max_restarts}) ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
                return

            restart_count += 1
            current_b = b0
            perturb_steps = random.randint(3, 6)
            perturb_actions = []
            for _ in range(perturb_steps):
                act = random.choice(actions)
                current_b = transition_belief_state(current_b, act, M, N, obstacles)
                perturb_actions.append(act)

            dirs.extend(perturb_actions)
            log_restart = f"==> [RESTART LẦN {restart_count}] Perturbing initial belief state...\n  -> Áp dụng các bước ngẫu nhiên: {' -> '.join(perturb_actions)}"
            union_dirty = frozenset().union(*(d for p, d in current_b))
            yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_restart, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

            if is_goal_belief_state(current_b):
                union_dirty = frozenset().union(*(d for p, d in current_b))
                yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": "==> ĐẠT ĐÍCH SAU KHI RESTART!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                return


def solve_local_beam_sensorless(M, N, initial_dirty, obstacles, style):
    k = style if style in [2, 3, 4] else 3
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    actions = ['U', 'D', 'L', 'R']

    logs.append(f"--- BẮT ĐẦU Local Beam Search (k = {k}) (Không trạng thái ban đầu) ---")

    h_init = heuristic_belief_state(b0)
    candidates = [(h_init, b0, [])]

    step = 0
    while step < 1000:
        step += 1
        nodes_expanded += len(candidates)

        for h, b, dirs in candidates:
            if is_goal_belief_state(b):
                logs.append(f"Bước {step}: Phát hiện một ứng viên đạt đích! (h={h})")
                return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        successors = []
        for h, b, dirs in candidates:
            for act in actions:
                next_b = transition_belief_state(b, act, M, N, obstacles)
                next_h = heuristic_belief_state(next_b)
                successors.append((next_h, next_b, dirs + [act]))
                nodes_generated += 1

        successors.sort(key=lambda x: x[0])
        candidates = successors[:k]

        step_log = f"Bước {step}: {len(candidates)} ứng viên tốt nhất: " + ", ".join(f"[cỡ {len(c[1])} h={c[0]}]" for c in candidates)
        logs.append(step_log)

    return {"found": False, "directions": [], "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_local_beam_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    k = style if style in [2, 3, 4] else 3
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    nodes_generated = 1
    nodes_expanded = 0
    actions = ['U', 'D', 'L', 'R']

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU Local Beam Search (k = {k}) (Không trạng thái ban đầu) ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    h_init = heuristic_belief_state(b0)
    candidates = [(h_init, b0, [])]

    step = 0
    while step < 1000:
        step += 1
        nodes_expanded += len(candidates)

        for h, b, dirs in candidates:
            if is_goal_belief_state(b):
                union_dirty = frozenset().union(*(d for p, d in b))
                yield {"pos": frozenset(p for p, d in b), "dirty": union_dirty, "log": f"Bước {step}: Tìm thấy ứng viên đạt đích! (h={h})", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
                return

        successors = []
        for h, b, dirs in candidates:
            for act in actions:
                next_b = transition_belief_state(b, act, M, N, obstacles)
                next_h = heuristic_belief_state(next_b)
                successors.append((next_h, next_b, dirs + [act]))
                nodes_generated += 1

        successors.sort(key=lambda x: x[0])
        candidates = successors[:k]

        best_cand = candidates[0][1]
        log_text = f"Bước {step}: {len(candidates)} ứng viên tốt nhất: " + ", ".join(f"[cỡ {len(c[1])} h={c[0]}]" for c in candidates)

        union_dirty = frozenset().union(*(d for p, d in best_cand))
        yield {"pos": frozenset(p for p, d in best_cand), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": "Không tìm thấy đường đi!", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_simulated_annealing_sensorless(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        return {"found": True, "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    T0 = 100.0
    T = T0
    max_steps = 1000

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    actions = ['U', 'D', 'L', 'R']

    style_name = "Tuyến tính" if style == 1 else "Mũ"
    logs.append(f"--- BẮT ĐẦU Simulated Annealing (Luyện kim) - Hạ nhiệt {style_name} (Không trạng thái ban đầu) ---")

    current_b = b0
    dirs = []
    step = 0

    while step < max_steps:
        step += 1
        nodes_expanded += 1

        if style == 1:
            T = T0 * (1.0 - step / max_steps)
        else:
            T = T0 * (0.98 ** step)

        if T <= 1e-4:
            logs.append(f"Bước {step}: Nhiệt độ quá thấp (T = {T:.6f}). Dừng tìm kiếm.")
            break

        h_curr = heuristic_belief_state(current_b)
        step_log = f"Bước {step}: Belief state cỡ {len(current_b)} [h={h_curr}], T={T:.4f}, còn {max(len(dirty) for pos, dirty in current_b)} ô bụi tối đa"

        if is_goal_belief_state(current_b):
            logs.append(step_log + " | ĐẠT ĐÍCH!")
            return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

        valid_neighbors = []
        for act in actions:
            next_b = transition_belief_state(current_b, act, M, N, obstacles)
            next_h = heuristic_belief_state(next_b)
            valid_neighbors.append({
                "b": next_b,
                "h": next_h,
                "dir": act
            })
            nodes_generated += 1

        neighbor = random.choice(valid_neighbors)
        delta_E = neighbor["h"] - h_curr

        if delta_E <= 0:
            current_b = neighbor["b"]
            dirs.append(neighbor["dir"])
            logs.append(step_log + f"\n  -> [Chấp nhận] Đi {neighbor['dir']} [h={neighbor['h']} <= {h_curr}]")
        else:
            p = math.exp(-delta_E / T)
            if random.random() < p:
                current_b = neighbor["b"]
                dirs.append(neighbor["dir"])
                logs.append(step_log + f"\n  -> [Chấp nhận tệ hơn] Đi {neighbor['dir']} [h={neighbor['h']} > {h_curr}] với p={p:.4f}")
            else:
                logs.append(step_log + f"\n  -> [Từ chối] Giữ nguyên [h={neighbor['h']} > {h_curr}] với p={p:.4f}")

    if is_goal_belief_state(current_b):
        return {"found": True, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

    logs.append(f"Không thể dọn sạch bụi sau {step} bước.")
    return {"found": False, "directions": dirs, "exploration_log": logs, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded}

def solve_simulated_annealing_sensorless_stepwise(M, N, initial_dirty, obstacles, style):
    b0 = get_initial_belief_state(M, N, initial_dirty, obstacles)
    if not initial_dirty:
        yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "directions": []}
        return

    T0 = 100.0
    T = T0
    max_steps = 1000

    nodes_generated = 1
    nodes_expanded = 0
    actions = ['U', 'D', 'L', 'R']

    style_name = "Tuyến tính" if style == 1 else "Mũ"
    yield {"pos": frozenset(p for p, d in b0), "dirty": frozenset(initial_dirty), "log": f"--- BẮT ĐẦU Simulated Annealing (Luyện kim) - Hạ nhiệt {style_name} (Không trạng thái ban đầu) ---", "is_goal": False, "nodes_gen": 1, "nodes_exp": 0, "directions": []}

    current_b = b0
    dirs = []
    step = 0

    while step < max_steps:
        step += 1
        nodes_expanded += 1

        if style == 1:
            T = T0 * (1.0 - step / max_steps)
        else:
            T = T0 * (0.98 ** step)

        h_curr = heuristic_belief_state(current_b)
        log_text = f"Bước {step}: Belief state cỡ {len(current_b)} [h={h_curr}], T={T:.4f}, còn {max(len(dirty) for pos, dirty in current_b)} ô bụi tối đa"

        if is_goal_belief_state(current_b):
            union_dirty = frozenset().union(*(d for p, d in current_b))
            yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
            return

        if T <= 1e-4:
            union_dirty = frozenset().union(*(d for p, d in current_b))
            yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_text + f"\n  -> Nhiệt độ quá thấp (T = {T:.6f}). Dừng.", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}
            return

        valid_neighbors = []
        for act in actions:
            next_b = transition_belief_state(current_b, act, M, N, obstacles)
            next_h = heuristic_belief_state(next_b)
            valid_neighbors.append({
                "b": next_b,
                "h": next_h,
                "dir": act
            })
            nodes_generated += 1

        neighbor = random.choice(valid_neighbors)
        delta_E = neighbor["h"] - h_curr

        if delta_E <= 0:
            current_b = neighbor["b"]
            dirs.append(neighbor["dir"])
            log_text += f"\n  -> [Chấp nhận] Đi {neighbor['dir']} [h={neighbor['h']} <= {h_curr}]"
        else:
            p = math.exp(-delta_E / T)
            if random.random() < p:
                current_b = neighbor["b"]
                dirs.append(neighbor["dir"])
                log_text += f"\n  -> [Chấp nhận tệ hơn] Đi {neighbor['dir']} [h={neighbor['h']} > {h_curr}] với p={p:.4f}"
            else:
                log_text += f"\n  -> [Từ chối] Giữ nguyên [h={neighbor['h']} > {h_curr}] với p={p:.4f}"

        union_dirty = frozenset().union(*(d for p, d in current_b))
        yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_text, "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}

    if is_goal_belief_state(current_b):
        union_dirty = frozenset().union(*(d for p, d in current_b))
        yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_text + " -> ĐẠT ĐÍCH!", "is_goal": True, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": dirs}
    else:
        union_dirty = frozenset().union(*(d for p, d in current_b))
        yield {"pos": frozenset(p for p, d in current_b), "dirty": union_dirty, "log": log_text + f"\n  -> Kết thúc mà không dọn sạch bụi sau {step} bước.", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "directions": []}


def solve_vacuum_sensorless(M, N, initial_dirty, obstacles, algo, style):
    if algo == "BFS":
        return solve_bfs_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "DFS":
        return solve_dfs_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "IDS":
        return solve_ids_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "UCS":
        return solve_ucs_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "A*":
        return solve_astar_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "Greedy":
        return solve_greedy_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "IDA*":
        return solve_idastar_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "Hill Climbing":
        return solve_hill_climbing_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "Random Restart Hill":
        return solve_random_restart_hill_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "Local Beam Search":
        return solve_local_beam_sensorless(M, N, initial_dirty, obstacles, style)
    elif algo == "Simulated Annealing":
        return solve_simulated_annealing_sensorless(M, N, initial_dirty, obstacles, style)
    else:
        raise ValueError(f"Unknown algorithm: {algo}")

def solve_vacuum_sensorless_stepwise(M, N, initial_dirty, obstacles, algo, style):
    if algo == "BFS":
        return solve_bfs_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "DFS":
        return solve_dfs_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "IDS":
        return solve_ids_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "UCS":
        return solve_ucs_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "A*":
        return solve_astar_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "Greedy":
        return solve_greedy_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "IDA*":
        return solve_idastar_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "Hill Climbing":
        return solve_hill_climbing_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "Random Restart Hill":
        return solve_random_restart_hill_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "Local Beam Search":
        return solve_local_beam_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    elif algo == "Simulated Annealing":
        return solve_simulated_annealing_sensorless_stepwise(M, N, initial_dirty, obstacles, style)
    else:
        raise ValueError(f"Unknown algorithm: {algo}")
