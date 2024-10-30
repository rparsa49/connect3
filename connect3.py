from concurrent.futures import ThreadPoolExecutor, Future
from typing import Optional

import numpy as np
import pygame
import sys

from ai import move_for_player_2, Board

# Constants
ROW_COUNT = 4
COLUMN_COUNT = 5
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

PLAYER1 = 1
PLAYER2 = 2

# Initialize Pygame
pygame.init()

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
screen = pygame.display.set_mode(size)
myfont = pygame.font.SysFont("monospace", 25)

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Check horizontal locations
    for c in range(COLUMN_COUNT - 2):
        for r in range(ROW_COUNT):
            if all(board[r][c+i] == piece for i in range(3)):
                return True

    # Check vertical locations
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 2):
            if all(board[r+i][c] == piece for i in range(3)):
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 2):
        for r in range(ROW_COUNT - 2):
            if all(board[r+i][c+i] == piece for i in range(3)):
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 2):
        for r in range(2, ROW_COUNT):
            if all(board[r-i][c+i] == piece for i in range(3)):
                return True

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER1:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == PLAYER2:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


def get_clicked_col(event) -> int:
    posx = event.pos[0]
    return int(posx / SQUARESIZE)


def ndarray_to_tuple(arr: np.ndarray) -> Board:
    return tuple(tuple(arr[i]) for i in range(ROW_COUNT))



if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=1,) as ai_thread:
        ai_fut: Optional[Future] = None
        # Game Setup
        board = create_board()
        game_over = False
        turn = PLAYER1

        draw_board(board)
        pygame.display.update()

        while not game_over:
            if turn != PLAYER1:
                if ai_fut is None:
                    ai_fut = ai_thread.submit(move_for_player_2, ndarray_to_tuple(board))
                elif ai_fut.done():
                    col = ai_fut.result()
                    ai_fut = None
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER2)
                    if winning_move(board, PLAYER2):
                        label = myfont.render("Computer wins!", 1, YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True
                    turn += 1
                    turn = turn % 2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                    posx = event.pos[0]
                    if turn == PLAYER1:
                        pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))

                    # Ask for Player 1 Input
                    if turn == PLAYER1:
                        col = get_clicked_col(event)
                        if not is_valid_location(board, col):
                            continue
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER1)

                        if winning_move(board, PLAYER1):
                            label = myfont.render("Human wins!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True
                        turn += 1
                        turn = turn % 2


            #print_board(board)
            draw_board(board)

            if game_over:
                pygame.time.wait(3000)
