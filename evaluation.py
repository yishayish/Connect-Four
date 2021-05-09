def evaluate_position(self, board, first_turn, depth=0):
    if board.hash() in memo:
        return memo[board.hash()]

    win = board.is_winning_move()
    if win:
        winner = -1 if first_turn else 1
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
                depth = DEPTH - abs(value)

            # there is a win in one move
            # if value == 1:
            #     return 2
            # if value == -1:
            #     return -2

            moves[value] = moves.get(value, [])
            moves[value].append(col)

    min_or_max = max if first_turn else min
    # print(moves,depth)

    evaluation = min_or_max(moves)
    if evaluation > 0:
        return evaluation + 1
    elif evaluation < 0:
        return evaluation - 1
    else:
        return 0
