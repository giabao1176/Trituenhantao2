import random

def heuristic(pos, dirty):
    if not dirty:
        return 0
    min_dist = min(abs(pos[0] - d[0]) + abs(pos[1] - d[1]) for d in dirty)
    return min_dist + len(dirty) - 1

def solve_local_beam(M, N, start_pos, initial_dirty, obstacles, style):
    k = style
    initial_dirty = frozenset(initial_dirty)

    if start_pos in initial_dirty:
        initial_dirty = initial_dirty - {start_pos}

    if not initial_dirty:
        return {"found": True, "path": [start_pos], "directions": [], "exploration_log": ["Đích trùng bắt đầu!"], "nodes_gen": 1, "nodes_exp": 0}

    beams = [{
        "pos": start_pos,
        "dirty": initial_dirty,
        "path": [start_pos],
        "directions": [],
        "visited": { (start_pos, initial_dirty) }
    }]

    nodes_generated = 1
    nodes_expanded = 0
    logs = [f"--- BẮT ĐẦU Local Beam Search (k = {k}) ---"]

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    max_steps = 1000
    step = 0

    while step < max_steps:
        step += 1

        for beam in beams:
            if not beam["dirty"]:
                logs.append(f"Bước {step}: Phát hiện chùm tia đạt đích!")
                return {
                    "found": True,
                    "path": beam["path"],
                    "directions": beam["directions"],
                    "exploration_log": logs,
                    "nodes_gen": nodes_generated,
                    "nodes_exp": nodes_expanded
                }

        candidates = []
        for i, beam in enumerate(beams):
            r, c = beam["pos"]
            dirty = beam["dirty"]
            nodes_expanded += 1

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                    next_dirty = dirty - {(nr, nc)}
                    state_key = ((nr, nc), next_dirty)

                    if state_key not in beam["visited"]:
                        new_visited = set(beam["visited"])
                        new_visited.add(state_key)

                        candidate = {
                            "pos": (nr, nc),
                            "dirty": next_dirty,
                            "path": beam["path"] + [(nr, nc)],
                            "directions": beam["directions"] + [dir_names[(dr, dc)]],
                            "visited": new_visited,
                            "h": heuristic((nr, nc), next_dirty)
                        }
                        candidates.append(candidate)
                        nodes_generated += 1

                        if not next_dirty:
                            logs.append(f"Bước {step}: Sinh con đạt đích từ chùm {i+1} tại ({nr},{nc})!")
                            return {
                                "found": True,
                                "path": candidate["path"],
                                "directions": candidate["directions"],
                                "exploration_log": logs,
                                "nodes_gen": nodes_generated,
                                "nodes_exp": nodes_expanded
                            }

        if not candidates:
            logs.append(f"Bước {step}: Tất cả chùm tia đều bị kẹt (không sinh thêm trạng thái mới).")
            break

        seen = set()
        unique_candidates = []
        for cand in candidates:
            dup_key = (cand["pos"], cand["dirty"])
            if dup_key not in seen:
                seen.add(dup_key)
                unique_candidates.append(cand)

        if not unique_candidates:
            logs.append(f"Bước {step}: Không có ứng viên hợp lệ nào sau khi loại trùng lặp.")
            break

        unique_candidates.sort(key=lambda x: x["h"])

        beams = unique_candidates[:k]

        best_beam = beams[0]
        beam_locations = ", ".join(f"({b['pos'][0]},{b['pos'][1]})[h={b['h']}]" for b in beams)
        logs.append(f"Bước {step}: Cập nhật {len(beams)} chùm: [{beam_locations}]. Chùm tốt nhất còn {len(best_beam['dirty'])} bụi.")

    logs.append(f"Kết thúc tìm kiếm sau {step} bước mà không tìm thấy đích.")
    if beams:
        best_beam = beams[0]
        return {
            "found": False,
            "path": best_beam["path"],
            "directions": best_beam["directions"],
            "exploration_log": logs,
            "nodes_gen": nodes_generated,
            "nodes_exp": nodes_expanded
        }
    else:
        return {
            "found": False,
            "path": [start_pos],
            "directions": [],
            "exploration_log": logs,
            "nodes_gen": nodes_generated,
            "nodes_exp": nodes_expanded
        }

def solve_local_beam_stepwise(M, N, start_pos, initial_dirty, obstacles, style):
    k = style
    initial_dirty = frozenset(initial_dirty)

    if start_pos in initial_dirty:
        initial_dirty = initial_dirty - {start_pos}

    if not initial_dirty:
        yield {"pos": start_pos, "dirty": frozenset(), "log": "Trạng thái bắt đầu đã trùng đích!", "is_goal": True, "nodes_gen": 1, "nodes_exp": 0, "path": [start_pos], "directions": []}
        return

    beams = [{
        "pos": start_pos,
        "dirty": initial_dirty,
        "path": [start_pos],
        "directions": [],
        "visited": { (start_pos, initial_dirty) }
    }]

    nodes_generated = 1
    nodes_expanded = 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dir_names = {(-1, 0): "U", (1, 0): "D", (0, -1): "L", (0, 1): "R"}

    yield {"pos": start_pos, "dirty": initial_dirty, "log": f"--- BẮT ĐẦU Local Beam Search (k = {k}) ---", "is_goal": False, "nodes_gen": nodes_generated, "nodes_exp": nodes_expanded, "path": None, "directions": []}

    max_steps = 1000
    step = 0

    while step < max_steps:
        step += 1

        for beam in beams:
            if not beam["dirty"]:
                yield {
                    "pos": beam["pos"],
                    "dirty": beam["dirty"],
                    "log": f"Bước {step}: Phát hiện chùm tia đạt đích! -> ĐẠT ĐÍCH!",
                    "is_goal": True,
                    "nodes_gen": nodes_generated,
                    "nodes_exp": nodes_expanded,
                    "path": beam["path"],
                    "directions": beam["directions"]
                }
                return

        candidates = []
        for i, beam in enumerate(beams):
            r, c = beam["pos"]
            dirty = beam["dirty"]
            nodes_expanded += 1

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < M and 0 <= nc < N and (nr, nc) not in obstacles:
                    next_dirty = dirty - {(nr, nc)}
                    state_key = ((nr, nc), next_dirty)

                    if state_key not in beam["visited"]:
                        new_visited = set(beam["visited"])
                        new_visited.add(state_key)

                        candidate = {
                            "pos": (nr, nc),
                            "dirty": next_dirty,
                            "path": beam["path"] + [(nr, nc)],
                            "directions": beam["directions"] + [dir_names[(dr, dc)]],
                            "visited": new_visited,
                            "h": heuristic((nr, nc), next_dirty)
                        }
                        candidates.append(candidate)
                        nodes_generated += 1

                        if not next_dirty:
                            yield {
                                "pos": candidate["pos"],
                                "dirty": candidate["dirty"],
                                "log": f"Bước {step}: Sinh con đạt đích từ chùm {i+1} tại ({nr},{nc})! -> ĐẠT ĐÍCH!",
                                "is_goal": True,
                                "nodes_gen": nodes_generated,
                                "nodes_exp": nodes_expanded,
                                "path": candidate["path"],
                                "directions": candidate["directions"]
                            }
                            return

        if not candidates:
            yield {
                "pos": beams[0]["pos"] if beams else start_pos,
                "dirty": beams[0]["dirty"] if beams else initial_dirty,
                "log": f"Bước {step}: Tất cả chùm tia đều bị kẹt.",
                "is_goal": False,
                "nodes_gen": nodes_generated,
                "nodes_exp": nodes_expanded,
                "path": None,
                "directions": []
            }
            return

        seen = set()
        unique_candidates = []
        for cand in candidates:
            dup_key = (cand["pos"], cand["dirty"])
            if dup_key not in seen:
                seen.add(dup_key)
                unique_candidates.append(cand)

        if not unique_candidates:
            yield {
                "pos": beams[0]["pos"] if beams else start_pos,
                "dirty": beams[0]["dirty"] if beams else initial_dirty,
                "log": f"Bước {step}: Không có ứng viên hợp lệ nào sau khi loại trùng lặp.",
                "is_goal": False,
                "nodes_gen": nodes_generated,
                "nodes_exp": nodes_expanded,
                "path": None,
                "directions": []
            }
            return

        unique_candidates.sort(key=lambda x: x["h"])
        beams = unique_candidates[:k]

        best_beam = beams[0]
        beam_locations = ", ".join(f"({b['pos'][0]},{b['pos'][1]})[h={b['h']}]" for b in beams)
        log_text = f"Bước {step}: Cập nhật {len(beams)} chùm: [{beam_locations}]. Chùm tốt nhất còn {len(best_beam['dirty'])} bụi."

        yield {
            "pos": best_beam["pos"],
            "dirty": best_beam["dirty"],
            "log": log_text,
            "is_goal": False,
            "nodes_gen": nodes_generated,
            "nodes_exp": nodes_expanded,
            "path": None,
            "directions": []
        }
