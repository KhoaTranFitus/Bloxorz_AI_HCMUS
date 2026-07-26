import json
import os
import sys
import multiprocessing
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.level_loader import load_level
from ai.bfs import bfs_search
from ai.dfs import dfs_search
from ai.ucs import solve_ucs as ucs_search
from ai.astar import solve_astar as astar_search
from ai.profiler import run_with_profiling

def ucs_adapter(level):
    return ucs_search(level.board, level.initial_state)

def astar_adapter(level):
    return astar_search(level.board, level.initial_state)

algorithms = {
    "BFS": bfs_search,
    "DFS": dfs_search,
    "UCS": ucs_adapter,
    "A*": astar_adapter
}

def worker_func(alg_name, level_path, return_dict):
    try:
        level = load_level(level_path)
        alg_fn = algorithms[alg_name]
        res = run_with_profiling(alg_name, alg_fn, level)
        if res.success:
            return_dict['res'] = f"Yes | Time: {res.search_time:.4f}s | Mem: {res.memory_usage:.4f}MB | Nodes: {res.nodes_expanded} | Moves: {res.solution_length} | Cost: {res.total_cost}"
        else:
            return_dict['res'] = f"No | Time: {res.search_time:.4f}s | Mem: {res.memory_usage:.4f}MB"
    except Exception as e:
        return_dict['res'] = f"Error: {e}"

def main():
    levels_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "levels"))
    test_levels = ["level_04.json", "level_08.json", "level_09.json", "level_10.json", "level_11.json"]
    
    with open("scratch/results.txt", "w") as f:
        for level_file in test_levels:
            level_path = os.path.join(levels_dir, level_file)
            f.write(f"\n--- {level_file} ---\n")
            print(f"Testing {level_file}...")
            
            for alg_name in algorithms.keys():
                manager = multiprocessing.Manager()
                return_dict = manager.dict()
                p = multiprocessing.Process(target=worker_func, args=(alg_name, level_path, return_dict))
                p.start()
                
                # Wait up to 10 seconds for DFS or others on level 10
                timeout = 10 if (alg_name == "DFS" and level_file == "level_10.json") else 30
                p.join(timeout)
                
                if p.is_alive():
                    p.terminate()
                    p.join()
                    res_str = f"Timeout after {timeout}s"
                else:
                    res_str = return_dict.get('res', 'Unknown Error')
                
                out = f"{alg_name}: {res_str}"
                print(out)
                f.write(out + "\n")
                f.flush()

if __name__ == '__main__':
    main()
