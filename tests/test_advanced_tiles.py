"""Unit tests for soft and heavy switch behavior."""

from core.block import Block
from core.board import Board
from core.enums import Move, Orientation, TileType
from core.state import GameState
from core.transition import apply_move, get_activated_switches


def _single_row_board(*tiles: TileType) -> Board:
    return Board(
        width=len(tiles),
        height=1,
        tiles=(tuple(tiles),),
    )


def test_soft_switch_activates_under_part_of_lying_block() -> None:
    board = _single_row_board(TileType.FLOOR, TileType.SOFT_SWITCH)
    state = GameState(Block(0, 0, Orientation.HORIZONTAL))

    assert get_activated_switches(board, state) == ((0, 1),)


def test_heavy_switch_requires_standing_block() -> None:
    board = _single_row_board(TileType.HEAVY_SWITCH, TileType.FLOOR)
    lying = GameState(Block(0, 0, Orientation.HORIZONTAL))
    standing = GameState(Block(0, 0, Orientation.STANDING))

    assert get_activated_switches(board, lying) == ()
    assert get_activated_switches(board, standing) == ((0, 0),)


def test_split_cube_activates_soft_but_not_heavy_switch() -> None:
    soft_board = _single_row_board(
        TileType.FLOOR,
        TileType.SOFT_SWITCH,
    )
    heavy_board = _single_row_board(
        TileType.FLOOR,
        TileType.HEAVY_SWITCH,
    )
    state = GameState(
        block=Block(0, 0, Orientation.CUBE),
        split_cubes=((0, 0), (0, 1)),
        active_cube=0,
    )

    assert get_activated_switches(soft_board, state) == ((0, 1),)
    assert get_activated_switches(heavy_board, state) == ()


def test_entering_soft_switch_opens_linked_bridge() -> None:
    board = Board(
        width=3,
        height=1,
        tiles=((
            TileType.FLOOR,
            TileType.FLOOR,
            TileType.SOFT_SWITCH,
        ),),
        switch_links=((0, 2, (0,), "open"),),
    )
    state = GameState(
        Block(0, 0, Orientation.STANDING),
        bridge_states=(False,),
    )

    next_state = apply_move(board, state, Move.RIGHT)

    assert next_state is not None
    assert next_state.bridge_states == (True,)


def test_lying_on_heavy_switch_does_not_open_bridge() -> None:
    board = Board(
        width=3,
        height=1,
        tiles=((
            TileType.FLOOR,
            TileType.FLOOR,
            TileType.HEAVY_SWITCH,
        ),),
        switch_links=((0, 2, (0,), "open"),),
    )
    state = GameState(
        Block(0, 0, Orientation.STANDING),
        bridge_states=(False,),
    )

    next_state = apply_move(board, state, Move.RIGHT)

    assert next_state is not None
    assert next_state.bridge_states == (False,)


def test_standing_on_heavy_switch_opens_bridge() -> None:
    board = Board(
        width=4,
        height=1,
        tiles=((
            TileType.FLOOR,
            TileType.FLOOR,
            TileType.FLOOR,
            TileType.HEAVY_SWITCH,
        ),),
        switch_links=((0, 3, (0,), "open"),),
    )
    state = GameState(
        Block(0, 0, Orientation.STANDING),
        bridge_states=(False,),
    )

    lying_state = apply_move(board, state, Move.RIGHT)
    assert lying_state is not None
    standing_state = apply_move(board, lying_state, Move.RIGHT)

    assert standing_state is not None
    assert standing_state.block.orientation == Orientation.STANDING
    assert standing_state.bridge_states == (True,)


def test_split_cube_can_open_bridge_with_soft_switch() -> None:
    board = Board(
        width=2,
        height=2,
        tiles=(
            (TileType.FLOOR, TileType.FLOOR),
            (TileType.SOFT_SWITCH, TileType.FLOOR),
        ),
        switch_links=((1, 0, (0,), "open"),),
    )
    state = GameState(
        block=Block(0, 0, Orientation.CUBE),
        bridge_states=(False,),
        split_cubes=((0, 0), (0, 1)),
        active_cube=0,
    )

    next_state = apply_move(board, state, Move.DOWN)

    assert next_state is not None
    assert next_state.bridge_states == (True,)
