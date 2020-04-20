import numpy as np

import pickle

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

    def get_possible_moves(self, from_x, from_y):
        moves = []
        if self.current_player * self.board[from_y, from_x] <= 0:
            return([])
        if abs(self.board[from_y, from_x]) == 1:
            moves = self.get_possible_moves_for_ordinary(from_x, from_y)
        else:
            moves = self.get_possible_moves_for_queen(from_x, from_y)
        if len(moves) == 0:
            return([])
        #print("MOVES from x = {}, from y = {}".format(x, y))
        #print(moves)
        i = 0
        while True:
            correct_next_moves = []
            current_move = moves[i]

            if current_move.is_attack:
                if current_move.is_queen:
                    next_moves = self.get_possible_moves_for_queen(current_move.visited_cells[-1][0], current_move.visited_cells[-1][1])
                else:
                    next_moves = self.get_possible_moves_for_ordinary(current_move.visited_cells[-1][0], current_move.visited_cells[-1][1])
                correct_next_moves = []

                for j in np.arange(0, len(next_moves)):
                    if next_moves[j].is_attack and not next_moves[j].beaten_cells[-1] in current_move.beaten_cells:
                        next_moves[j].beaten_cells = current_move.beaten_cells + next_moves[j].beaten_cells
                        next_moves[j].visited_cells = current_move.visited_cells + next_moves[j].visited_cells
                        next_moves[j].is_queen = next_moves[j].is_queen or current_move.is_queen
                        correct_next_moves.append(next_moves[j])
                del(next_moves)

            if len(correct_next_moves) == 0:
                i += 1
                if i == len(moves):
                    break;
                continue

            #print("CORRECT NEXT MOVES : ", correct_next_moves)
            #print("MOVES_TO_APPEND : ", moves)
            #print("CURRENT MOVE : ", current_move)

            del(moves[i])
            moves.extend(correct_next_moves)

            if i == len(moves):
                break;
        return(moves)

    def get_all_possible_moves(self) -> List['BoardState']:
        """
        :return: list of BoardStates with  all possible moves
        """
        boards = []

        for y in np.arange(0, 8):
            for x in np.arange(0, 8):
                moves = self.get_possible_moves(x, y)
                for move in moves:
                    boards.append(self.do_correct_move(x, y, move))

        #print("RETURNN")
        return boards

    def do_correct_move(self, from_x, from_y, move: Move) -> Optional['BoardState']:
        """
        :return: new Boardstate
        """
        #print("DO CORRECT MOVE from x = {}, y = {}, ".format(from_x, from_y), move)
        result = self.copy()
        was_queen = move.is_queen

        for cell in move.beaten_cells:
            result.board[cell[1], cell[0]] = 0

        result.board[move.visited_cells[-1][1], move.visited_cells[-1][0]] = result.board[from_y, from_x]
        if was_queen and abs(result.board[from_y, from_x]) == 1:
            result.board[move.visited_cells[-1][1], move.visited_cells[-1][0]] *= 2

        result.board[from_y, from_x] = 0
        #result.current_player *= -1
        return result

    def do_move(self, from_x, from_y, to_x, to_y) -> Optional['BoardState']:
        """
        :return: new BoardState or None for invalid move
        """

        if self.current_player * self.board[from_y, from_x] <= 0:
            return None
        possible_moves = self.get_possible_moves(from_x, from_y)
        current_move = Move()

        for move in possible_moves:
            if Move(to_x, to_y, False) == move:
                current_move = move
                break
            if Move(to_x, to_y, True) == move:
                current_move = move
                break
        else:
            return None

        return self.do_correct_move(from_x, from_y, current_move)

    def get_possible_moves_for_ordinary(self, from_x, from_y) -> List['Move']: # moves with only one attack
        moves = []
        for y in [from_y - 1, from_y + 1]:
            for  x in [from_x - 1, from_x + 1]:
                if self.is_in_board(x, y): #check is in board
                    if self.board[y, x] == 0 and y == from_y - 1: #check is empty
                        moves.append(Move(x, y, False, is_queen = (y == 0)))
                    if self.board[y, x] * self.current_player < 0: # if the opponent is on the square
                        next_y, next_x = 2 * y - from_y, 2 * x - from_x # after attack coordinate
                        if self.is_in_board(next_x, next_y) and self.board[next_y, next_x] == 0:
                            moves.append(Move(next_x, next_y, True, x, y, is_queen = (next_y == 0)))
        return moves

    def get_possible_moves_for_queen(self, from_x, from_y) -> List['Move']:
        moves = []
        def moves_for_direction(x_direction: int, y_direction: int):
            was_attack = False
            beaten_cell_x = None
            beaten_cell_y = None
            to_x, to_y = from_x, from_y
            while True:
                to_x += x_direction
                to_y += y_direction
                if not self.is_in_board(to_x, to_y):
                    break
                if self.board[to_y, to_x] == 0:
                    moves.append(Move(to_x, to_y, was_attack, beaten_cell_x, beaten_cell_y, is_queen = True))
                if self.board[to_y, to_x] * self.current_player < 0:
                    if not was_attack:
                        was_attack = True
                        beaten_cell_x = to_x
                        beaten_cell_y = to_y
                    else:
                        break
                if self.board[to_y, to_x] * self.current_player > 0:
                    break

        moves_for_direction(1, 1)
        moves_for_direction(1, -1)
        moves_for_direction(-1, 1)
        moves_for_direction(-1, -1)
        return moves

    def __getstate__(self) -> dict:
        state = {}
        state["board"] = self.board
        state["current_player"] = self.current_player
        return state

    def __setstate__(self, state: dict):
        self.board = state["board"]
        self.current_player = state["current_player"]

    @property
    def is_game_finished(self) -> bool:
        ... # todo

    @property
    def get_winner(self) -> Optional[int]:
        if self.get_figures_count(self.current_player) == 0:
            return -1 * self.current_player
        if len(self.get_all_possible_moves()) == 0:
            return -1 * self.current_player
        return 0

    def get_figures_count(self, player: int):
        count = 0
        for i in self.board:
            for j in i:
                if player * j > 0:
                    count += 1
        return count

    def is_in_board(self, x, y) -> bool:
        size = self.board.shape[0] - 1
        return x >= 0 and y >= 0 and x <= size and y <= size

    @staticmethod
    def initial_state() -> Optional['BoardState']:
        board = np.zeros(shape=(8, 8), dtype=np.int8)
        x_places = np.arange(0, 8)

        for x in x_places:
            if x % 2 == 0:
                board[7, x] = 1
                board[5, x] = 1
                board[1, x] = -1
            else:
                board[0, x] = -1
                board[2, x] = -1
                board[6, x] = 1
        return BoardState(board, 1)
