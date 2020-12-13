import mip
import numpy as np

def solve(adj: np.ndarray) -> tuple[float, list[int]]:
    n: int = adj.shape[0]
    model = mip.Model()
    edge_var = model.add_var_tensor(shape=(n,n), name="edge", var_type=mip.BINARY)
    subtour_var = model.add_var_tensor(shape=(n,), name="subtour", var_type=mip.CONTINUOUS)

    # minimize total distance
    model.objective = mip.minimize(mip.xsum([adj[node1, node2] * edge_var[node1, node2] for node1 in range(n) for node2 in range(n)]))
    # constraints
    # no self edge edge_var[i][i]
    model.add_constr(mip.xsum([edge_var[node][node] for node in range(n)]) == 0)
    # leave each city once
    for from_node in range(n):
        model.add_constr(mip.xsum(edge_var[from_node, :]) == 1)
    # enter each city once
    for to_node in range(n):
        model.add_constr(mip.xsum(edge_var[:, to_node]) == 1)
    # eliminate subtour - linear ordering
    for node1 in range(1, n):
        for node2 in range(1, n):
            if node1 == node2:
                continue
            model.add_constr(subtour_var[node2] - subtour_var[node1] >= (n+1) * edge_var[node1][node2] - n)

    # optimize
    model.optimize()
    if model.num_solutions:
        cost = float(model.objective_value)
        tour = [0]
        while len(tour) < n:
            for next_node in range(n):
                if edge_var[tour[-1], next_node].x > 0.5:
                    tour.append(next_node)
                    break
        return cost, tour
    return float("inf"), []