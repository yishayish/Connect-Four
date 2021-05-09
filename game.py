import numpy as np
import utils

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 65, 0)
RED = (204, 0, 0)
GREEN = (0, 153, 0)
BLUE = (0, 100, 255)
# COLORS = {1: RED, 2: GREEN}

ROWS = 6
COLUMNS = 7
SQUARE_SIZE = 80

width = COLUMNS * SQUARE_SIZE
height = (ROWS + 1) * SQUARE_SIZE


class ConnectDotsGame:

    def __init__(self):
        self.game_over = False
        self.turn = 0
        self.board = np.zeros((ROWS, COLUMNS))
        self.next_pos = [ROWS - 1] * COLUMNS
        self.four_in_row = []

    def check_winning(self, row, col, turn):
        win, self.four_in_row = utils.find4(self.board, row, col, turn)
        return win

    def is_validate_location(self, col):
        return self.next_pos[col] > -1

    def add_disc(self, col):
        if (next_pos := self.next_pos[col]) != -1:
            self.board[next_pos][col] = self.turn + 1
            self.next_pos[col] -= 1
            win = self.check_winning(next_pos, col, self.turn + 1)
            if win:
                self.game_over = True
            else:
                self.turn = 1 - self.turn
            return next_pos, col, win
