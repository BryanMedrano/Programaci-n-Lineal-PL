"""Ventana interactiva para navegar las iteraciones del tableau."""

from __future__ import annotations

import tkinter as tk

from ..config.palette import PAL, fmt
from .widgets import make_btn


class TableauWindow(tk.Toplevel):
    """Ventana de iteraciones del método símplex."""

    def __init__(self, master, history):
        super().__init__(master)
        self.title("Iteraciones del Símplex")
        self.configure(bg=PAL["bg"])
        self.geometry("980x360")
        self.history = history
        self.cur_iter = 0
        self._build()
        self._render()

    def _build(self):
        top = tk.Frame(self, bg=PAL["accent"], pady=8)
        top.pack(fill="x", padx=0, pady=(0, 10))
        tk.Label(top, text="  📊  Tableau del Símplex", bg=PAL["accent"],
                 fg="#FFFFFF", font=("Segoe UI", 13, "bold")).pack(side="left", padx=12)
        ctrl = tk.Frame(self, bg=PAL["bg"])
        ctrl.pack(fill="x", padx=16)
        self.btn_prev = make_btn(ctrl, "◀  Anterior", self._prev)
        self.btn_prev.pack(side="left", padx=(0, 6))
        self.iter_lbl = tk.Label(ctrl, text="", bg=PAL["bg"],
                                 fg=PAL["accent"], font=("Segoe UI", 11, "bold"))
        self.iter_lbl.pack(side="left", padx=8)
        self.btn_next = make_btn(ctrl, "Siguiente  ▶", self._next)
        self.btn_next.pack(side="left", padx=6)
        self.status_lbl = tk.Label(ctrl, text="", bg=PAL["bg"],
                                   fg=PAL["success"], font=("Segoe UI", 10, "italic"))
        self.status_lbl.pack(side="left", padx=14)

        frame = tk.Frame(self, bg=PAL["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=10)
        vsb = tk.Scrollbar(frame, bg=PAL["border"], troughcolor=PAL["surface2"])
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(frame, orient="horizontal",
                           bg=PAL["border"], troughcolor=PAL["surface2"])
        hsb.pack(side="bottom", fill="x")
        self.canvas = tk.Canvas(frame, bg=PAL["surface"],
                                yscrollcommand=vsb.set,
                                xscrollcommand=hsb.set,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        vsb.config(command=self.canvas.yview)
        hsb.config(command=self.canvas.xview)
        self.inner = tk.Frame(self.canvas, bg=PAL["surface"])
        self.canvas_win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)
        self.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.bind_all("<Shift-Button-4>", self._on_shift_mousewheel)
        self.bind_all("<Shift-Button-5>", self._on_shift_mousewheel)

    def _on_mousewheel(self, event):
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(delta, "units")

    def _on_shift_mousewheel(self, event):
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self.canvas.xview_scroll(delta, "units")

    def _render(self):
        for w in self.inner.winfo_children():
            w.destroy()
        snap = self.history[self.cur_iter]
        T, vb = snap["T"], snap["vb"]
        col_names, piv_col = snap["col_names"], snap.get("piv_col")

        status = snap.get("status", "")
        enter = snap.get("enter", "")
        leave = snap.get("leave", "")

        if status == "optimal":
            self.status_lbl.config(text="✔  Solución óptima", fg=PAL["success"])
        elif enter:
            self.status_lbl.config(
                text=f"Entra: {enter}   →   Sale: {leave}", fg=PAL["warning"])
        else:
            self.status_lbl.config(text="")

        hdrs = ["Ec.", "VB", "Z"] + col_names + ["LD"]
        for c in range(len(hdrs)):
            self.inner.columnconfigure(c, weight=1, minsize=88 if c < 2 else 92)

        def cell(row, col, text, bg=None, fg=None, w=10):
            bg = bg or (PAL["row_even"] if row % 2 == 0 else PAL["row_odd"])
            fg = fg or PAL["text"]
            tk.Label(self.inner, text=text, bg=bg, fg=fg,
                     font=("Consolas", 13), width=w,
                     relief="flat", padx=4, pady=4,
                     anchor="center").grid(row=row, column=col,
                                           sticky="nsew", padx=1, pady=1)

        for c, h in enumerate(hdrs):
            tk.Label(self.inner, text=h, bg=PAL["accent"],
                     fg="#FFFFFF", font=("Segoe UI", 12, "bold"),
                     width=10, padx=4, pady=5, anchor="center"
                     ).grid(row=0, column=c, sticky="nsew", padx=1, pady=1)

        for i, row in enumerate(T):
            r = i + 1
            label = "Z" if i == 0 else vb[i - 1]
            cell(r, 0, f"({i})", fg=PAL["text3"])
            cell(r, 1, label, fg=PAL["accent"] if i == 0 else PAL["accent2"])
            for j, v in enumerate(row):
                col_idx = j + 2
                is_pivot = (piv_col is not None and j == piv_col - 1 and i > 0)
                is_z_pivot = (piv_col is not None and j == piv_col - 1 and i == 0)
                bg_c = ("#D6EAF8") if is_pivot else None
                fg_c = PAL["accent"] if is_pivot else (PAL["text3"] if is_z_pivot else None)
                val_str = f"[{fmt(v)}]" if is_pivot else fmt(v)
                cell(r, col_idx, val_str, bg=bg_c, fg=fg_c)

        n_iters = len(self.history)
        self.iter_lbl.config(text=f"Iteración  {self.cur_iter}  /  {n_iters - 1}")
        self.btn_prev.config(state="disabled" if self.cur_iter == 0 else "normal")
        self.btn_next.config(state="disabled" if self.cur_iter == n_iters - 1 else "normal")

    def _prev(self):
        if self.cur_iter > 0:
            self.cur_iter -= 1
            self._render()

    def _next(self):
        if self.cur_iter < len(self.history) - 1:
            self.cur_iter += 1
            self._render()
