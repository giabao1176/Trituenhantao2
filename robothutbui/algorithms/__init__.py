from .bfs import solve_bfs, solve_bfs_stepwise
from .dfs import solve_dfs, solve_dfs_stepwise
from .ids import solve_ids, solve_ids_stepwise
from .ucs import solve_ucs, solve_ucs_stepwise
from .astar import solve_astar, solve_astar_stepwise
from .greedy import solve_greedy, solve_greedy_stepwise
from .idastar import solve_idastar, solve_idastar_stepwise
from .hill_climbing import solve_hill_climbing, solve_hill_climbing_stepwise
from .random_restart_hill import solve_random_restart_hill, solve_random_restart_hill_stepwise

def solve_vacuum(M, N, start_pos, initial_dirty, obstacles, algo, style):
    if algo == "BFS":
        return solve_bfs(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "DFS":
        return solve_dfs(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "IDS":
        return solve_ids(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "UCS":
        return solve_ucs(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "A*":
        return solve_astar(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "Greedy":
        return solve_greedy(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "IDA*":
        return solve_idastar(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "Hill Climbing":
        return solve_hill_climbing(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "Random Restart Hill":
        return solve_random_restart_hill(M, N, start_pos, initial_dirty, obstacles, style)
    else:
        raise ValueError(f"Unknown algorithm: {algo}")

def solve_vacuum_stepwise(M, N, start_pos, initial_dirty, obstacles, algo, style):
    if algo == "BFS":
        return solve_bfs_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "DFS":
        return solve_dfs_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "IDS":
        return solve_ids_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "UCS":
        return solve_ucs_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "A*":
        return solve_astar_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "Greedy":
        return solve_greedy_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "IDA*":
        return solve_idastar_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "Hill Climbing":
        return solve_hill_climbing_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    elif algo == "Random Restart Hill":
        return solve_random_restart_hill_stepwise(M, N, start_pos, initial_dirty, obstacles, style)
    else:
        raise ValueError(f"Unknown algorithm: {algo}")
