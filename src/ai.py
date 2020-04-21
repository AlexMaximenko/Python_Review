from typing import Optional

from .boardstate import BoardState


class PositionEvaluation:
    def __call__(self, board: BoardState, player) -> float:
        #todo
        evaluation = board.player_checks + 2 * board.player_queens
        evaluation -= (board.opponent_checks + 2 * board.opponent_queens)
        return evaluation * player * board.current_player

class AI:
    def __init__(self, position_evaluation: PositionEvaluation, search_depth: int):
        self.position_evaluation: PositionEvaluation = position_evaluation
        self.depth: int = search_depth

    def get_min_max(
            self,
            board: BoardState,
            recursive_level: int = 0,
            alpha: int = 1000,
            beta: int = -1000) -> float:
        if recursive_level >= self.depth:
            return self.position_evaluation(board, self.player)

        curr_board = board.inverted()
        if recursive_level % 2 == 0:
            moves = curr_board.get_all_possible_moves()
            if len(moves) == 0:
                return 1000
            min = 1000
            for move in curr_board.get_all_possible_moves():
                #print("WHITE MOVE")
                #for i in move.board:
                #    print(i)
                curr_value = self.get_min_max(move, recursive_level + 1, alpha = min)
                #print("CURRENT VALUE = ", curr_value)
                if curr_value <= beta :
                    #print("BETA")
                    return -1000
                if curr_value < min:
                    min = curr_value
            #print("MIN = ", min)
            return min

        else:
            #print("AFTER WHITE MOVE")
            #for i in curr_board.board:
            #    print(i)
            moves = curr_board.get_all_possible_moves()
            if len(moves) == 0:
                return -1000
            max = -1000
            for move in curr_board.get_all_possible_moves():
                curr_value = self.get_min_max(move, recursive_level + 1, beta = max)
                if curr_value > alpha:
                    #print("ALPHA")
                    return 1000
                if curr_value > max:
                    max = curr_value
            return max

    def next_move(self, board: BoardState) -> Optional[BoardState]:
        moves = board.get_all_possible_moves()
        print("-------------------")
        if len(moves) == 0:
            return None
        print(moves)
        print("-------------------")

        self.player = board.current_player
        # todo better implementation
        max = -1000
        best = 0
        for i in range(len(moves)):
            curr_value = self.get_min_max(moves[i], 0, beta = max)
            #print("CURR_VALUE = ", curr_value)
            if curr_value > max:
                max = curr_value
                beta = max
                best = i
        return moves[best]
