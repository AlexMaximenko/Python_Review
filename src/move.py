from typing import Optional, List
import pygame


class Move:
    def __init__(self, to_x: int = 0, to_y:int = 0, is_atack: bool = False):
        self.to_x = to_x
        self.to_y = to_y
        self.is_atack = is_atack
    def __repr__(self):
        return ("Move to x = {}, y = {}, is_atack = {}".format(self.to_x, self.to_y, self.is_atack))
