import random
import numpy as np
import database


COLUMNS = 7
ROWS = 6


class Board:

    def __init__(self):
        self.matrix = np.zeros((ROWS, COLUMNS))
        self.cols = {i: ROWS - 1 for i in range(COLUMNS)}
        self.last_move = (None, None)

    def hash(self):
        return tuple(self.matrix.flat)

    def col(self, n):
        return self.cols[n] > -1

    def add(self, col, turn):
        row = self.cols[col]
        copy = np.copy(self.matrix)
        copy[row][col] = 1 + (not turn * 1)
        obj = Board()
        obj.matrix = copy
        obj.cols = self.cols.copy()
        obj.cols[col] -= 1
        obj.last_move = (row, col)
        return obj

    def _check_four_monotony(self, arr):
        if arr.size == 0:
            return False
        count = 1
        a = arr[0]
        for b in arr[1:]:
            if b - a == 1:
                count += 1
                if count == 4:
                    return True
            else:
                count = 1
            a = b
        return False

    def is_winning_move(self):
        row, col = self.last_move
        turn = self.matrix[row, col]
        dots_row = np.where(self.matrix[row] == turn)
        if self._check_four_monotony(dots_row[0]):
            return True
        dots_col = np.where(self.matrix[:, col] == turn)
        if self._check_four_monotony(dots_col[0]):
            return True
        dots_diagonal = np.where(np.diagonal(self.matrix, col - row) == turn)
        if self._check_four_monotony(dots_diagonal[0]):
            return True
        dots_diagonal_back = np.where(np.fliplr(self.matrix).diagonal(COLUMNS - 1 - col - row) == turn)
        if self._check_four_monotony(dots_diagonal_back[0]):
            return True
        return False


memo = database.db_to_dict()

DEPTH = 3


class EnginePlayer:
    def __init__(self):
        self.board = Board()
        self.first = None
        self.count_moves = 0

    def make_move(self):
        col = self.best_move()
        self.board = self.board.add(col, self.first)
        self.count_moves += 1
        print(f'{1 if self.first else 2} move:', col)
        return col


    def opponent_move(self, col):
        self.board = self.board.add(col, not self.first)
        self.count_moves += 1
        print(f'{2 if self.first else 1} move:', col)

    # min max algorithm
    def best_move(self):
        if self.count_moves < 4:
            depth = DEPTH - 2
        else:
            depth = 0
        board = self.board
        evaluation = {}
        for col in range(COLUMNS):
            if board.col(col):
                moved = board.add(col, self.first)
                value = self.evaluate_position(moved, not self.first, depth=depth)
                evaluation[value] = evaluation.get(value, [])
                evaluation[value].append(col)

        min_or_max = max if self.first else min
        best = min_or_max(evaluation)
        print(evaluation, best)
        return random.choice(evaluation[best])

    def evaluate_position(self, board, first_turn, depth=0):
        if board.hash() in memo:
            return memo[board.hash()]

        win = board.is_winning_move()
        if win:
            winner = -1 if first_turn else 1
            database.store_position(board.hash(), winner)
            memo[board.hash()] = winner
            return winner
        else:
            if depth == DEPTH:
                return 0

        moves = {}
        for col in range(COLUMNS):
            if board.col(col):
                moved = board.add(col, first_turn)
                value = self.evaluate_position(moved, not first_turn, depth=depth + 1)
                if value != 0:
                    memo[moved.hash()] = value
                    database.store_position(moved.hash(),value)
                moves[value] = moves.get(value, [])
                moves[value].append(col)
                if first_turn and value == 1:
                    return 1
                if not first_turn and value == -1:
                    return -1

        min_or_max = max if first_turn else min
        # print(moves,depth)
        try:
            evaluation = min_or_max(moves)
        except ValueError:
            return 0

        return evaluation

#
# b = Board()
# b.matrix = np.array([[0., 0., 0., 0., 0., 0., 0.],
#                      [0., 0., 0., 0., 0., 0., 0.],
#                      [0., 0., 1., 0., 0., 0., 0.],
#                      [0., 0., 2., 0., 1., 0., 0.],
#                      [0., 0., 1., 2., 1., 0., 0.],
#                      [2., 1., 1., 2., 2., 0., 0.]])
# b.cols = {0: 4, 1: 4, 2: 1, 3: 3, 4: 2, 5: 5, 6: 5}
# b.last_move = (2, 2)
# m = best_move(b, False)
# print('best =', m)
# # print([(np.array(i).reshape((6, 7)), j) for i, j in memo.items()])
