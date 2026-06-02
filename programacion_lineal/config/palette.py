"""Constantes visuales y formato numérico de la aplicación."""

PAL = {
    "bg":        "#F5F7FA",
    "surface":   "#FFFFFF",
    "surface2":  "#EEF1F6",
    "border":    "#C8D3E0",
    "accent":    "#1A5276",
    "accent2":   "#1A7A4A",
    "success":   "#1E7E34",
    "warning":   "#7D5A00",
    "danger":    "#B22222",
    "text":      "#1C2833",
    "text2":     "#34495E",
    "text3":     "#7F8C8D",
    "highlight": "#2874A6",
    "header_bg": "#1A5276",
    "header_fg": "#FFFFFF",
    "tab_sel":   "#2874A6",
    "row_even":  "#F0F4F8",
    "row_odd":   "#FFFFFF",
}

REST_COLORS = [
    "#1A5276", "#1A7A4A", "#7D5A00", "#B22222",
    "#6C3483", "#0E6655", "#784212", "#1B4F72",
]

INF_STR = "1E+30"
NEG_INF_STR = "-1E+30"


def fmt(v: float) -> str:
    """Formatea números como en la versión actual de la interfaz."""
    if v is None:
        return "—"
    if v == float("inf") or v >= 9e28:
        return INF_STR
    if v == float("-inf") or v <= -9e28:
        return NEG_INF_STR
    if abs(v) < 1e-9:
        return "0"
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.6f}".rstrip("0").rstrip(".")
