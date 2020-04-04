from typing import Callable

import pygame

from game.board import Board
from src.constants import *


def pymill_hotseat(on_game_exit: Callable):
    pygame.display.init()
    pygame.font.init()

    window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
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
                    if board.mouse_over_node():
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
