from typing import Callable

import pygame

from src.game.board import Board
from src.constants import *


def pymill_hotseat(on_game_exit: Callable):
    width = 800
    height = 600
    current_scale = 1

    pygame.display.init()
    pygame.font.init()

    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("PyMill")
    clock = pygame.time.Clock()

    board = Board()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if board.mouse_over_any_node():
                        board.node_pressed = True
                    if not board.must_remove_piece:
                        if board.phase == PHASE2:
                            board.pick_up_piece()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    if board.must_remove_piece:
                        if board.node_pressed:
                            board.remove_opponent_piece()
                    if board.phase == PHASE1:
                        if board.node_pressed:
                            board.put_new_piece()
                    else:
                        board.put_down_piece()
                board.node_pressed = False
            elif event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_p:
                #     board.put_new_piece_alone(0, WHITE)
                # elif event.key == pygame.K_c:
                #     board.change_piece_location(23, 8)
                if event.key == pygame.K_MINUS:
                    if current_scale > 1:
                        width -= 160
                        height -= 120
                        window = pygame.display.set_mode((width, height))  # TODO also resize the text
                        board.on_window_resize(width, height)
                        current_scale -= 1
                elif event.key == pygame.K_EQUALS:
                    if current_scale < 5:
                        width += 160
                        height += 120
                        window = pygame.display.set_mode((width, height))
                        board.on_window_resize(width, height)
                        current_scale += 1

        mouse = pygame.mouse.get_pos()
        board.update(mouse)

        if board.game_over:
            print("GAME OVER")

        window.fill((148, 16, 148))
        board.render(window)
        pygame.display.flip()
        clock.tick(30)

    on_game_exit()
    pygame.quit()
