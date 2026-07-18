"""Result returned by a search algorithm."""

from dataclasses import dataclass

from core.enums import Move


@dataclass(frozen=True)
class SearchResult:
    moves: tuple[Move, ...]
    cost: int
    expanded_nodes: int
    solved: bool = True

    @classmethod
    def no_solution(cls, expanded_nodes: int) -> "SearchResult":
        return cls((), 0, expanded_nodes, False)
