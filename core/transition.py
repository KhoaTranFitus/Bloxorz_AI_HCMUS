"""Transition logic placeholder."""
from core.block import Block
from core.board import Board
from core.enums import Move, Orientation, TileType
from core.state import GameState


def calculate_moved_block(block: Block, move: Move) -> Block:
    """
    Tính vị trí và orientation mới sau khi block lăn.

    Hàm này chỉ tính hình học.
    Nó chưa kiểm tra block mới có nằm trên board hay không.
    """

    row = block.row
    col = block.col
    orientation = block.orientation

    # Block đang đứng.
    if orientation == Orientation.STANDING:
        if move == Move.UP:
            return Block(row - 2, col, Orientation.VERTICAL)

        if move == Move.DOWN:
            return Block(row + 1, col, Orientation.VERTICAL)

        if move == Move.LEFT:
            return Block(row, col - 2, Orientation.HORIZONTAL)

        if move == Move.RIGHT:
            return Block(row, col + 1, Orientation.HORIZONTAL)

    # Block đang nằm ngang theo chiều cột.
    elif orientation == Orientation.HORIZONTAL:
        if move == Move.UP:
            return Block(row - 1, col, Orientation.HORIZONTAL)

        if move == Move.DOWN:
            return Block(row + 1, col, Orientation.HORIZONTAL)

        if move == Move.LEFT:
            return Block(row, col - 1, Orientation.STANDING)

        if move == Move.RIGHT:
            return Block(row, col + 2, Orientation.STANDING)

    # Block đang nằm dọc theo chiều hàng.
    elif orientation == Orientation.VERTICAL:
        if move == Move.UP:
            return Block(row - 1, col, Orientation.STANDING)

        if move == Move.DOWN:
            return Block(row + 2, col, Orientation.STANDING)

        if move == Move.LEFT:
            return Block(row, col - 1, Orientation.VERTICAL)

        if move == Move.RIGHT:
            return Block(row, col + 1, Orientation.VERTICAL)

    raise ValueError(
        f"Unsupported transition: "
        f"orientation={orientation}, move={move}"
    )


def is_block_supported(
    board: Board,
    state: GameState,
    block: Block,
) -> bool:
    """
    Kiểm tra tất cả ô block chiếm đều có thể đỡ block.
    """

    for row, col in block.occupied_cells():
        if not board.is_walkable(
            row,
            col,
            state.bridge_states,
        ):
            return False

    return True


def apply_move(
    board: Board,
    state: GameState,
    move: Move,
) -> GameState | None:
    """
    Áp dụng một hành động lên state.

    Return:
        GameState mới nếu bước đi hợp lệ.
        None nếu block rơi khỏi board hoặc nằm trên void.

    Sau này BFS, DFS, UCS và A* sẽ gọi chính hàm này.
    """

    if state.is_split:
        raise NotImplementedError(
            "Split-block movement has not been implemented yet"
        )

    moved_block = calculate_moved_block(state.block, move)

    if not is_block_supported(board, state, moved_block):
        return None

    return GameState(
        block=moved_block,
        bridge_states=state.bridge_states,
        split_cubes=state.split_cubes,
        active_cube=state.active_cube,
    )


def is_goal_state(board: Board, state: GameState) -> bool:
    """
    Chỉ thắng khi block đang đứng trên ô goal.
    """

    if state.is_split:
        return False

    block = state.block

    if block.orientation != Orientation.STANDING:
        return False

    return board.get_tile(block.row, block.col) == TileType.GOAL


def get_valid_moves(
    board: Board,
    state: GameState,
) -> list[tuple[Move, GameState]]:
    """
    Sinh tất cả successor hợp lệ từ một state.

    Đây là hàm các thuật toán tìm kiếm sẽ sử dụng.
    """

    successors: list[tuple[Move, GameState]] = []

    for move in Move:
        next_state = apply_move(board, state, move)

        if next_state is not None:
            successors.append((move, next_state))

    return successors