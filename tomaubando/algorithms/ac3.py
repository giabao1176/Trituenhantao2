import time
from .backtracking import ColoringMetrics

def revise(domains, xi, xj):
    revised = False
    for x in list(domains[xi]):
        if len(domains[xj]) == 1 and domains[xj][0] == x:
            domains[xi].remove(x)
            revised = True
    return revised

def run_ac3(districts, neighbors, domains):
    queue = []
    for x in districts:
        for y in neighbors.get(x, []):
            queue.append((x, y))

    while queue:
        xi, xj = queue.pop(0)
        if revise(domains, xi, xj):
            if not domains[xi]:
                return False
            for xk in neighbors.get(xi, []):
                if xk != xj:
                    queue.append((xk, xi))
    return True

def solve_ac3(districts, neighbors, colors):
    metrics = ColoringMetrics()
    metrics.start_time = time.time()
    domains = {var: list(colors) for var in districts}

    ac3_success = run_ac3(districts, neighbors, domains)
    if not ac3_success:
        metrics.end_time = time.time()
        return False, {}, metrics

    assignment = {}

    def select_unassigned_variable():
        for var in districts:
            if var not in assignment:
                return var
        return None

    def backtrack_ac3(domains_curr):
        var = select_unassigned_variable()
        if var is None:
            return True

        for color in domains_curr[var]:
            metrics.assignments += 1
            assignment[var] = color

            new_domains = {v: list(d) for v, d in domains_curr.items()}
            new_domains[var] = [color]

            consistent = True
            queue = []
            for nb in neighbors.get(var, []):
                if nb not in assignment:
                    queue.append((nb, var))

            while queue:
                xi, xj = queue.pop(0)
                if revise(new_domains, xi, xj):
                    if not new_domains[xi]:
                        consistent = False
                        break
                    for xk in neighbors.get(xi, []):
                        if xk != xj and xk not in assignment:
                            queue.append((xk, xi))

            if consistent:
                if backtrack_ac3(new_domains):
                    return True

            del assignment[var]
            metrics.backtracks += 1

        return False

    success = backtrack_ac3(domains)
    metrics.end_time = time.time()
    return success, assignment, metrics

def solve_ac3_stepwise(districts, neighbors, colors):
    metrics = ColoringMetrics()
    metrics.start_time = time.time()
    domains = {var: list(colors) for var in districts}
    assignment = {}

    queue = []
    for x in districts:
        for y in neighbors.get(x, []):
            queue.append((x, y))

    yield {"assignment": dict(assignment), "domains": {v: list(d) for v, d in domains.items()}, "action": "ac3_start", "metrics": metrics, "log": "Bắt đầu chạy AC-3 lọc miền giá trị..."}

    ac3_success = True
    while queue:
        xi, xj = queue.pop(0)
        if revise(domains, xi, xj):
            yield {"assignment": dict(assignment), "domains": {v: list(d) for v, d in domains.items()}, "action": "ac3_revise", "metrics": metrics, "log": f"AC-3 lọc: rút gọn miền giá trị của {xi} dựa trên {xj} -> {domains[xi]}"}
            if not domains[xi]:
                ac3_success = False
                break
            for xk in neighbors.get(xi, []):
                if xk != xj:
                    queue.append((xk, xi))

    if not ac3_success:
        yield {"assignment": dict(assignment), "domains": {v: list(d) for v, d in domains.items()}, "action": "fail", "metrics": metrics, "log": "AC-3 thất bại! Không thể thỏa mãn ràng buộc."}
        return

    yield {"assignment": dict(assignment), "domains": {v: list(d) for v, d in domains.items()}, "action": "ac3_done", "metrics": metrics, "log": "AC-3 hoàn tất lọc! Bắt đầu Backtracking trên miền giá trị đã thu nhỏ."}

    def select_unassigned_variable():
        for var in districts:
            if var not in assignment:
                return var
        return None

    def backtrack_ac3(domains_curr):
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
            queue_mac = []
            for nb in neighbors.get(var, []):
                if nb not in assignment:
                    queue_mac.append((nb, var))

            while queue_mac:
                xi, xj = queue_mac.pop(0)
                if revise(new_domains, xi, xj):
                    if not new_domains[xi]:
                        consistent = False
                        break
                    for xk in neighbors.get(xi, []):
                        if xk != xj and xk not in assignment:
                            queue_mac.append((xk, xi))

            if consistent:
                assignment[var] = color
                yield {"assignment": dict(assignment), "domains": new_domains, "var": var, "color": color, "action": "assign", "metrics": metrics}

                success = False
                for step in backtrack_ac3(new_domains):
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
                yield {"assignment": dict(assignment), "domains": domains_curr, "var": var, "color": color, "action": "fail_mac", "metrics": metrics}

    yield from backtrack_ac3(domains)
