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

if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    from sparse_uls.uls import solve_l1

    np.random.seed(1234)


    def draw_hist(x: np.ndarray, title: str = "norm", draw: bool = False):
        hist, edge = np.histogram(x, bins=101, range=[-0.1, +0.1])
        center = np.array([0.5 * (edge[i] + edge[i + 1]) for i in range(len(hist))])
        print(
            f"middle [{edge[int(len(hist) / 2)]}, {edge[1 + int(len(hist) / 2)]}] occurences: {hist[int(len(hist) / 2)]}")
        if draw:
            plt.title(title)
            plt.xlabel("values")
            plt.ylabel("occurrences")
            plt.bar(center, hist, width=(center[1] - center[0]))
            plt.show()


    def norm_p(x: np.ndarray, p: float = 2.0) -> float:
        if p > 0:
            return np.sum(np.abs(x) ** p) ** (1 / p)
        return (x != 0).sum()


    n = 10
    m = 2
    A = np.random.random(size=(m, n)).astype(dtype=np.float64)
    b = np.random.random(size=(m)).astype(dtype=np.float64)

    def draw(x: np.ndarray, p: int):
        print(f"\tconstraints: {np.max(np.abs(A @ x - b))}")
        print(f"\tL^{p} norm: {norm_p(x, p)}")
        draw_hist(x, f"L^{p} norm", draw=True)

    x0 = solve_l0(A, b)
    draw(x0, 0)
    x1 = solve_l1(A, b)
    draw(x1, 1)
    pass