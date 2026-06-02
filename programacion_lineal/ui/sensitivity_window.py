"""Ventana de análisis de sensibilidad."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..config.palette import PAL, fmt
from .widgets import make_btn


class SensWindow(tk.Toplevel):
    """Ventana con pestañas para sensibilidad de variables y restricciones."""

    def __init__(self, master, var_rows, rest_rows):
        super().__init__(master)
        self.title("Análisis de Sensibilidad")
        self.configure(bg=PAL["bg"])
        self.geometry("1020x400")
        self._build(var_rows, rest_rows)

    def _on_mousewheel(self, event):
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self._mousewheel_target.yview_scroll(delta, "units")

    def _on_shift_mousewheel(self, event):
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 if event.delta > 0 else 1
        self._mousewheel_target.xview_scroll(delta, "units")

    def _build(self, var_rows, rest_rows):
        header = tk.Frame(self, bg=PAL["accent"], pady=8)
        header.pack(fill="x")
        tk.Label(header, text="  📈  Análisis de Sensibilidad", bg=PAL["accent"],
                 fg="#FFFFFF", font=("Segoe UI", 14, "bold")).pack(side="left", padx=12)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.configure("TNotebook", background=PAL["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=PAL["surface2"], foreground=PAL["text2"],
                        padding=(14, 6), font=("Segoe UI", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", PAL["accent"])],
                  foreground=[("selected", "#FFFFFF")])

        tab1 = tk.Frame(nb, bg=PAL["bg"])
        nb.add(tab1, text="  Celdas Variables  ")
        tab2 = tk.Frame(nb, bg=PAL["bg"])
        nb.add(tab2, text="  Restricciones  ")

        VAR_HDRS = ["Variable", "Valor Final", "Costo Red.",
                    "Coef. Obj.", "Aum. Perm.", "Dis. Perm.", "Coef. Mín", "Coef. Máx"]
        REST_HDRS = ["Restricción", "Val. Final", "Precio Sombra",
                     "RHS", "Aum. Perm.", "Dis. Perm.", "RHS Mín", "RHS Máx"]
        NOTE = ("Los valores 1E+30 / -1E+30 indican rangos sin límite "
                "(equivalen al 1E+30 / −1E+30 de Excel Solver).")

        self._make_table(tab1, VAR_HDRS, var_rows)
        tk.Label(tab1, text=NOTE, bg=PAL["bg"], fg=PAL["text3"],
                 font=("Segoe UI", 9, "italic")).pack(anchor="w", padx=12, pady=(4, 0))
        self._make_table(tab2, REST_HDRS, rest_rows)
        tk.Label(tab2, text=NOTE, bg=PAL["bg"], fg=PAL["text3"],
                 font=("Segoe UI", 9, "italic")).pack(anchor="w", padx=12, pady=(4, 0))

    def _make_table(self, parent, headers, rows):
        frame = tk.Frame(parent, bg=PAL["bg"])
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        vsb = tk.Scrollbar(frame, bg=PAL["surface"])
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(frame, orient="horizontal", bg=PAL["surface"])
        hsb.pack(side="bottom", fill="x")
        canvas = tk.Canvas(frame, bg=PAL["surface"],
                           yscrollcommand=vsb.set,
                           xscrollcommand=hsb.set,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        vsb.config(command=canvas.yview)
        hsb.config(command=canvas.xview)
        inner = tk.Frame(canvas, bg=PAL["surface"])
        canvas_win = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        self._mousewheel_target = canvas
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)
        self.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.bind_all("<Shift-Button-4>", self._on_shift_mousewheel)
        self.bind_all("<Shift-Button-5>", self._on_shift_mousewheel)

        col_w = [14] + [13] * (len(headers) - 1)
        for c in range(len(headers)):
            inner.columnconfigure(c, weight=1, minsize=94 if c == 0 else 102)
        for c, h in enumerate(headers):
            tk.Label(inner, text=h, bg=PAL["accent"], fg="#FFFFFF",
                     font=("Segoe UI", 12, "bold"), width=col_w[c],
                     padx=6, pady=6, anchor="center"
                     ).grid(row=0, column=c, sticky="nsew", padx=1, pady=1)

        is_inf = lambda v: v in ("1E+30", "-1E+30")

        for r, row in enumerate(rows):
            bg_row = PAL["row_even"] if r % 2 == 0 else PAL["row_odd"]
            for c, val in enumerate(row):
                text = fmt(val) if isinstance(val, float) else str(val)
                fg_c = PAL["text3"] if is_inf(text) else PAL["text"]
                if c == 0:
                    fg_c = PAL["accent"]
                tk.Label(inner, text=text, bg=bg_row, fg=fg_c,
                         font=("Consolas", 13), width=col_w[c],
                         padx=6, pady=5, anchor="center"
                         ).grid(row=r + 1, column=c, sticky="nsew", padx=1, pady=1)
