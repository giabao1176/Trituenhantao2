import random

class ErraticVacuumProblem:
    def __init__(self, M, N, start_pos, initial_dirty, obstacles):
        self.M = M
        self.N = N
        self.initial_state = (start_pos, frozenset(initial_dirty))
        self.obstacles = set(obstacles)

    def goal_test(self, state):
        pos, dirty = state
        return len(dirty) == 0

    def actions(self, state):
        pos, dirty = state
        r, c = pos
        acts = []
        if r > 0 and (r - 1, c) not in self.obstacles:
            acts.append("U")
        if r < self.M - 1 and (r + 1, c) not in self.obstacles:
            acts.append("D")
        if c > 0 and (r, c - 1) not in self.obstacles:
            acts.append("L")
        if c < self.N - 1 and (r, c + 1) not in self.obstacles:
            acts.append("R")
        acts.append("Suck")
        return acts

    def results(self, state, action):
        pos, dirty = state
        r, c = pos
        if action == "U":
            next_pos = (r - 1, c)
            return [(next_pos, dirty)]
        elif action == "D":
            next_pos = (r + 1, c)
            return [(next_pos, dirty)]
        elif action == "L":
            next_pos = (r, c - 1)
            return [(next_pos, dirty)]
        elif action == "R":
            next_pos = (r, c + 1)
            return [(next_pos, dirty)]
        elif action == "Suck":
            outcomes = []
            if pos in dirty:
                clean_self = dirty - {pos}
                outcomes.append((pos, clean_self))

                neighbors = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
                dirty_neighbors = [nb for nb in neighbors if nb in clean_self]
                for nb in dirty_neighbors:
                    outcomes.append((pos, clean_self - {nb}))
            else:
                outcomes.append((pos, dirty))
                outcomes.append((pos, dirty | {pos}))

            unique_outcomes = []
            for out in outcomes:
                if out not in unique_outcomes:
                    unique_outcomes.append(out)
            return unique_outcomes

def solve_and_or(M, N, start_pos, initial_dirty, obstacles):
    problem = ErraticVacuumProblem(M, N, start_pos, initial_dirty, obstacles)

    nodes_generated = 1
    nodes_expanded = 0
    logs = []

    memo = {}

    def or_search(state, path):
        nonlocal nodes_expanded, nodes_generated

        pos, dirty = state
        step_log = f"Xét OR_node {pos}, còn {len(dirty)} ô bụi"

        if problem.goal_test(state):
            return []

        if state in path:
            return None

        if state in memo:
            return memo[state]

        nodes_expanded += 1
        logs.append(step_log)

        if nodes_expanded >= 15000:
            logs.append("Vượt quá giới hạn số bước duyệt!")
            return None

        for action in problem.actions(state):
            result_states = problem.results(state, action)
            nodes_generated += len(result_states)

            plan = and_search(result_states, path + [state])
            if plan is not None:
                solution = [action, plan]
                memo[state] = solution
                return solution

        memo[state] = None
        return None

    def and_search(states, path):
        plans = {}
        for s in states:
            plan_s = or_search(s, path)
            if plan_s is None:
                return None
            plans[s] = plan_s
        return plans

    initial_state = problem.initial_state
    plan = or_search(initial_state, [])

    if plan is not None:
        return {
            "found": True,
            "plan": plan,
            "exploration_log": logs,
            "nodes_gen": nodes_generated,
            "nodes_exp": nodes_expanded,
            "problem": problem
        }
    else:
        return {
            "found": False,
            "plan": None,
            "exploration_log": logs,
            "nodes_gen": nodes_generated,
            "nodes_exp": nodes_expanded,
            "problem": problem
        }
