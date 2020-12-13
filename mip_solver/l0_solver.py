from typing import Optional

import mip
import numpy as np

def solve_l0(A: np.ndarray, b: np.ndarray, bound: float=1e3) -> Optional[np.ndarray]:
    """
    minimize ||x||_0
    such that Ax = b
    """
    m, n = A.shape
    model = mip.Model()

    # x = x_con, x_bin[i] == 1 if and only if x_con != 0
    x_bin = model.add_var_tensor(shape=(n,), name="x_bin", var_type=mip.BINARY)
    x_con = model.add_var_tensor(shape=(n,), name="x_con", var_type=mip.CONTINUOUS, lb=-bound, ub=+bound)
    # minimize number of non-zero elements
    model.objective = mip.minimize(mip.xsum(x_bin))
    # constraints
    # x_bin[i] == 1 if and only if x_con != 0
    for j in range(n):
        model.add_constr(x_con[j] <= +bound * x_bin[j])
        model.add_constr(-bound * x_bin[j] <= x_con[j])
    # Ax = b
    for i in range(m):
        model.add_constr(mip.xsum([A[i, j] * x_con[j] for j in range(n)]) == b[i])

    # optimize
    model.optimize()
    if model.num_solutions:
        x = np.empty(shape=(n,), dtype=float)
        for j in range(n):
            x[j] = x_con[j].x
        return x

    return None
