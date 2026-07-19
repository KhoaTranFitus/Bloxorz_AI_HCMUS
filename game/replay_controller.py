"""Bộ điều khiển replay: tự động lăn block theo chuỗi moves."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ursina import invoke

from core.enums import Move

if TYPE_CHECKING:
    from game.game import GameController


class ReplayController:
    """
    Phát lại chuỗi bước đi tìm được bởi solver.

    Sử dụng ``ursina.invoke(delay=...)`` để gọi tuần tự
    ``game.try_move()`` mỗi ``step_delay`` giây.
    """

    def __init__(
        self,
        game: GameController,
        moves: list[Move],
        step_delay: float = 0.4,
    ) -> None:
        self.game = game
        self.moves = list(moves)  # copy để tránh side-effect
        self.step_delay = step_delay

        self._current_step: int = 0
        self.is_playing: bool = False

    def start(self) -> None:
        """Bắt đầu replay từ bước đầu tiên."""

        if not self.moves:
            return

        self.is_playing = True
        self._current_step = 0
        self.game.is_busy = True

        # Bắt đầu chuỗi replay
        self._play_next_step()

    def _play_next_step(self) -> None:
        """Thực hiện bước tiếp theo trong chuỗi replay."""

        if self._current_step >= len(self.moves):
            # Replay xong
            self.is_playing = False
            self.game.is_busy = False
            return

        move = self.moves[self._current_step]
        self.game._execute_move(move, allow_when_busy=True)
        self._current_step += 1

        # Lên lịch bước tiếp theo
        invoke(self._play_next_step, delay=self.step_delay)

    def stop(self) -> None:
        """Invalidate the replay; already scheduled callbacks become no-ops."""
        self.is_playing = False
        self._current_step = len(self.moves)
        self.game.is_busy = False
