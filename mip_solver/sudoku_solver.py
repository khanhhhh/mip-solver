from typing import Optional

import mip
import numpy as np

def solve(board: np.ndarray, block: int) -> Optional[np.ndarray]:
    size: int = block ** 2
    model = mip.Model()
    model.verbose = False
    # variable: x[row, col, symbol] = 1 if board[row, col] = symbol
    x = model.add_var_tensor(shape=(size, size, size), var_type=mip.BINARY, name="x")
    # constraints
    # board
    for row in range(size):
        for col in range(size):
            if board[row, col] in range(size):
                model.add_constr(x[row, col, board[row, col]] == 1)
    # each (row, col) has 1 symbol
    for row in range(size):
        for col in range(size):
            model.add_constr(mip.xsum(x[row, col, :]) == 1)
    # each (row, symbol) has 1 col
    for row in range(size):
        for symbol in range(size):
            model.add_constr(mip.xsum(x[row, :, symbol]) == 1)
    # each (col, symbol) has 1 row
    for col in range(size):
        for symbol in range(size):
            model.add_constr(mip.xsum(x[:, col, symbol]) == 1)
    # each (block x block) block
    for tp_r in range(0, size, block):
        for tp_c in range(0, size, block):
            for symbol in range(size):
                model.add_constr(mip.xsum(x[tp_r:tp_r + block, tp_c:tp_c + block, symbol].flatten()) == 1)
    # solve
    model.optimize()
    if model.num_solutions:
        solution = np.empty(shape=(size, size), dtype=int)
        for row in range(size):
            for col in range(size):
                for symbol in range(size):
                    if x[row, col, symbol].x > 0.5:
                        solution[row, col] = symbol
        return solution
    return None
