import json
import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.level import Level
from core.level_loader import load_level
from ai.bfs import bfs_search
from ai.dfs import dfs_search
from ai.ucs import solve_ucs as ucs_search
from ai.astar import solve_astar as astar_search
from ai.profiler import run_with_profiling

# Adapters for ucs and astar since they take board, state
def ucs_adapter(level):
    res = ucs_search(level.board, level.initial_state)
    if res is None:
        return None
    return res

def astar_adapter(level):
    res = astar_search(level.board, level.initial_state)
    if res is None:
        return None
    return res

algorithms = {
    "BFS": bfs_search,
    "DFS": dfs_search,
    "UCS": ucs_adapter,
    "A*": astar_adapter
}

def main():
    levels_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "levels"))
    level_files = sorted([f for f in os.listdir(levels_dir) if f.endswith('.json')])
    
    print("| Level | Algorithm | Success | Time (s) | Memory (MB) | Nodes Expanded | Path Length | Cost |")
    print("|---|---|---|---|---|---|---|---|")
    
    for level_file in level_files:
        level_path = os.path.join(levels_dir, level_file)
        
        for alg_name, alg_fn in algorithms.items():
            try:
                # load fresh level instance
                level = load_level(level_path)
            
                res = run_with_profiling(alg_name, alg_fn, level)
                if res.success:
                    print(f"| {level_file} | {alg_name} | Yes | {res.search_time:.4f} | {res.memory_usage:.4f} | {res.nodes_expanded} | {res.solution_length} | {res.total_cost} |")
                else:
                    print(f"| {level_file} | {alg_name} | No | {res.search_time:.4f} | {res.memory_usage:.4f} | - | - | - |")
            except Exception as e:
                print(f"| {level_file} | {alg_name} | Error | - | - | - | - | - |")
                # print(e)

if __name__ == '__main__':
    main()
