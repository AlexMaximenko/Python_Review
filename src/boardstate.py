import numpy as np

import pickle

from typing import Optional, List

from .move import Move


class BoardState:
    def __init__(
            self,
            board: np.ndarray,
            current_player: int = 1,
            player_checks: int = 12,
            opponent_checks: int = 12,
            player_queens: int = 0,
            opponent_queens: int = 0):
        self.board: np.ndarray = board
        self.current_player: int = current_player
        self.player_checks = player_checks
        self.opponent_checks = opponent_checks
        self.player_queens = player_queens
        self.opponent_queens = opponent_queens

    def inverted(self) -> 'BoardState':
        return BoardState(self.board[::-1, ::-1],
                          self.current_player * -1,
                          self.opponent_checks,
                          self.player_checks,
                          self.opponent_queens,
                          self.player_queens)

    def copy(self) -> 'BoardState':
        return BoardState(self.board.copy(),
                          self.current_player,
                          self.player_checks,
                          self.opponent_checks,
                          self.player_queens,
                          self.opponent_queens)

    def get_possible_moves(self, from_x, from_y, is_attack: bool = False):
        moves = []
        if self.current_player * self.board[from_y, from_x] <= 0:
            return([])
        if abs(self.board[from_y, from_x]) == 1:
            moves = self.get_possible_moves_for_ordinary(from_x, from_y, is_attack)
        else:
            moves = self.get_possible_moves_for_queen(from_x, from_y, is_attack)
        if len(moves) == 0:
            return([])

        i = 0
        while True:
            correct_next_moves = []
            current_move = moves[i]

            if current_move.is_attack:
                if current_move.is_queen:
                    next_moves = self.get_possible_moves_for_queen(
                        current_move.visited_cells[-1][0],
                        current_move.visited_cells[-1][1], True)
                else:
                    next_moves = self.get_possible_moves_for_ordinary(
                        current_move.visited_cells[-1][0],
                        current_move.visited_cells[-1][1])
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

            del(moves[i])
            moves.extend(correct_next_moves)

            if i == len(moves):
                break;

        moves_with_attack = []
        for move in moves:
            if len(move.beaten_cells) > 0:
                moves_with_attack.append(move)
        if len(moves_with_attack) > 0:
            return moves_with_attack
        else:
            return moves

    def get_all_possible_moves(self) -> List['BoardState']:
        """
        :return: list of BoardStates with  all possible moves
        """
        boards = []
        is_attack = False

        for y in np.arange(0, 8):
            for x in np.arange(0, 8):
                moves = self.get_possible_moves(x, y, is_attack)
                if len(moves) == 0:
                    continue
                if not is_attack and len(moves[0].beaten_cells) > 0:
                    is_attack = True
                    boards = []
                    for move in moves:
                        boards.append(self.do_correct_move(x, y, move))

                if is_attack and len(moves[0].beaten_cells) > 0:
                    for move in moves:
                        boards.append(self.do_correct_move(x, y, move))

                if not is_attack and len(moves[0].beaten_cells) == 0:
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
        if abs(result.board[from_x, from_y]) != 2 and was_queen:
            result.player_checks -= 1
            result.player_queens += 1

        for cell in move.beaten_cells:
            result.opponent_checks -= abs(result.board[cell[1], cell[0]])
            result.board[cell[1], cell[0]] = 0

        result.board[
            move.visited_cells[-1][1],
            move.visited_cells[-1][0]] = result.board[from_y, from_x]
        if was_queen and abs(result.board[from_y, from_x]) == 1:
            result.board[
            move.visited_cells[-1][1],
            move.visited_cells[-1][0]] *= 2

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

    def get_possible_moves_for_ordinary(self, from_x, from_y, is_attack = False) -> List['Move']:
        moves_with_attack = []
        moves_without_attack = []
        for y in [from_y - 1, from_y + 1]:
            for  x in [from_x - 1, from_x + 1]:
                if self.is_in_board(x, y):
                    if not is_attack and self.board[y, x] == 0 and y == from_y - 1:
                        moves_without_attack.append(Move(x, y, False, is_queen = (y == 0)))

                    if self.board[y, x] * self.current_player < 0:
                        next_y, next_x = 2 * y - from_y, 2 * x - from_x
                        if (self.is_in_board(next_x, next_y) and
                                self.board[next_y, next_x] == 0):
                            is_attack = True
                            moves_with_attack.append(
                                Move(next_x,
                                     next_y,
                                     True, x, y,
                                     is_queen = (next_y == 0)))
        return moves_with_attack if is_attack else moves_without_attack

    def get_possible_moves_for_queen(self, from_x, from_y, is_attack = False) -> List['Move']:
        moves_with_attack = []
        moves_without_attack = []
        def moves_for_direction(x_direction: int, y_direction: int):
            was_attack = False
            beaten_cell_x = None
            beaten_cell_y = None
            to_x, to_y = from_x, from_y
            while True:
                nonlocal is_attack
                to_x += x_direction
                to_y += y_direction
                if not self.is_in_board(to_x, to_y):
                    break

                if not is_attack and self.board[to_y, to_x] == 0:
                    moves_without_attack.append(
                        Move(to_x,
                             to_y,
                             was_attack,
                             beaten_cell_x,
                             beaten_cell_y,
                             is_queen = True))

                if was_attack and self.board[to_y, to_x] == 0:
                    is_attack = True
                    moves_with_attack.append(
                        Move(to_x,
                             to_y,
                             was_attack,
                             beaten_cell_x,
                             beaten_cell_y,
                             is_queen = True))

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
        return moves_with_attack if is_attack else moves_without_attack


    def __getstate__(self) -> dict:
        state = {}
        state["board"] = self.board
        state["current_player"] = self.current_player
        state["player_checks"] = self.player_checks
        state["opponent_checks"] = self.opponent_checks
        state["player_queens"] = self.player_queens
        state["opponent_queens"] = self.opponent_queens
        return state

    def __setstate__(self, state: dict):
        self.board = state["board"]
        self.current_player = state["current_player"]
        self.player_checks = state['player_checks']
        self.opponent_checks = state['opponent_checks']
        self.player_queens = state['player_queens']
        self.opponent_queens = state['opponent_queens']

    @property
    def is_game_finished(self) -> bool:
        ... # todo

    @property
    def get_winner(self) -> Optional[int]:
        if self.get_figures_count(self.current_player) == 0:
            print('gg_count')
            return -1 * self.current_player
        if len(self.get_all_possible_moves()) == 0:
            print('gg_moves')
            return -1 * self.current_player
        return 0

    def get_figures_count(self, player: int):
        count = 0
        for row in self.board:
            for cell in row:
                if player * cell > 0:
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
                board[6, x] = 1
                board[2, x] = -1

        return BoardState(board, 1)
