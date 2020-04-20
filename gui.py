from itertools import product

from typing import Optional

import pickle

import pygame
from pygame import Surface

from src.ai import AI, PositionEvaluation
from src.boardstate import BoardState


def draw_board(screen: Surface, pos_x: int, pos_y: int, elem_size: int, board: BoardState):
    dark = (0, 0, 0)
    white = (200, 200, 200)

    for y, x in product(range(8), range(8)):
        color = white if (x + y) % 2 == 0 else dark
        position = pos_x + x * elem_size, pos_y + y * elem_size, elem_size, elem_size
        pygame.draw.rect(screen, color, position)

        figure = board.board[y, x]

        if figure == 0:
            continue

        if figure > 0:
            figure_color = 255, 255, 255
        else:
            figure_color = 100, 100, 100
        r = elem_size // 2 - 10

        pygame.draw.circle(screen, figure_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)
        if abs(figure) == 2:
            r = 5
            negative_color = [255 - e for e in figure_color]
            pygame.draw.circle(screen, negative_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)

def save_board(board: BoardState, filename: str):
    with open(filename, "wb") as fp:
        pickle.dump(board, fp)

def load_board(filename: str) -> Optional['BoardState']:
    with open(filename, "rb") as fp:
        return pickle.load(fp)

def draw_final_message(screen, player):
    winners = ''
    if player == 1:
        winners = "WHITE "
    else:
        winners = "BLACK "
    message = winners + 'WINS!'
    font = pygame.font.SysFont('Comic Sans Serif', 64)
    message_block = pygame.Surface((screen.get_size()[0], 50))
    message_block.blit(font.render(message, 1, (0, 250, 0)), (120, 3))
    screen.blit(message_block, (0, 0))



def game_loop(screen: Surface, board: BoardState, ai: AI):
    grid_size = screen.get_size()[0] // 8
    previous_board = board
    visible_board = board
    step = 0
    flag = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click_position = event.pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                new_x, new_y = [p // grid_size for p in event.pos]
                old_x, old_y = [p // grid_size for p in mouse_click_position]

                new_board = board.do_move(old_x, old_y, new_x, new_y)
                if new_board is not None:
                    previous_board = board
                    board = new_board.inverted()
                    if step % 2 == 0:
                        visible_board = new_board
                    else:
                        visible_board = board
                    step += 1

            #if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                #x, y = [p // grid_size for p in event.pos]
                #board.board[y, x] = (board.board[y, x] + 1 + 2) % 5 - 2  # change figure

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = board.inverted()
                elif event.key == pygame.K_n:
                    board = board.initial_state()
                elif event.key == pygame.K_s:
                    save_board(visible_board, './src/save.bin')
                elif event.key == pygame.K_l:
                    board = load_board('./src/save.bin')
                    visible_board = board
                elif event.key == pygame.K_z:
                    board = previous_board
                if event.key == pygame.K_SPACE:
                    new_board = ai.next_move(board)
                    if new_board is not None:
                        previous_board = board
                        board = new_board.inverted()
                        if step % 2 == 0:
                            visible_board = new_board
                        else:
                            visible_board = board
                        step += 1

        draw_board(screen, 0, 0, grid_size, visible_board)
        if board.get_winner != 0:
            draw_final_message(screen, board.get_winner)

            print("GG")
        pygame.display.flip()

pygame.font.init()
pygame.init()

pygame.display.set_caption('Russian Checkers')

screen: Surface = pygame.display.set_mode([512, 512])
ai = AI(PositionEvaluation(), search_depth=4)

game_loop(screen, BoardState.initial_state(), ai)

pygame.quit()
