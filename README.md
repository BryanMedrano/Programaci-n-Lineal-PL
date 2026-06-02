# Programación Lineal 

**Equipo**: Bryan Medrano, Eyner Gómez & Luis Felipe Echeverry.

---
## Resumen

Aplicación de escritorio en Python que resuelve problemas de Programación Lineal mediante el Método Símplex (tableau, iteraciones). Proporciona:

- Resolución automática de problemas LP (maximización/minimización) con restricciones tipo ≤, ≥ y =.
- Visualización interactiva de las iteraciones (tableau) del símplex.
- Análisis de sensibilidad de variables y restricciones.
- Interfaz gráfica para introducir variables, restricciones y ver resultados y gráficas.

## Qué resuelve

Resuelve problemas de optimización lineal estándar: encontrar valores de variables que optimicen una función objetivo lineal sujeta a restricciones lineales. Es útil para ejemplos académicos y para estudiar el comportamiento del símplex (pivoteos, variables básicas, precio sombra, rangos de factibilidad).

## Características principales

- Interfaz gráfica (Tkinter) para crear y resolver problemas PL sin programar.
- Panel de entrada para coeficientes de la función objetivo y de restricciones.
- Botón para ejecutar el símplex y ver la solución óptima.
- Ventana de `Tableau` con iteraciones paso a paso.
- Ventana de `Sensibilidad` mostrando rangos permisibles y precios sombra.
- Gráfica de resultados (cuando aplica) y mensajes de estado.

## Requisitos

- Python 3.8 o superior.
- Dependencias Python (instalables vía pip):
  - numpy
  - scipy
  - matplotlib
- Tkinter (incluido con la mayoría de instalaciones de Python; en Windows suele venir por defecto).

## Instalación

Se recomienda usar un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install numpy scipy matplotlib
```

## Ejecución

Desde la carpeta del proyecto, ejecutar el lanzador principal:

```powershell
python main.py
```

También puedes ejecutar el paquete directamente:

```powershell
python -m programacion_lineal.main
```

## Uso rápido

1. Abrir la aplicación.
2. Seleccionar número de variables y restricciones.
3. Introducir coeficientes de la función objetivo y de cada restricción (RHS).
4. Elegir si es `Maximizar` o `Minimizar` según el problema.
5. Pulsar `Resolver` para ejecutar el método Símplex.
6. Ver la solución óptima en el panel superior y, opcionalmente, abrir:
  - `Tableau` para revisar iteraciones.
  - `Sensibilidad` para rangos y precios sombra.

## Solución de problemas

- Si falta `tkinter`, instala la distribución de Python que incluye Tcl/Tk o activa la opción en el instalador.
- Si aparece un error de paquetes, instala dependencias con `pip install numpy scipy matplotlib`.
- En Windows PowerShell, para ejecutar un script con una ruta entre comillas y argumentos, usar el operador `&` si es necesario.

## Estructura 

- `programacion_lineal/main.py` — punto de entrada del paquete.
- `programacion_lineal/core/simplex_engine.py` — motor Símplex y utilidades básicas.
- `programacion_lineal/core/sensitivity.py` — análisis de sensibilidad.
- `programacion_lineal/core/helpers.py` — utilidades generales.
- `programacion_lineal/graphics/graph_plotter.py` — método gráfico.
- `programacion_lineal/ui/app.py` — ventana principal y eventos.
- `programacion_lineal/ui/tableau_window.py` — ventana de iteraciones.
- `programacion_lineal/ui/sensitivity_window.py` — ventana de sensibilidad.
- `programacion_lineal/ui/widgets.py` — widgets reutilizables.
- `programacion_lineal/config/palette.py` — paleta, constantes y formato.
- `main.py` — lanzador raíz para compatibilidad.
- `requirements.txt` — dependencias mínimas.
