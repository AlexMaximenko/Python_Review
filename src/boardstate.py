import numpy as np
from typing import Optional, List

from .move import Move


class BoardState:
    def __init__(self, board: np.ndarray, current_player: int = 1):
        self.board: np.ndarray = board
        self.current_player: int = current_player

    def inverted(self) -> 'BoardState':
        return BoardState(board=self.board[::-1, ::-1], current_player=self.current_player * -1)

    def copy(self) -> 'BoardState':
        return BoardState(self.board.copy(), self.current_player)

    def do_move(self, from_x, from_y, to_x, to_y) -> Optional['BoardState']:
        """
        :return: new BoardState or None for invalid move
        """
        if self.current_player * self.board[from_y, from_x] <= 0:
            return None
        print("Possible moves: ", self.get_possible_moves_for_ordinary(from_x, from_y))
        possible_moves = []
        if abs(self.board[from_y, from_x]) == 1:
            possible_moves = self.get_possible_moves_for_ordinary(from_x, from_y)
        else:
            possible_moves = self.get_possible_moves_for_queen(from_x, from_y)

        current_move = Move()
        if Move(to_x, to_y, False) in possible_moves:
            current_move = Move(to_x, to_y, False)
        elif Move(to_x, to_y, True) in possible_moves:
                current_move = Move(to_x, to_y, True)
        else:
            return None

        # todo more validation her

        result = self.copy()
        result.board[to_y, to_x] = result.board[from_y, from_x]
        result.board[from_y, from_x] = 0

        return result

    def get_possible_moves_for_ordinary(self, from_x, from_y) -> List['Move']:
        moves = []
        size = self.board.shape[0] - 1
        for y in [from_y - 1, from_y + 1]:
            for  x in [from_x - 1, from_x + 1]:
                if self.is_in_board(x, y): #check is in board
                    if self.board[y, x] == 0: #check is empty
                        moves.append(Move(x, y, False))
                    if self.board[y, x] * self.current_player < 0: # if the opponent is on the square
                        next_y, next_x = 2 * y - from_y, 2 * x - from_x # after atack coordinate
                        if self.board[next_y, next_x] == 0 and self.is_in_board(next_x, next_y):
                            moves.append(Move(next_x, next_y, True))
        return moves

    def get_possible_moves_for_queen(self) -> List['BoardState']:
        return [] # todo

    @property
    def is_game_finished(self) -> bool:
        ... # todo

    @property
    def get_winner(self) -> Optional[int]:
        ... # todo

    def is_in_board(self, x, y) -> bool:
        size = self.board.shape[0] - 1
        return x >= 0 and y >= 0 and x <= size and y <= size

    @staticmethod
    def initial_state() -> 'BoardState':
        board = np.zeros(shape=(8, 8), dtype=np.int8)
        y_places = np.arange(0, 8)
        white_x_places = np.array([7, 6] * 4)

        for x, y in zip(white_x_places, y_places):
            board[x, y] = 1
            board[x - 6, y] = -1

        return BoardState(board, 1)
