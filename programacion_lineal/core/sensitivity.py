"""Análisis de sensibilidad para la solución símplex."""

from __future__ import annotations

import numpy as np

from .simplex_engine import basic_row


def sensitivity(T, vb, c_int, c_orig, A, b, tipos, is_max):
    """Calcula las tablas de sensibilidad sin alterar los cálculos actuales."""
    n, m = len(c_int), len(b)
    art_idx = [i for i, t in enumerate(tipos) if t in (">=", "=")]
    art_map = {i: k for k, i in enumerate(art_idx)}
    sign = 1 if is_max else -1
    sol = np.zeros(n)
    for j in range(n):
        cv = T[:, j + 1]
        ones = np.where(np.abs(cv - 1) < 1e-8)[0]
        if len(ones) == 1 and np.count_nonzero(np.abs(cv) > 1e-8) == 1:
            sol[j] = T[ones[0], -1]
    cb = np.array([c_int[int(v[1:]) - 1] if v.startswith("X") else 0.0 for v in vb])

    var_rows = []
    for j in range(n):
        col = j + 1
        val = sol[j]
        cj_orig = c_orig[j]
        br = basic_row(T, col)
        rc = sign * (-T[0, col])
        if br is not None and br > 0:
            z_row = T[0, 1:-1]
            t_row = T[br, 1:-1]
            incs, decs = [], []
            for k in range(n + m):
                if basic_row(T, k + 1) is None and k != j:
                    zk, trk = z_row[k], t_row[k]
                    if abs(trk) > 1e-10:
                        if trk < 0:
                            incs.append(zk / abs(trk))
                        else:
                            decs.append(zk / trk)
            ai_int = min(incs) if incs else np.inf
            ad_int = min(decs) if decs else np.inf
        else:
            ai_int = T[0, col]
            ad_int = np.inf
        ai_d, ad_d = (ai_int, ad_int) if is_max else (ad_int, ai_int)
        cm = cj_orig - ad_d if ad_d < np.inf else -np.inf
        cx = cj_orig + ai_d if ai_d < np.inf else np.inf
        var_rows.append((f"X{j+1}", val, rc, cj_orig, ai_d, ad_d, cm, cx))

    rest_rows = []
    for i in range(m):
        lhs = float(np.dot(A[i], sol))
        rhs = b[i]
        tipo = tipos[i]
        id_col = (n + i + 1) if tipo == "<=" else (n + m + art_map[i] + 1)
        d = T[1:, id_col]
        shadow = sign * float(np.dot(cb, d))
        bbar = T[1:, -1]
        incs, decs = [], []
        for r in range(m):
            if d[r] < -1e-10:
                incs.append(-bbar[r] / d[r])
            elif d[r] > 1e-10:
                decs.append(bbar[r] / d[r])
        ai = min(incs) if incs else np.inf
        ad = min(decs) if decs else np.inf
        rm = rhs - ad if ad < np.inf else -np.inf
        rx = rhs + ai if ai < np.inf else np.inf
        rest_rows.append((f"R{i+1} ({tipo})", lhs, shadow, rhs, ai, ad, rm, rx))
    return var_rows, rest_rows, sol
