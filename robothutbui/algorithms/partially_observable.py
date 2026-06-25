import random

def get_blocked_directions(pos, M, N, obstacles):
    r, c = pos
    blocked = []
    directions = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    for d, (dr, dc) in directions.items():
        nr, nc = r + dr, c + dc
        if not (0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles):
            blocked.append(d)
    return frozenset(blocked)

def get_percept(pos, dirty, M, N, obstacles):
    is_dirty = pos in dirty
    blocked_dirs = get_blocked_directions(pos, M, N, obstacles)
    return (is_dirty, blocked_dirs)

def predict_belief_state(b, action, M, N, obstacles):
    directions = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    b_pred = []
    for pos, dirty in b:
        r, c = pos
        if action == "Suck":
            next_pos = pos
            next_dirty = dirty - {pos}
        else:
            dr, dc = directions[action]
            nr, nc = r + dr, c + dc
            if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                next_pos = (nr, nc)
            else:
                next_pos = pos
            next_dirty = dirty
        b_pred.append((next_pos, frozenset(next_dirty)))
    return frozenset(b_pred)

def update_belief_state(b_pred, percept, M, N, obstacles):
    is_dirty, blocked_dirs = percept
    b_updated = []
    for pos, dirty in b_pred:
        state_is_dirty = pos in dirty
        if state_is_dirty != is_dirty:
            continue
        state_blocked = get_blocked_directions(pos, M, N, obstacles)
        if state_blocked != blocked_dirs:
            continue
        b_updated.append((pos, dirty))
    return frozenset(b_updated)

def solve_partially_observable(M, N, start_pos, initial_dirty, obstacles):
    initial_dirty = frozenset(initial_dirty)
    initial_percept = get_percept(start_pos, initial_dirty, M, N, obstacles)

    b0_list = []
    for r in range(M):
        for c in range(N):
            if (r, c) not in obstacles:
                cand_percept = get_percept((r, c), initial_dirty, M, N, obstacles)
                if cand_percept == initial_percept:
                    b0_list.append(((r, c), initial_dirty))
    b0 = frozenset(b0_list)

    nodes_generated = 1
    nodes_expanded = 0
    logs = []
    memo = {}

    actions = ["U", "D", "L", "R", "Suck"]

    def or_search(b, path):
        nonlocal nodes_expanded, nodes_generated

        if all(len(dirty) == 0 for pos, dirty in b):
            return []

        if b in path:
            return None

        if b in memo:
            return memo[b]

        nodes_expanded += 1
        max_dirt = max(len(dirty) for pos, dirty in b) if b else 0
        logs.append(f"Xét OR_node belief_state cỡ {len(b)} (bụi tối đa: {max_dirt})")

        if nodes_expanded >= 5000:
            logs.append("Vượt quá giới hạn số bước duyệt của hệ thống!")
            return None

        for action in actions:
            b_pred = predict_belief_state(b, action, M, N, obstacles)

            possible_percepts = {}
            for pos, dirty in b_pred:
                percept = get_percept(pos, dirty, M, N, obstacles)
                if percept not in possible_percepts:
                    possible_percepts[percept] = []
                possible_percepts[percept].append((pos, dirty))

            percept_belief_states = {}
            for percept, states_list in possible_percepts.items():
                percept_belief_states[percept] = frozenset(states_list)

            nodes_generated += len(percept_belief_states)

            plan = and_search(percept_belief_states, path + [b])
            if plan is not None:
                solution = [action, plan]
                memo[b] = solution
                return solution

        memo[b] = None
        return None

    def and_search(percept_belief_states, path):
        plans = {}
        for percept, b_next in percept_belief_states.items():
            plan_b = or_search(b_next, path)
            if plan_b is None:
                return None
            plans[percept] = plan_b
        return plans

    plan = or_search(b0, [])

    if plan is not None:
        return {
            "found": True,
            "plan": plan,
            "exploration_log": logs,
            "nodes_gen": nodes_generated,
            "nodes_exp": nodes_expanded,
            "b0": b0
        }
    else:
        return {
            "found": False,
            "plan": None,
            "exploration_log": logs,
            "nodes_gen": nodes_generated,
            "nodes_exp": nodes_expanded,
            "b0": b0
        }
