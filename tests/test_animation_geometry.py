"""Geometry checks for block and separated-cube animations."""

from ursina import Vec3

from core.block import Block
from core.board import Board
from core.enums import Move, Orientation, TileType
from core.state import GameState
from game.animation import BlockAnimator


def test_roll_directions_share_one_board_up_convention() -> None:
    expected = {
        Move.UP: Vec3(90, 0, 0),
        Move.DOWN: Vec3(-90, 0, 0),
        Move.LEFT: Vec3(0, 0, -90),
        Move.RIGHT: Vec3(0, 0, 90),
    }

    for move, rotation in expected.items():
        assert BlockAnimator._get_rotation_delta(move) == rotation


def test_roll_extent_matches_block_edge_in_move_direction() -> None:
    standing = GameState(Block(2, 2, Orientation.STANDING))
    horizontal = GameState(Block(2, 2, Orientation.HORIZONTAL))
    vertical = GameState(Block(2, 2, Orientation.VERTICAL))

    assert BlockAnimator._get_roll_extent(standing, Move.RIGHT) == 0.5
    assert BlockAnimator._get_roll_extent(horizontal, Move.RIGHT) == 1.0
    assert BlockAnimator._get_roll_extent(horizontal, Move.UP) == 0.5
    assert BlockAnimator._get_roll_extent(vertical, Move.UP) == 1.0
    assert BlockAnimator._get_roll_extent(vertical, Move.RIGHT) == 0.5


def test_partial_support_uses_the_last_tile_edge_as_fall_fulcrum() -> None:
    board = Board(
        width=3,
        height=1,
        tiles=((TileType.FLOOR, TileType.FLOOR, TileType.VOID),),
    )
    animator = BlockAnimator(
        root=None,
        tile_top_y=0.1,
        get_position=lambda state: Vec3(0, 0, 0),
        sync_with_state=lambda state, reset: None,
    )
    state = GameState(Block(0, 0, Orientation.STANDING))

    assert animator._get_fall_fulcrum(board, state, Move.RIGHT) == Vec3(
        1.5,
        0.1,
        0,
    )
