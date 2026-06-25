import time
from .backtracking import ColoringMetrics

def solve_forward_checking(districts, neighbors, colors):
    metrics = ColoringMetrics()
    metrics.start_time = time.time()
    assignment = {}
    domains = {var: list(colors) for var in districts}

    def select_unassigned_variable():
        for var in districts:
            if var not in assignment:
                return var
        return None

    def backtrack_fc(domains_curr):
        var = select_unassigned_variable()
        if var is None:
            return True

        for color in domains_curr[var]:
            metrics.assignments += 1
            assignment[var] = color

            new_domains = {v: list(d) for v, d in domains_curr.items()}
            new_domains[var] = [color]

            consistent = True
            for nb in neighbors.get(var, []):
                if nb not in assignment:
                    if color in new_domains[nb]:
                        new_domains[nb].remove(color)
                        if not new_domains[nb]:
                            consistent = False
                            break

            if consistent:
                if backtrack_fc(new_domains):
                    return True

            del assignment[var]
            metrics.backtracks += 1

        return False

    success = backtrack_fc(domains)
    metrics.end_time = time.time()
    return success, assignment, metrics

def solve_forward_checking_stepwise(districts, neighbors, colors):
    assignment = {}
    metrics = ColoringMetrics()
    metrics.start_time = time.time()
    domains = {var: list(colors) for var in districts}

    def select_unassigned_variable():
        for var in districts:
            if var not in assignment:
                return var
        return None

    def backtrack_fc(domains_curr):
        var = select_unassigned_variable()
        if var is None:
            yield {"assignment": dict(assignment), "domains": domains_curr, "var": None, "color": None, "action": "success", "metrics": metrics}
            return

        for color in domains_curr[var]:
            metrics.assignments += 1
            yield {"assignment": dict(assignment), "domains": domains_curr, "var": var, "color": color, "action": "try", "metrics": metrics}

            new_domains = {v: list(d) for v, d in domains_curr.items()}
            new_domains[var] = [color]

            consistent = True
            pruned = []
            for nb in neighbors.get(var, []):
                if nb not in assignment:
                    if color in new_domains[nb]:
                        new_domains[nb].remove(color)
                        pruned.append(nb)
                        if not new_domains[nb]:
                            consistent = False
                            break

            if consistent:
                assignment[var] = color
                yield {"assignment": dict(assignment), "domains": new_domains, "var": var, "color": color, "action": "assign", "metrics": metrics}

                success = False
                for step in backtrack_fc(new_domains):
                    if step["action"] == "success":
                        success = True
                        yield step
                        return
                    yield step

                if success:
                    return

                del assignment[var]
                metrics.backtracks += 1
                yield {"assignment": dict(assignment), "domains": domains_curr, "var": var, "color": color, "action": "backtrack", "metrics": metrics}
            else:
                metrics.backtracks += 1
                yield {"assignment": dict(assignment), "domains": domains_curr, "var": var, "color": color, "action": "fail_fc", "metrics": metrics}

    yield from backtrack_fc(domains)
