import time

class ColoringMetrics:
    def __init__(self):
        self.assignments = 0
        self.backtracks = 0
        self.start_time = 0.0
        self.end_time = 0.0

def solve_backtracking(districts, neighbors, colors):
    metrics = ColoringMetrics()
    metrics.start_time = time.time()
    assignment = {}

    def is_consistent(var, color, assignment):
        for nb in neighbors.get(var, []):
            if nb in assignment and assignment[nb] == color:
                return False
        return True

    def select_unassigned_variable():
        for var in districts:
            if var not in assignment:
                return var
        return None

    def backtrack():
        var = select_unassigned_variable()
        if var is None:
            return True

        for color in colors:
            metrics.assignments += 1
            if is_consistent(var, color, assignment):
                assignment[var] = color
                if backtrack():
                    return True
                del assignment[var]
                metrics.backtracks += 1
        return False

    success = backtrack()
    metrics.end_time = time.time()
    return success, assignment, metrics

def solve_backtracking_stepwise(districts, neighbors, colors):
    assignment = {}
    metrics = ColoringMetrics()
    metrics.start_time = time.time()

    def is_consistent(var, color, assignment):
        for nb in neighbors.get(var, []):
            if nb in assignment and assignment[nb] == color:
                return False
        return True

    def select_unassigned_variable():
        for var in districts:
            if var not in assignment:
                return var
        return None

    def backtrack():
        var = select_unassigned_variable()
        if var is None:
            yield {"assignment": dict(assignment), "var": None, "color": None, "action": "success", "metrics": metrics}
            return

        for color in colors:
            metrics.assignments += 1
            yield {"assignment": dict(assignment), "var": var, "color": color, "action": "try", "metrics": metrics}

            if is_consistent(var, color, assignment):
                assignment[var] = color
                yield {"assignment": dict(assignment), "var": var, "color": color, "action": "assign", "metrics": metrics}

                success = False
                for step in backtrack():
                    if step["action"] == "success":
                        success = True
                        yield step
                        return
                    yield step

                if success:
                    return

                del assignment[var]
                metrics.backtracks += 1
                yield {"assignment": dict(assignment), "var": var, "color": color, "action": "backtrack", "metrics": metrics}
            else:
                yield {"assignment": dict(assignment), "var": var, "color": color, "action": "fail_constraint", "metrics": metrics}

    yield from backtrack()
