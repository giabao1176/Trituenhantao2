import time
import random
from .backtracking import ColoringMetrics

def count_conflicts(var, color, assignment, neighbors):
    conflicts = 0
    for nb in neighbors.get(var, []):
        if nb in assignment and assignment[nb] == color:
            conflicts += 1
    return conflicts

def get_conflicted_variables(districts, neighbors, assignment):
    conflicted = []
    for var in districts:
        color = assignment.get(var)
        if count_conflicts(var, color, assignment, neighbors) > 0:
            conflicted.append(var)
    return conflicted

def solve_min_conflicts(districts, neighbors, colors, max_steps=1000):
    metrics = ColoringMetrics()
    metrics.start_time = time.time()

    assignment = {}
    for var in districts:
        assignment[var] = random.choice(colors)
        metrics.assignments += 1

    for step in range(max_steps):
        conflicted = get_conflicted_variables(districts, neighbors, assignment)
        if not conflicted:
            metrics.end_time = time.time()
            return True, assignment, metrics

        var = random.choice(conflicted)

        min_conf = len(neighbors.get(var, [])) + 1
        best_colors = []
        for c in colors:
            conf = count_conflicts(var, c, assignment, neighbors)
            if conf < min_conf:
                min_conf = conf
                best_colors = [c]
            elif conf == min_conf:
                best_colors.append(c)

        chosen_color = random.choice(best_colors)
        if assignment[var] != chosen_color:
            assignment[var] = chosen_color
            metrics.assignments += 1

    metrics.end_time = time.time()
    return False, assignment, metrics

def solve_min_conflicts_stepwise(districts, neighbors, colors, max_steps=200):
    metrics = ColoringMetrics()
    metrics.start_time = time.time()

    assignment = {}
    for var in districts:
        assignment[var] = random.choice(colors)
        metrics.assignments += 1

    yield {
        "assignment": dict(assignment),
        "var": None,
        "color": None,
        "action": "init",
        "metrics": metrics,
        "log": "Khởi tạo gán màu ngẫu nhiên cho toàn bộ bản đồ."
    }

    for step in range(max_steps):
        conflicted = get_conflicted_variables(districts, neighbors, assignment)
        if not conflicted:
            yield {
                "assignment": dict(assignment),
                "var": None,
                "color": None,
                "action": "success",
                "metrics": metrics,
                "log": f"Giải thành công ở bước {step}! Không còn xung đột."
            }
            return

        var = random.choice(conflicted)

        min_conf = len(neighbors.get(var, [])) + 1
        best_colors = []
        conflicts_info = {}
        for c in colors:
            conf = count_conflicts(var, c, assignment, neighbors)
            conflicts_info[c] = conf
            if conf < min_conf:
                min_conf = conf
                best_colors = [c]
            elif conf == min_conf:
                best_colors.append(c)

        chosen_color = random.choice(best_colors)
        old_color = assignment[var]

        log_str = f"Bước {step+1}: Chọn biến xung đột '{var}' (Màu cũ: {old_color}).\n"
        log_str += "  Số xung đột ứng với mỗi màu: " + ", ".join(f"{c}: {conflicts_info[c]}" for c in colors) + ".\n"

        if old_color == chosen_color:
            log_str += f"  -> Chọn giữ nguyên màu {chosen_color} để tối thiểu xung đột ({min_conf} xung đột)."
            yield {
                "assignment": dict(assignment),
                "var": var,
                "color": chosen_color,
                "action": "keep",
                "metrics": metrics,
                "log": log_str
            }
        else:
            assignment[var] = chosen_color
            metrics.assignments += 1
            log_str += f"  -> Gán màu mới {chosen_color} để tối thiểu xung đột ({min_conf} xung đột)."
            yield {
                "assignment": dict(assignment),
                "var": var,
                "color": chosen_color,
                "action": "assign",
                "metrics": metrics,
                "log": log_str
            }

    yield {
        "assignment": dict(assignment),
        "var": None,
        "color": None,
        "action": "fail",
        "metrics": metrics,
        "log": f"Không thể giải thành công sau {max_steps} bước."
    }
