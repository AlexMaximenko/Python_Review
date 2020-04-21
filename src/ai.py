from typing import Optional

from .boardstate import BoardState


class PositionEvaluation:
    def __call__(self, board: BoardState) -> float:
        #todo
        evaluation = board.player_checks + 2 * board.player_queens
        evaluation -= (board.opponent_checks + 2 * board.opponent_queens)
        return -evaluation

class AI:
    def __init__(self, position_evaluation: PositionEvaluation, search_depth: int):
        self.position_evaluation: PositionEvaluation = position_evaluation
        self.depth: int = search_depth

    def get_min_max(
            self,
            board: BoardState,
            recursive_level: int = 0,
            current_alpha: float,
            current_beta: float):
        print("Recursive level = ", recursive_level)

        if recursive_level >= self.depth * 2:
            return self.position_evaluation(board)

        curr_board = board.inverted()
        if recursive_level % 2 == 0:
            return max([self.get_min_max(
                b,
                recursive_level + 1)] for b in curr_board.get_all_possible_moves())
        else:
            return min([self.get_min_max(
                b,
                recursive_level + 1)] for b in curr_board.get_all_possible_moves())

    def next_move(self, board: BoardState) -> Optional[BoardState]:
        moves = board.get_all_possible_moves()
        print("-------------------")
        if len(moves) == 0:
            return None
        print(moves)
        print("-------------------")

        player = board.current_player
        # todo better implementation
        return min(moves, key=lambda b: self.get_min_max(b))
