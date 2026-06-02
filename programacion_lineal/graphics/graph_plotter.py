"""Dibujo del método gráfico para problemas con dos variables."""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from scipy.spatial import ConvexHull

from ..config.palette import PAL, REST_COLORS, fmt


def is_feasible(p, A, b, tipos, tol=1e-5):
    """Indica si un punto pertenece a la región factible."""
    for k in range(len(A)):
        lhs = float(np.dot(A[k], p))
        if tipos[k] == "<=" and lhs > b[k] + tol:
            return False
        if tipos[k] == ">=" and lhs < b[k] - tol:
            return False
        if tipos[k] == "=" and abs(lhs - b[k]) > tol:
            return False
    return True


def get_vertices(A, b, tipos):
    """Calcula vértices factibles para el método gráfico."""
    m, pts = len(b), []
    if is_feasible([0.0, 0.0], A, b, tipos):
        pts.append(np.zeros(2))
    for i in range(m):
        for j in range(i + 1, m):
            Mt = np.array([A[i], A[j]], float)
            if abs(np.linalg.det(Mt)) > 1e-10:
                try:
                    p = np.linalg.solve(Mt, [b[i], b[j]])
                    if np.all(p >= -1e-5):
                        p = np.maximum(p, 0.0)
                        if is_feasible(p, A, b, tipos):
                            pts.append(p)
                except Exception:
                    pass
    for i in range(m):
        a1, a2 = float(A[i][0]), float(A[i][1])
        if abs(a1) > 1e-10:
            p = np.array([b[i] / a1, 0.0])
            if p[0] >= -1e-5 and is_feasible(np.maximum(p, 0.0), A, b, tipos):
                pts.append(np.maximum(p, 0.0))
        if abs(a2) > 1e-10:
            p = np.array([0.0, b[i] / a2])
            if p[1] >= -1e-5 and is_feasible(np.maximum(p, 0.0), A, b, tipos):
                pts.append(np.maximum(p, 0.0))
    uniq = []
    for p in pts:
        if not any(np.linalg.norm(p - q) < 1e-4 for q in uniq):
            uniq.append(p)
    return np.array(uniq) if uniq else np.empty((0, 2))


def draw_graph(ax, A, b, sol, c_orig, tipos, is_max):
    """Dibuja la región factible y la recta objetivo con la estética actual."""
    ax.set_facecolor("#FFFFFF")
    fig = ax.get_figure()
    fig.patch.set_facecolor("#F5F7FA")

    m = len(b)
    verts = get_vertices(A, b, tipos)

    all_x = np.concatenate([verts[:, 0] if len(verts) > 0 else [], [sol[0], 1.0]])
    all_y = np.concatenate([verts[:, 1] if len(verts) > 0 else [], [sol[1], 1.0]])
    xd, yd = max(float(all_x.max()), 1.0), max(float(all_y.max()), 1.0)
    mg = 0.32 if xd < 20 else (0.22 if xd < 150 else 0.14)
    xl, yl = xd * (1 + mg), yd * (1 + mg)

    x = np.linspace(0, xl, 2000)

    ax.grid(True, which="major", color="#D5DCE8", linewidth=0.8, zorder=0)
    ax.grid(True, which="minor", color="#E8EDF4", linewidth=0.35, zorder=0)
    ax.set_axisbelow(True)

    if len(verts) >= 3:
        try:
            hull = ConvexHull(verts)
            hp = verts[hull.vertices]
            poly = plt.Polygon(hp, closed=True,
                               facecolor="#1A5276", alpha=0.12,
                               edgecolor="#1A5276", linewidth=0,
                               zorder=1, label="Región factible")
            ax.add_patch(poly)
            border = np.vstack([hp, hp[0]])
            ax.plot(border[:, 0], border[:, 1],
                    color="#1A5276", lw=1.2, alpha=0.45,
                    linestyle="--", zorder=2)
        except Exception:
            pass
    elif len(verts) == 2:
        ax.plot(verts[:, 0], verts[:, 1],
                color="#4F8EF7", lw=1.5, alpha=0.6, zorder=2)

    legend_handles = []
    for i in range(m):
        a1, a2 = float(A[i][0]), float(A[i][1])
        col = REST_COLORS[i % len(REST_COLORS)]
        parts = []
        for j, aj in enumerate([a1, a2]):
            if abs(aj) < 1e-10:
                continue
            vname = f"X{j+1}"
            if abs(aj - 1) < 1e-10:
                parts.append(vname)
            elif abs(aj + 1) < 1e-10:
                parts.append(f"−{vname}")
            else:
                parts.append(f"{aj:g}{vname}")
        lhs_str = " + ".join(parts) if parts else "0"
        lbl = f"R{i+1}:  {lhs_str} {tipos[i]} {b[i]:g}"

        if abs(a2) > 1e-10:
            y = (b[i] - a1 * x) / a2
            mk = (y >= -yl * 0.04) & (y <= yl * 1.08)
            ax.plot(x[mk], y[mk], lw=2.0, color=col,
                    label=lbl, zorder=4, solid_capstyle="round")
        else:
            if abs(a1) > 1e-10:
                ax.axvline(b[i] / a1, lw=2.0, color=col, label=lbl, zorder=4)
        legend_handles.append(mpatches.Patch(color=col, label=lbl))

    for p in (verts if len(verts) > 0 else []):
        ax.scatter(p[0], p[1], s=55, color="#1A5276",
                   zorder=8, edgecolors="#0E3460", linewidths=1.0)
        ha = "right" if p[0] > xd * 0.70 else "left"
        dx = -xl * 0.025 if ha == "right" else xl * 0.012
        dy = yl * 0.025
        ax.annotate(
            f"({p[0]:.3g}, {p[1]:.3g})",
            xy=(p[0], p[1]), xytext=(p[0] + dx, p[1] + dy),
            fontsize=7.5, ha=ha, color="#1C2833",
            bbox=dict(boxstyle="round,pad=0.3",
                      fc="#FFFFFF", ec="#C8D3E0", alpha=0.95),
            zorder=9
        )

    Z_opt = float(np.dot(c_orig, sol))
    a1, a2 = float(c_orig[0]), float(c_orig[1])
    tag = "MAX" if is_max else "MIN"
    obj_lbl = f"Z = {Z_opt:.6g}  ({tag})"

    if abs(a2) > 1e-10:
        yobj = (Z_opt - a1 * x) / a2
        ax.plot(x, yobj, color="#B22222", lw=2.5,
                linestyle="-", label=obj_lbl, zorder=5,
                solid_capstyle="round")
    else:
        ax.axvline(sol[0], color="#B22222", lw=2.5,
                   label=obj_lbl, zorder=5)
    legend_handles.append(mpatches.Patch(color="#B22222", label=obj_lbl))

    if abs(a2) > 1e-10:
        for factor in [0.3, 0.6, 1.4, 1.7]:
            Z_iso = Z_opt * factor
            y_iso = (Z_iso - a1 * x) / a2
            ax.plot(x, y_iso, color="#B22222", lw=0.6,
                    linestyle=":", alpha=0.22, zorder=3)

    ax.scatter(sol[0], sol[1], s=420, color="#B22222",
               alpha=0.12, zorder=10, edgecolors="none")
    ax.scatter(sol[0], sol[1], s=220, color="#B22222",
               alpha=0.28, zorder=11, edgecolors="none")
    ax.scatter(sol[0], sol[1], s=160, color="#B22222",
               zorder=12, marker="*", edgecolors="#7B0000", linewidths=0.8)

    ax.annotate(
        f"  Óptimo\n  X₁ = {sol[0]:.4g}\n  X₂ = {sol[1]:.4g}\n  Z  = {Z_opt:.6g}",
        xy=(sol[0], sol[1]),
        xytext=(sol[0] + xl * 0.05, sol[1] + yl * 0.07),
        fontsize=9, color="#B22222", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.45",
                  fc="#FFF5F5", ec="#B22222", alpha=0.97, lw=1.2),
        arrowprops=dict(arrowstyle="-|>", color="#B22222",
                        lw=1.5, connectionstyle="arc3,rad=0.12"),
        zorder=13
    )

    if len(verts) >= 3:
        centroid = verts.mean(axis=0)
        ax.text(centroid[0], centroid[1], "Región\nfactible",
                ha="center", va="center", fontsize=8,
                color="#1A5276", alpha=0.65,
                fontstyle="italic", zorder=7)

    ax.set_xlim(0, xl)
    ax.set_ylim(0, yl)
    ax.set_xlabel("X₁", fontsize=12, color=PAL["text2"], labelpad=10)
    ax.set_ylabel("X₂", fontsize=12, color=PAL["text2"], rotation=0, labelpad=18)
    ax.tick_params(colors=PAL["text3"], labelsize=8.5)
    for spine in ax.spines.values():
        spine.set_edgecolor(PAL["border"])

    tipo_obj = "Maximización" if is_max else "Minimización"
    ax.set_title(f"Método Gráfico — {tipo_obj}",
                 fontsize=13, fontweight="bold",
                 color=PAL["text"], pad=14)

    for axobj, lim in ((ax.xaxis, xl), (ax.yaxis, yl)):
        raw = max(lim / 8, 1e-9)
        mag = 10 ** np.floor(np.log10(raw))
        nice = round(raw / mag) * mag
        if nice <= 0:
            nice = 1.0
        axobj.set_major_locator(MultipleLocator(nice))
        axobj.set_minor_locator(AutoMinorLocator(4))

    legend_handles.insert(0, mpatches.Patch(color="#1A5276", alpha=0.35,
                                             label="Región factible"))
    leg = ax.legend(handles=legend_handles,
                    fontsize=8, loc="upper right",
                    framealpha=0.96, edgecolor=PAL["border"],
                    facecolor="#FFFFFF",
                    labelcolor=PAL["text"],
                    borderpad=0.9, labelspacing=0.6)
    for text in leg.get_texts():
        text.set_color(PAL["text2"])

    ax.figure.tight_layout()
