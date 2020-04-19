from typing import Optional

from .boardstate import BoardState


class PositionEvaluation:
    def __call__(self, board: BoardState) -> float:
        #todo
        return 0


class AI:
    def __init__(self, position_evaluation: PositionEvaluation, search_depth: int):
        self.position_evaluation: PositionEvaluation = position_evaluation
        self.depth: int = search_depth

    def next_move(self, board: BoardState) -> Optional[BoardState]:
        moves = board.get_possible_moves()
        if len(moves) == 0:
            return None

        # todo better implementation
        return max(moves, key=lambda b: self.position_evaluation(b) * b.current_player)
