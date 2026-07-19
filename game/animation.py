"""Animation logic for the Bloxorz block."""

from collections.abc import Callable

from ursina import Entity, Vec3, curve, destroy, invoke, scene

from core.enums import Move, Orientation
from core.state import GameState


class BlockAnimator:
    """Animate a rendered block without owning its visual appearance."""

    def __init__(
        self,
        root: Entity,
        tile_top_y: float,
        get_position: Callable[[GameState], Vec3],
        sync_with_state: Callable[[GameState, bool], None],
    ) -> None:
        self.root = root
        self.tile_top_y = tile_top_y
        self.get_position = get_position
        self.sync_with_state = sync_with_state
        self._roll_pivot: Entity | None = None
        self._animation_generation = 0

    @staticmethod
    def _get_rotation_delta(move: Move) -> Vec3:
        if move == Move.UP:
            return Vec3(90, 0, 0)
        if move == Move.DOWN:
            return Vec3(-90, 0, 0)
        if move == Move.LEFT:
            return Vec3(0, 0, -90)
        if move == Move.RIGHT:
            return Vec3(0, 0, 90)
        raise ValueError(f"Unsupported move: {move}")

    @staticmethod
    def _get_move_direction(move: Move) -> Vec3:
        if move == Move.UP:
            return Vec3(0, 0, 1)
        if move == Move.DOWN:
            return Vec3(0, 0, -1)
        if move == Move.LEFT:
            return Vec3(-1, 0, 0)
        if move == Move.RIGHT:
            return Vec3(1, 0, 0)
        raise ValueError(f"Unsupported move: {move}")

    @staticmethod
    def _get_roll_extent(state: GameState, move: Move) -> float:
        """Return the distance from the block center to its rolling edge."""
        orientation = state.block.orientation
        moves_along_x = move in (Move.LEFT, Move.RIGHT)

        if orientation == Orientation.STANDING:
            return 0.5
        if orientation == Orientation.HORIZONTAL and moves_along_x:
            return 1.0
        if orientation == Orientation.VERTICAL and not moves_along_x:
            return 1.0
        return 0.5

    def clear_roll_pivot(self) -> None:
        if self._roll_pivot is None:
            return

        self.root.world_parent = scene
        destroy(self._roll_pivot)
        self._roll_pivot = None

    def _begin_edge_roll(
        self,
        state: GameState,
        move: Move,
        duration: float,
    ) -> None:
        """
        Lăn block lớn quanh cạnh đang tiếp xúc với mặt sàn.
        """

        self.clear_roll_pivot()

        direction = self._get_move_direction(move)

        pivot_position = (
            self.get_position(state)
            + direction * self._get_roll_extent(state, move)
        )

        pivot_position.y = self.tile_top_y

        self._roll_pivot = Entity(
            parent=scene,
            position=pivot_position,
        )

        self.root.world_parent = self._roll_pivot

        self._roll_pivot.animate_rotation(
            self._get_rotation_delta(move),
            duration=duration,
            curve=curve.in_out_sine,
        )

    def animate_to_state(
        self,
        current_state: GameState,
        next_state: GameState,
        move: Move,
        duration: float = 0.2,
    ) -> None:
        """Roll the block to a valid next state."""
        self._animation_generation += 1
        generation = self._animation_generation
        self._begin_edge_roll(current_state, move, duration)
        invoke(
            self._sync_if_current,
            generation,
            next_state,
            delay=duration,
        )

    def animate_split_to_state(
        self,
        current_state: GameState,
        next_state: GameState,
        move: Move,
        duration: float = 0.2,
    ) -> None:
        """
        Animation cho cube nhỏ khi block đang bị tách đôi.
        """

        self._animation_generation += 1
        generation = self._animation_generation

        self.clear_roll_pivot()

        # SPACE chỉ đổi cube đang điều khiển.
        if move == Move.SWITCH:
            self.sync_with_state(next_state, True)
            return

        if not current_state.is_split:
            raise ValueError(
                "animate_split_to_state requires a split state"
            )

        active_idx = (
            current_state.active_cube
            if current_state.active_cube is not None
            else 0
        )

        current_row, current_col = (
            current_state.split_cubes[active_idx]
        )

        current_position = Vec3(
            current_col,
            self.tile_top_y + 0.38,
            -current_row,
        )

        # Đảm bảo root nằm đúng tại cube đang điều khiển.
        self.root.position = current_position

        # Không để rotation của lần trước ảnh hưởng hướng lăn hiện tại.
        self.root.rotation = Vec3(0, 0, 0)

        direction = self._get_move_direction(move)

        # Cube 1x1x1 có cạnh cách tâm 0.5 đơn vị.
        pivot_position = (
            current_position
            + direction * 0.5
        )

        pivot_position.y = self.tile_top_y

        self._roll_pivot = Entity(
            parent=scene,
            position=pivot_position,
        )

        self.root.world_parent = self._roll_pivot

        self._roll_pivot.animate_rotation(
            self._get_rotation_delta(move),
            duration=duration,
            curve=curve.in_out_sine,
        )

        invoke(
            self._sync_if_current,
            generation,
            next_state,
            delay=duration,
        )

    def _sync_if_current(self, generation: int, state: GameState) -> None:
        if generation == self._animation_generation:
            self.sync_with_state(state, True)

    def animate_fall(
        self,
        move: Move,
        current_state: GameState,
        roll_duration: float = 0.25,
        fall_duration: float = 0.65,
    ) -> None:
        """Roll the block over an unsupported edge, then drop it."""
        self._animation_generation += 1
        generation = self._animation_generation
        self._begin_edge_roll(current_state, move, roll_duration)
        invoke(
            self._drop_down_if_current,
            generation,
            fall_duration,
            delay=roll_duration,
        )

    def _drop_down_if_current(self, generation: int, duration: float) -> None:
        if generation == self._animation_generation:
            self._drop_down(duration)

    def _drop_down(self, duration: float) -> None:
        self.clear_roll_pivot()
        target_position = self.root.position + Vec3(0, -7, 0)

        self.root.animate_position(
            target_position,
            duration=duration,
            curve=curve.in_quad,
        )
        self.root.animate_rotation(
            self.root.rotation + Vec3(80, 20, 45),
            duration=duration,
            curve=curve.in_quad,
        )

    def destroy(self) -> None:
        self.cancel()

    def cancel(self) -> None:
        """Invalidate delayed callbacks and restore direct ownership of root."""
        self._animation_generation += 1
        self.clear_roll_pivot()
