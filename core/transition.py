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

        if (
            block.orientation == Orientation.STANDING
            and board.get_tile(row, col) == TileType.FRAGILE
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

    provisional_state = GameState(
        block=moved_block,
        bridge_states=state.bridge_states,
        split_cubes=state.split_cubes,
        active_cube=state.active_cube,
    )
    previously_pressed = set(get_activated_switches(board, state))
    currently_pressed = set(get_activated_switches(board, provisional_state))
    bridge_states = list(state.bridge_states)

    for row, col in currently_pressed - previously_pressed:
        link = board.get_switch_link(row, col)
        if link is None:
            continue
        bridge_ids, action = link
        for bridge_id in bridge_ids:
            if action == "open":
                bridge_states[bridge_id] = True
            elif action == "close":
                bridge_states[bridge_id] = False
            else:
                bridge_states[bridge_id] = not bridge_states[bridge_id]

    next_state = GameState(
        block=moved_block,
        bridge_states=tuple(bridge_states),
        split_cubes=state.split_cubes,
        active_cube=state.active_cube,
    )

    if not is_block_supported(board, next_state, moved_block):
        return None

    return next_state


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


def get_activated_switches(
    board: Board,
    state: GameState,
) -> tuple[tuple[int, int], ...]:
    """Return switches pressed by the block in this state.

    A soft switch reacts to either half of a lying block. A heavy switch
    requires the complete block weight, so it reacts only while standing.
    """

    activated: list[tuple[int, int]] = []
    block = state.block

    for row, col in block.occupied_cells():
        tile = board.get_tile(row, col)

        if tile == TileType.SOFT_SWITCH:
            activated.append((row, col))
        elif (
            tile == TileType.HEAVY_SWITCH
            and block.orientation == Orientation.STANDING
        ):
            activated.append((row, col))

    return tuple(activated)


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
