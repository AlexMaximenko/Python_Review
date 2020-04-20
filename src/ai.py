from typing import Optional

from .boardstate import BoardState


class PositionEvaluation:
    def __call__(self, board: BoardState) -> float:
        #todo
        evaluation = self.get_opponent_figures_count(board)
        return -evaluation

    def get_opponent_figures_count(self, board: BoardState):
        count = 0
        player = board.current_player * -1
        for i in board.board:
            for j in i:
                if player * j > 0:
                    count += 1
        return count


class AI:
    def __init__(self, position_evaluation: PositionEvaluation, search_depth: int):
        self.position_evaluation: PositionEvaluation = position_evaluation
        self.depth: int = search_depth

    def next_move(self, board: BoardState) -> Optional[BoardState]:
        moves = board.get_all_possible_moves()
        if len(moves) == 0:
            return None
        print(moves)
        player = board.current_player
        # todo better implementation
        return max(moves, key=lambda b: self.position_evaluation(b))
