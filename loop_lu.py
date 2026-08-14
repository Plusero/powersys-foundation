import numpy as np


def loop_lu(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a_n = np.array(matrix, dtype=float, copy=True)
    l_n = np.eye(a_n.shape[0], dtype=float)
    u_n = np.zeros_like(a_n, dtype=float)

    if a_n.ndim != 2 or a_n.shape[0] != a_n.shape[1]:
        raise ValueError("matrix must be square")
    if a_n.shape[0] == 0:
        raise ValueError("matrix must not be empty")


    for i in range(a_n.shape[0]):
        n = a_n.shape[0]
        # base case for recursion
        if n == 1:
            u_n[i, i] = a_11
            break
        # partition A
        a_11 = a_n[0, 0]
        w = a_n[0, 1:].copy()
        v = a_n[1:, 0].copy()
        a_n_minus_1 = a_n[1:, 1:]


        # the four equations
        u_11 = a_11
        u = w.copy()
        ell = v / u_11
        s = a_n_minus_1 - np.outer(ell, u)
        
        # fill L and U matrices
        l_n[i + 1:, i] = ell
        u_n[i, i+1:] = u
        u_n[i, i] = u_11

        # update the matrix for the next LU iteration   
        a_n=s

    return l_n, u_n

a_n = np.array(
    [
        [10.0, -1.0,  2.0,  0.0],
        [-1.0, 11.0, -1.0,  3.0],
        [ 2.0, -1.0, 10.0, -1.0],
        [ 0.0,  3.0, -1.0,  8.0],
    ]
)

l_n, u_n = loop_lu(a_n)
print("L matrix:\n", l_n)
print("U matrix:\n", u_n)