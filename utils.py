import threading
import numpy as np


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


COL = 7
ROW = 6


def get_indices_of_diagonal(size, d_num, flip=False):
    r, c = np.indices(size)
    if flip:
        c = np.flip(c)
    return list(zip(np.diagonal(r, d_num), np.diagonal(c, d_num)))


def find4(arr, row, col, val):
    c = []
    for i in range(ROW):
        if arr[i][col] == val:
            c.append((i, col))
            if len(c) == 4:
                return True, c
        else:
            c = []
    c = []
    for j in range(COL):
        if arr[row][j] == val:
            c.append((row, j))
            if len(c) == 4:
                return True, c
        else:
            c = []

    c = []
    for a, b in get_indices_of_diagonal((ROW, COL), col - row):
        if arr[a][b] == val:
            c.append((a, b))
            if len(c) == 4:
                return True, c
        else:
            c = []
    c = []
    for a, b in get_indices_of_diagonal((ROW, COL), COL - 1 - col - row, flip=True):
        if arr[a][b] == val:
            c.append((a, b))
            if len(c) == 4:
                return True, c
        else:
            c = []
    return False, []

def parse_msg(msg):
    if not msg:
        raise Exception(f'BAD MESSAGE -> {msg}')
    parser = eval(msg.decode())
    return parser

