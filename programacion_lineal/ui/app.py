"""Ventana principal y flujo de eventos de la aplicación."""

from __future__ import annotations

import warnings

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk, font as tkfont

from ..config.palette import PAL, REST_COLORS, fmt
from ..core.simplex_engine import simplex_engine
from ..core.sensitivity import sensitivity
from ..graphics.graph_plotter import draw_graph
from .widgets import make_entry, make_label, make_btn, make_combobox
from .tableau_window import TableauWindow
from .sensitivity_window import SensWindow

warnings.filterwarnings("ignore")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Programación Lineal — Método Símplex")
        self.configure(bg=PAL["bg"])
        self.geometry("1280x820")
        self.minsize(900, 600)

        self._result = None
        self._entries = {}
        self._build_ui()
        self._load_example()

    # ── Layout principal ─────────────────────────────────────────────────────

    def _build_ui(self):
        self.left = tk.Frame(self, bg=PAL["bg"], width=360)
        self.left.pack(side="left", fill="y", padx=(14, 0), pady=14)
        self.left.pack_propagate(False)
        self._build_left(self.left)

        sep = tk.Frame(self, bg=PAL["border"], width=1)
        sep.pack(side="left", fill="y", padx=10)

        right = tk.Frame(self, bg=PAL["bg"])
        right.pack(side="left", fill="both", expand=True, pady=14, padx=(0, 14))
        self._build_right(right)

    def _build_left(self, parent):
        header = tk.Frame(parent, bg=PAL["accent"], pady=10, padx=12)
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="📐  Programación Lineal",
                 bg=PAL["accent"], fg="#FFFFFF",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(header, text="Método Símplex Generalizado · Análisis de Sensibilidad",
                 bg=PAL["accent"], fg="#BDD7EE",
                 font=("Segoe UI", 8)).pack(anchor="w")

        self._hr(parent)

        sect = self._section(parent, "Configuración")
        grid = tk.Frame(sect, bg=PAL["bg"])
        grid.pack(fill="x")

        make_label(grid, "Variables:").grid(row=0, column=0, sticky="w", pady=3)
        self.cb_vars = make_combobox(grid, ["2", "3", "4", "5"], 6)
        self.cb_vars.grid(row=0, column=1, sticky="w", padx=(6, 0))
        self.cb_vars.bind("<<ComboboxSelected>>", lambda e: self._rebuild_coefs())

        make_label(grid, "Restricciones:").grid(row=1, column=0, sticky="w", pady=3)
        self.cb_rest = make_combobox(grid, ["2", "3", "4", "5", "6"], 6)
        self.cb_rest.grid(row=1, column=1, sticky="w", padx=(6, 0))
        self.cb_rest.bind("<<ComboboxSelected>>", lambda e: self._rebuild_coefs())

        make_label(grid, "Objetivo:").grid(row=2, column=0, sticky="w", pady=3)
        self.cb_obj = make_combobox(grid, ["Maximizar", "Minimizar"], 10)
        self.cb_obj.grid(row=2, column=1, sticky="w", padx=(6, 0))

        self._hr(parent)

        self._section(parent, "Función objetivo  Z =")
        obj_outer = tk.Frame(parent, bg=PAL["bg"])
        obj_outer.pack(fill="x", pady=(0, 4))
        hsb = tk.Scrollbar(obj_outer, orient="horizontal",
                           bg=PAL["border"], troughcolor=PAL["surface2"])
        hsb.pack(side="bottom", fill="x")
        self.obj_canvas = tk.Canvas(obj_outer, bg=PAL["bg"], height=42,
                                    xscrollcommand=hsb.set, highlightthickness=0)
        self.obj_canvas.pack(fill="x", expand=True)
        hsb.config(command=self.obj_canvas.xview)
        self.obj_frame = tk.Frame(self.obj_canvas, bg=PAL["bg"])
        self.obj_canvas_win = self.obj_canvas.create_window((0, 0), window=self.obj_frame, anchor="nw")
        self.obj_frame.bind("<Configure>", lambda e: self.obj_canvas.configure(
            scrollregion=self.obj_canvas.bbox("all")))

        self._hr(parent)

        self._section(parent, "Restricciones")
        rest_outer = tk.Frame(parent, bg=PAL["bg"])
        rest_outer.pack(fill="both", expand=True)
        vsb = tk.Scrollbar(rest_outer, bg=PAL["surface"])
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(rest_outer, orient="horizontal", bg=PAL["surface"])
        hsb.pack(side="bottom", fill="x")
        self.rest_canvas = tk.Canvas(rest_outer, bg=PAL["bg"],
                                     yscrollcommand=vsb.set,
                                     xscrollcommand=hsb.set,
                                     highlightthickness=0)
        self.rest_canvas.pack(fill="both", expand=True)
        vsb.config(command=self.rest_canvas.yview)
        hsb.config(command=self.rest_canvas.xview)
        self.rest_frame = tk.Frame(self.rest_canvas, bg=PAL["bg"])
        self.rest_canvas_win = self.rest_canvas.create_window((0, 0), window=self.rest_frame, anchor="nw")
        self.rest_frame.bind("<Configure>", lambda e: self.rest_canvas.configure(
            scrollregion=self.rest_canvas.bbox("all")))

        self._hr(parent)

        btn_row = tk.Frame(parent, bg=PAL["bg"])
        btn_row.pack(fill="x", pady=6)
        make_btn(btn_row, "📖 Ejemplo", self._load_example).pack(side="left", padx=(0, 6))
        make_btn(btn_row, "🗑 Limpiar", self._clear).pack(side="left", padx=(0, 6))
        make_btn(btn_row, "▶  Resolver", self._solve, accent=True).pack(side="right")

        tool_row = tk.Frame(parent, bg=PAL["bg"])
        tool_row.pack(fill="x", pady=(0, 6))
        self.btn_tableau = make_btn(tool_row, "📋 Ver Tableaux", self._open_tableau)
        self.btn_tableau.pack(side="left", padx=(0, 6))
        self.btn_tableau.config(state="disabled")
        self.btn_sens = make_btn(tool_row, "📈 Sensibilidad", self._open_sens)
        self.btn_sens.pack(side="left")
        self.btn_sens.config(state="disabled")

        self._rebuild_coefs()

    def _build_right(self, parent):
        self.res_frame = tk.Frame(parent, bg=PAL["surface"],
                                  highlightthickness=1,
                                  highlightbackground=PAL["border"])
        self.res_frame.pack(fill="x", pady=(0, 10))
        self.res_lbl = tk.Label(self.res_frame,
                                text="Ingresa los datos y presiona  ▶ Resolver",
                                bg=PAL["surface"], fg=PAL["text3"],
                                font=("Segoe UI", 13),
                                pady=12, padx=14, anchor="w", justify="left")
        self.res_lbl.pack(fill="x")

        graph_card = tk.Frame(parent, bg=PAL["surface"],
                              highlightthickness=1,
                              highlightbackground=PAL["border"])
        graph_card.pack(fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(8, 6), facecolor="#F5F7FA")
        self.ax.set_facecolor("#FFFFFF")
        self.ax.text(0.5, 0.5,
                     "El gráfico aparecerá aquí\n(disponible para 2 variables)",
                     ha="center", va="center",
                     color=PAL["text3"], fontsize=11,
                     transform=self.ax.transAxes)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for sp in self.ax.spines.values():
            sp.set_edgecolor(PAL["border"])

        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=graph_card)
        self.canvas_fig.draw()
        self.canvas_fig.get_tk_widget().pack(fill="both", expand=True)

        toolbar_frame = tk.Frame(graph_card, bg=PAL["surface2"])
        toolbar_frame.pack(fill="x")
        tb = NavigationToolbar2Tk(self.canvas_fig, toolbar_frame)
        tb.config(bg=PAL["surface2"])
        tb.update()

    def _hr(self, parent):
        tk.Frame(parent, bg=PAL["border"], height=1).pack(fill="x", pady=8)

    def _section(self, parent, title):
        f = tk.Frame(parent, bg=PAL["bg"])
        f.pack(fill="x", pady=(0, 6))
        bar_row = tk.Frame(f, bg=PAL["bg"])
        bar_row.pack(fill="x")
        tk.Frame(bar_row, bg=PAL["accent"], width=3).pack(side="left", fill="y", padx=(0, 6))
        tk.Label(bar_row, text=title, bg=PAL["bg"],
                 fg=PAL["accent"], font=("Segoe UI", 11, "bold")).pack(anchor="w", side="left")
        return f

    def _rebuild_coefs(self):
        nv = int(self.cb_vars.get())
        nr = int(self.cb_rest.get())
        try:
            target_width = 520 if nv > 3 else 360
            self.left.config(width=target_width)
            self.left.update_idletasks()
        except Exception:
            pass
        prev_c = [e.get() for e in self._entries.get("c", [])] if self._entries.get("c") else []
        prev_A = [[e.get() for e in row] for row in self._entries.get("A", [])] if self._entries.get("A") else []
        prev_tipo = [cb.get() for cb in self._entries.get("tipo", [])] if self._entries.get("tipo") else []
        prev_b = [e.get() for e in self._entries.get("b", [])] if self._entries.get("b") else []

        self._entries.clear()

        for w in self.obj_frame.winfo_children():
            w.destroy()
        row = tk.Frame(self.obj_frame, bg=PAL["bg"])
        row.pack(fill="x")
        self._entries["c"] = []
        for j in range(nv):
            if j > 0:
                tk.Label(row, text="+", bg=PAL["bg"],
                         fg=PAL["text3"], font=("Segoe UI", 11)).pack(side="left", padx=2)
            e = make_entry(row, width=5)
            e.pack(side="left", padx=2, ipady=3)
            if j < len(prev_c) and prev_c[j] != "":
                try:
                    e.insert(0, prev_c[j])
                except Exception:
                    pass
            self._entries["c"].append(e)
            tk.Label(row, text=f"X{j+1}", bg=PAL["bg"],
                     fg=PAL["text2"], font=("Segoe UI", 11)).pack(side="left")

        for w in self.rest_frame.winfo_children():
            w.destroy()
        self._entries["A"] = []
        self._entries["tipo"] = []
        self._entries["b"] = []
        for i in range(nr):
            row = tk.Frame(self.rest_frame, bg=PAL["bg"])
            row.pack(fill="x", pady=3)
            color = REST_COLORS[i % len(REST_COLORS)]
            tk.Label(row, text=f"R{i+1}", bg=PAL["bg"],
                     fg=color, font=("Segoe UI", 11, "bold"),
                     width=3).pack(side="left")
            a_row = []
            for j in range(nv):
                if j > 0:
                    tk.Label(row, text="+", bg=PAL["bg"],
                             fg=PAL["text3"], font=("Segoe UI", 11)).pack(side="left", padx=1)
                e = make_entry(row, width=5)
                e.pack(side="left", padx=1, ipady=3)
                if i < len(prev_A) and j < len(prev_A[i]) and prev_A[i][j] != "":
                    try:
                        e.insert(0, prev_A[i][j])
                    except Exception:
                        pass
                a_row.append(e)
                tk.Label(row, text=f"X{j+1}", bg=PAL["bg"],
                         fg=PAL["text2"], font=("Segoe UI", 11)).pack(side="left")
            self._entries["A"].append(a_row)

            cb = make_combobox(row, ["≤", "≥", "="], 4)
            cb.pack(side="left", padx=5)
            if i < len(prev_tipo) and prev_tipo[i] in ("≤", ">=", "="):
                try:
                    cb.set(prev_tipo[i])
                except Exception:
                    pass
            self._entries["tipo"].append(cb)

            b_e = make_entry(row, width=6)
            b_e.pack(side="left", padx=2, ipady=3)
            if i < len(prev_b) and prev_b[i] != "":
                try:
                    b_e.insert(0, prev_b[i])
                except Exception:
                    pass
            self._entries["b"].append(b_e)

    def _read_form(self):
        nv = int(self.cb_vars.get())
        nr = int(self.cb_rest.get())
        try:
            c = [float(self._entries["c"][j].get()) for j in range(nv)]
        except ValueError:
            messagebox.showerror("Error", "Coeficientes de Z inválidos.")
            return None

        A, b, tipos = [], [], []
        tipo_map = {"≤": "<=", "≥": ">=", "=": "="}
        for i in range(nr):
            try:
                row = [float(self._entries["A"][i][j].get()) for j in range(nv)]
            except ValueError:
                messagebox.showerror("Error", f"Coeficientes de R{i+1} inválidos.")
                return None
            try:
                bv = float(self._entries["b"][i].get())
            except ValueError:
                messagebox.showerror("Error", f"RHS de R{i+1} inválido.")
                return None
            A.append(row)
            b.append(bv)
            tipos.append(tipo_map[self._entries["tipo"][i].get()])
        return nv, nr, c, A, b, tipos

    def _solve(self):
        data = self._read_form()
        if data is None:
            return
        nv, nr, c_orig, A_list, b_list, tipos = data
        is_max = self.cb_obj.get() == "Maximizar"

        A = np.array(A_list, float)
        b = np.array(b_list, float)
        c_int = c_orig[:] if is_max else [-v for v in c_orig]

        for i in range(nr):
            if b[i] < 0:
                A[i] *= -1
                b[i] *= -1
                if tipos[i] == "<=":
                    tipos[i] = ">="
                elif tipos[i] == ">=":
                    tipos[i] = "<="

        sol, T, col_names, vb, history, status = simplex_engine(
            A.copy(), b.copy(), c_int[:], tipos[:])

        self._result = dict(sol=sol, T=T, col_names=col_names, vb=vb,
                            history=history, A=A, b=b, tipos=tipos,
                            c_orig=np.array(c_orig), c_int=np.array(c_int),
                            is_max=is_max, nv=nv)

        if status == "infeasible":
            self.res_lbl.config(
                text="✘  El problema es INFACTIBLE — no existe ninguna solución.",
                fg=PAL["danger"])
            self.btn_tableau.config(state="normal")
            self.btn_sens.config(state="disabled")
            self._clear_graph()
            return
        if status == "unbounded":
            self.res_lbl.config(
                text="⚠  El problema NO ESTÁ ACOTADO.",
                fg=PAL["warning"])
            self.btn_tableau.config(state="normal")
            self.btn_sens.config(state="disabled")
            self._clear_graph()
            return

        Z_disp = T[0, -1] if is_max else -T[0, -1]
        vars_str = "   ".join(f"X{j+1} = {fmt(sol[j])}" for j in range(nv))
        n_iters = len(history) - 1
        tag = "MAX" if is_max else "MIN"
        txt = (f"✔  Solución óptima encontrada  ({n_iters} iteración(es))\n\n"
               f"   {vars_str}\n\n"
               f"   Z  ({tag})  =  {fmt(Z_disp)}")
        self.res_lbl.config(text=txt, fg=PAL["success"])

        self.btn_tableau.config(state="normal")
        self.btn_sens.config(state="normal")

        if nv == 2:
            self.ax.cla()
            draw_graph(self.ax, A.tolist(), b.tolist(), sol,
                       c_orig, tipos, is_max)
            self.canvas_fig.draw()
        else:
            self._clear_graph(msg="Gráfico disponible solo para 2 variables.")

    def _open_tableau(self):
        if self._result and self._result.get("history"):
            TableauWindow(self, self._result["history"])

    def _open_sens(self):
        if not self._result or self._result["sol"] is None:
            return
        r = self._result
        var_rows, rest_rows, _ = sensitivity(
            r["T"], r["vb"], r["c_int"].tolist(),
            r["c_orig"].tolist(), r["A"].tolist(),
            r["b"].tolist(), r["tipos"], r["is_max"])
        SensWindow(self, var_rows, rest_rows)

    def _clear_graph(self, msg="El gráfico aparecerá aquí\n(disponible para 2 variables)"):
        self.ax.cla()
        self.ax.set_facecolor("#FFFFFF")
        self.ax.text(0.5, 0.5, msg, ha="center", va="center",
                     color=PAL["text3"], fontsize=10,
                     transform=self.ax.transAxes)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for sp in self.ax.spines.values():
            sp.set_edgecolor(PAL["border"])
        self.canvas_fig.draw()

    def _clear(self):
        for e in self._entries.get("c", []):
            e.delete(0, "end")
        for row in self._entries.get("A", []):
            for e in row:
                e.delete(0, "end")
        for e in self._entries.get("b", []):
            e.delete(0, "end")
        self._result = None
        self.btn_tableau.config(state="disabled")
        self.btn_sens.config(state="disabled")
        self.res_lbl.config(text="Ingresa los datos y presiona  ▶ Resolver",
                            fg=PAL["text3"])
        self._clear_graph()

    def _load_example(self):
        self.cb_vars.set("2")
        self.cb_rest.set("3")
        self.cb_obj.set("Maximizar")
        self._rebuild_coefs()

        for v, e in zip([5, 4], self._entries["c"]):
            e.delete(0, "end")
            e.insert(0, str(v))

        data = [
            ([6, 4], "≤", 24),
            ([1, 2], "≤", 6),
            ([-1, 1], "≤", 1),
        ]
        for i, (row, tipo, bv) in enumerate(data):
            for j, v in enumerate(row):
                self._entries["A"][i][j].delete(0, "end")
                self._entries["A"][i][j].insert(0, str(v))
            self._entries["tipo"][i].set(tipo)
            self._entries["b"][i].delete(0, "end")
            self._entries["b"][i].insert(0, str(bv))
