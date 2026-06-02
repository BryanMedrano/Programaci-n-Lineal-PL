"""Widgets reutilizables de la interfaz."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..config.palette import PAL


def make_entry(parent, width=8, **kw):
    """Crea una entrada con el estilo visual actual."""
    return tk.Entry(parent, width=width,
                    bg="#FFFFFF", fg=PAL["text"],
                    insertbackground=PAL["accent"],
                    relief="flat", bd=0,
                    font=("Segoe UI", 11),
                    highlightthickness=1,
                    highlightbackground=PAL["border"],
                    highlightcolor=PAL["accent"],
                    **kw)


def make_label(parent, text, size=11, color=None, bold=False, **kw):
    """Crea una etiqueta con tipografía consistente."""
    color = color or PAL["text2"]
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text,
                    bg=PAL["bg"], fg=color,
                    font=("Segoe UI", size, weight), **kw)


def make_btn(parent, text, cmd, accent=False, danger=False, **kw):
    """Crea un botón con el estilo de la aplicación."""
    col = PAL["accent"] if accent else (PAL["danger"] if danger else PAL["surface2"])
    fg = "#FFFFFF" if accent or danger else PAL["text"]
    hover = PAL["highlight"] if accent else (PAL["danger"] if danger else PAL["border"])
    b = tk.Button(parent, text=text, command=cmd,
                  bg=col, fg=fg, activebackground=hover,
                  activeforeground=fg, relief="flat", bd=0,
                  font=("Segoe UI", 10, "bold"),
                  cursor="hand2", padx=12, pady=7, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=col))
    return b


def make_combobox(parent, values, width=10):
    """Crea un combobox readonly con el tema visual actual."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Edu.TCombobox",
                    fieldbackground="#FFFFFF",
                    background="#FFFFFF",
                    foreground=PAL["text"],
                    selectbackground=PAL["accent"],
                    selectforeground="#FFFFFF",
                    arrowcolor=PAL["accent"],
                    borderwidth=1,
                    relief="flat")
    cb = ttk.Combobox(parent, values=values, width=width,
                      style="Edu.TCombobox", state="readonly",
                      font=("Segoe UI", 11))
    cb.set(values[0])
    return cb
