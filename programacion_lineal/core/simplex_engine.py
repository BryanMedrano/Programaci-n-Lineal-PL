"""Motor Símplex Big-M y utilidades básicas de tableau."""

from __future__ import annotations

import numpy as np


def parse_tipo(s):
    """Normaliza el tipo de restricción sin alterar la semántica actual."""
    s = s.strip()
    if s in ("<=", "≤"):
        return "<="
    if s in (">=", "≥"):
        return ">="
    return "="


def simplex_engine(A, b, c, tipos):
    """Ejecuta el método Símplex Big-M exactamente con la lógica vigente."""
    M_BIG = 1e8
    n, m = len(c), len(b)
    art_idx = [i for i, t in enumerate(tipos) if t in (">=", "=")]
    art_map = {i: k for k, i in enumerate(art_idx)}
    n_art = len(art_idx)
    N = n + m + n_art

    col_names = (
        [f"X{j+1}" for j in range(n)]
        + [f"S{i+1}" for i in range(m)]
        + [f"A{k+1}" for k in range(n_art)]
    )
    vb = [f"S{i+1}" if tipos[i] == "<=" else f"A{art_map[i]+1}" for i in range(m)]

    T = np.zeros((m + 1, 1 + N + 1))
    T[0, 0] = 1
    T[0, 1 : n + 1] = -np.array(c, float)
    for k, i in enumerate(art_idx):
        T[0, n + m + k + 1] = M_BIG
    for i in range(m):
        T[i + 1, 1 : n + 1] = A[i]
        sc = n + i + 1
        if tipos[i] == "<=":
            T[i + 1, sc] = 1
        elif tipos[i] == ">=":
            T[i + 1, sc] = -1
            T[i + 1, n + m + art_map[i] + 1] = 1
        else:
            T[i + 1, n + m + art_map[i] + 1] = 1
        T[i + 1, -1] = b[i]
    for k, i in enumerate(art_idx):
        T[0] -= M_BIG * T[i + 1]

    history = []
    it = 0
    while it < 300:
        zrow = T[0, 1:-1]
        if np.all(zrow >= -1e-8):
            history.append({"iter": it, "T": T.copy(), "vb": vb[:], "col_names": col_names,
                            "piv_col": None, "status": "optimal"})
            break
        ec = int(np.argmin(zrow)) + 1
        history.append({"iter": it, "T": T.copy(), "vb": vb[:], "col_names": col_names,
                        "piv_col": ec, "enter": col_names[ec - 1]})
        ratios = [T[i, -1] / T[i, ec] if T[i, ec] > 1e-10 else np.inf for i in range(1, m + 1)]
        if min(ratios) == np.inf:
            return None, T, col_names, vb, history, "unbounded"
        pr = int(np.argmin(ratios)) + 1
        history[-1]["leave"] = vb[pr - 1]
        vb[pr - 1] = col_names[ec - 1]
        T[pr] /= T[pr, ec]
        for i in range(m + 1):
            if i != pr:
                T[i] -= T[i, ec] * T[pr]
        it += 1

    for r, bv in enumerate(vb):
        if bv.startswith("A") and T[r + 1, -1] > 1e-6:
            return None, T, col_names, vb, history, "infeasible"

    sol = np.zeros(n)
    for j in range(n):
        cv = T[:, j + 1]
        ones = np.where(np.abs(cv - 1) < 1e-8)[0]
        if len(ones) == 1 and np.count_nonzero(np.abs(cv) > 1e-8) == 1:
            sol[j] = T[ones[0], -1]
    return sol, T, col_names, vb, history, "ok"


def basic_row(T, col_1idx):
    """Devuelve la fila básica de una columna 1-indexada si existe."""
    cv = T[:, col_1idx]
    ones = np.where(np.abs(cv - 1) < 1e-8)[0]
    if len(ones) == 1 and np.count_nonzero(np.abs(cv) > 1e-8) == 1:
        return int(ones[0])
    return None
