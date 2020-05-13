from typing import Optional, List
import pygame


class Move:
    def __init__(self, to_x: int = 0, to_y:int = 0, is_attack: bool = False, beaten_cell_x:int = None, beaten_cell_y: int = None, is_queen: bool = False):
        self.visited_cells = []
        self.is_queen = is_queen
        self.visited_cells.append((to_x, to_y))
        self.is_attack = is_attack
        self.beaten_cells = []
        if beaten_cell_x != None and beaten_cell_y != None:
            self.beaten_cells.append((beaten_cell_x, beaten_cell_y));

    def add_visited_cell(self, to_x, to_y):
        self.visited_cells.append((to_x, to_y))

    def __repr__(self):
        str1 = str(self.beaten_cells)
        str2 = str(self.visited_cells)
        return ("Move: visited_cells = {}, is_attack = {}, is_queen = {}, beaten_cells : {}".format(self.visited_cells, self.is_attack, self.is_queen, self.beaten_cells))

    def __eq__(self, other):
        return self.visited_cells[-1] == other.visited_cells[-1] and self.is_attack == other.is_attack
