"""Punto de entrada del paquete `programacion_lineal`."""

from .ui.app import App


def main():
    """Lanza la aplicación gráfica principal."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
