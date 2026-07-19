"""Breadth-first search solver cho Bloxorz."""

from collections import deque

from core.board import Board
from core.enums import Move
from core.level import Level
from core.state import GameState
from core.transition import get_valid_moves, is_goal_state


def bfs_search(level: Level) -> dict | None:
    """
    Tìm đường đi ngắn nhất (theo số bước) bằng BFS.

    Args:
        level: Đối tượng Level chứa board và initial_state.

    Returns:
        Một dict chứa kết quả nếu tìm được lời giải:
            {
                "moves": list[Move]          – danh sách bước đi từ đầu đến đích,
                "path": list[GameState]       – danh sách state tương ứng (bao gồm cả initial),
                "nodes_expanded": int         – số node đã mở rộng (lấy ra khỏi queue),
                "nodes_generated": int        – số node đã sinh ra (thêm vào queue),
            }
        None nếu không tìm được lời giải.
    """

    board: Board = level.board
    initial_state: GameState = level.initial_state

    # ----- Kiểm tra trường hợp đặc biệt: state ban đầu đã là goal -----
    if is_goal_state(board, initial_state):
        return {
            "moves": [],
            "path": [initial_state],
            "nodes_expanded": 0,
            "nodes_generated": 1,
        }

    # ----- Khởi tạo BFS -----
    # Mỗi phần tử trong queue là (state hiện tại, danh sách moves, danh sách path)
    frontier: deque[tuple[GameState, list[Move], list[GameState]]] = deque()
    frontier.append((initial_state, [], [initial_state]))

    # Tập visited lưu các state đã thăm để tránh lặp vòng.
    # GameState là frozen dataclass nên hashable, dùng trực tiếp trong set.
    visited: set[GameState] = set()
    visited.add(initial_state)

    nodes_expanded: int = 0    # Đếm số node đã mở rộng
    nodes_generated: int = 1   # Đếm số node đã sinh (initial_state = 1)

    # ----- Vòng lặp BFS -----
    while frontier:
        current_state, moves_so_far, path_so_far = frontier.popleft()
        nodes_expanded += 1

        # Sinh tất cả successor hợp lệ từ state hiện tại
        for move, next_state in get_valid_moves(board, current_state):
            # Bỏ qua state đã thăm
            if next_state in visited:
                continue

            # Đánh dấu đã thăm ngay khi sinh ra (graph-search BFS chuẩn)
            visited.add(next_state)
            nodes_generated += 1

            new_moves = moves_so_far + [move]
            new_path = path_so_far + [next_state]

            # Kiểm tra goal
            if is_goal_state(board, next_state):
                return {
                    "moves": new_moves,
                    "path": new_path,
                    "nodes_expanded": nodes_expanded,
                    "nodes_generated": nodes_generated,
                }

            frontier.append((next_state, new_moves, new_path))

    # Duyệt hết mà không tìm được lời giải
    return None
