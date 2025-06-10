import io
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QScrollArea, QLabel, QSplitter, 
                            QLineEdit, QFrame, QGridLayout)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from sympy import sympify, latex, lambdify, Eq, solve
from sympy.abc import x, y, z
import numpy as np

def set_latex_label(label, latex_code):
    """Renderiza código LaTeX como imagen y lo muestra en un QLabel."""
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex_code}$", fontsize=16)
    buf = io.BytesIO()
    plt.axis('off')
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.2, dpi=150, transparent=True)
    plt.close(fig)
    buf.seek(0)
    pixmap = QPixmap()
    pixmap.loadFromData(buf.getvalue())
    label.setPixmap(pixmap)

class EntradaFuncionWidget(QWidget):
    def __init__(self, nombre, parent=None):
        super().__init__(parent)
        self.nombre = nombre
        self.parent = parent
        self.visible = True  # Estado de visibilidad de la gráfica
        self.init_ui()
        
    def init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Botón mostrar/ocultar
        self.btn_visible = QPushButton("👁️")
        self.btn_visible.setCheckable(True)
        self.btn_visible.setChecked(True)
        self.btn_visible.setFixedWidth(32)
        self.btn_visible.clicked.connect(self.toggle_visible)
        self.layout.addWidget(self.btn_visible)

        # Campo de entrada
        self.entrada = QLineEdit()
        self.entrada.setPlaceholderText(f"{self.nombre}(x) = ")
        self.entrada.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.entrada.textChanged.connect(self.actualizar_funcion)
        self.layout.addWidget(self.entrada)

        self.setLayout(self.layout)
    
    def toggle_visible(self):
        self.visible = self.btn_visible.isChecked()
        if self.parent:
            self.parent.actualizar_grafico()
    
    def actualizar_funcion(self):
        if self.parent:
            self.parent.actualizar_grafico()

class ZoomableFigureCanvas(FigureCanvas):
    def __init__(self, fig, parent=None):
        super().__init__(fig)
        self.setParent(parent)
        self._zoom = 1.0
        self._base_xlim = None
        self._base_ylim = None
        self._panning = False
        self._pan_start = None
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus()

    def wheelEvent(self, event):
        if not self.figure.axes:
            return
        ax = self.figure.axes[0]
        if self._base_xlim is None or self._base_ylim is None:
            self._base_xlim = ax.get_xlim()
            self._base_ylim = ax.get_ylim()
        angle = event.angleDelta().y()
        factor = 0.9 if angle > 0 else 1.1
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        xmid = (xlim[0] + xlim[1]) / 2
        ymid = (ylim[0] + ylim[1]) / 2
        xlen = (xlim[1] - xlim[0]) * factor / 2
        ylen = (ylim[1] - ylim[0]) * factor / 2
        ax.set_xlim(xmid - xlen, xmid + xlen)
        ax.set_ylim(ymid - ylen, ymid + ylen)
        self.draw()
        if hasattr(self.parent(), "actualizar_grafico"):
            self.parent().actualizar_grafico()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._panning = True
            self._pan_start = event.pos()

    def mouseMoveEvent(self, event):
        if self._panning and self._pan_start is not None:
            dx = event.x() - self._pan_start.x()
            dy = event.y() - self._pan_start.y()
            ax = self.figure.axes[0]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            width = self.width()
            height = self.height()
            dx_data = -dx * (xlim[1] - xlim[0]) / width
            dy_data = dy * (ylim[1] - ylim[0]) / height
            ax.set_xlim(xlim[0] + dx_data, xlim[1] + dx_data)
            ax.set_ylim(ylim[0] + dy_data, ylim[1] + dy_data)
            self._pan_start = event.pos()
            self.draw()
            if hasattr(self.parent(), "actualizar_grafico"):
                self.parent().actualizar_grafico()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._panning = False
            self._pan_start = None

class GeoGebraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Integrales estilo GeoGebra")
        self.setGeometry(100, 100, 1200, 750)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
        self.funciones = {}
        self.entradas = []
        self.nombre_actual = ord('f')
        
        self.init_ui()
        
    def init_ui(self):
        # Configuración principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Cambia a QHBoxLayout

        # Splitter horizontal para expandir/colapsar entradas y gráfico
        splitter_horizontal = QSplitter(Qt.Horizontal)

        # Panel izquierdo (controles)
        panel_izquierdo = QWidget()
        panel_izquierdo.setMaximumWidth(400)
        left_layout = QVBoxLayout(panel_izquierdo)

        # Título
        titulo = QLabel("Calculadora de Integrales")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        titulo.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(titulo)

        # Área de funciones
        funciones_label = QLabel("Funciones ingresadas:")
        funciones_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(funciones_label)

        # Scroll area para entradas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        left_layout.addWidget(self.scroll_area)

        # Botón nueva función
        self.btn_nueva_funcion = QPushButton("➕ Nueva función")
        self.btn_nueva_funcion.clicked.connect(self.agregar_entrada)
        left_layout.addWidget(self.btn_nueva_funcion)

        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        left_layout.addWidget(separador)

        # Límites de integración (ahora antes del botón calcular)
        limites_layout = QHBoxLayout()
        self.limite_inf = QLineEdit("-1")
        self.limite_inf.setFixedWidth(60)
        self.limite_inf.setPlaceholderText("Límite inf.")
        self.limite_sup = QLineEdit("1")
        self.limite_sup.setFixedWidth(60)
        self.limite_sup.setPlaceholderText("Límite sup.")
        limites_layout.addWidget(QLabel("Límites integración:"))
        limites_layout.addWidget(self.limite_inf)
        limites_layout.addWidget(self.limite_sup)
        left_layout.addLayout(limites_layout)

        # Botón calcular
        self.btn_calcular = QPushButton("Calcular ")
        self.btn_calcular.clicked.connect(self.calcular_area)
        left_layout.addWidget(self.btn_calcular)

        # Resultado
        self.resultado = QLabel("Resultado: -")
        self.resultado.setStyleSheet("font-size: 16px; color: #d35400;")
        left_layout.addWidget(self.resultado)

        # Botón teclado
        self.btn_teclado = QPushButton("🧮 Mostrar Teclado")
        self.btn_teclado.setCheckable(True)
        self.btn_teclado.setChecked(True)
        self.btn_teclado.clicked.connect(self.toggle_teclado)
        left_layout.addWidget(self.btn_teclado)

        # Teclado virtual
        self.teclado_widget = QWidget()
        self.teclado_layout = QHBoxLayout(self.teclado_widget)
        self.init_teclado()
        left_layout.addWidget(self.teclado_widget)

        # Panel izquierdo terminado
        panel_izquierdo.setLayout(left_layout)

        # Gráfico
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = ZoomableFigureCanvas(self.fig)
        self.configurar_grafico()

        # Añade ambos al splitter horizontal
        splitter_horizontal.addWidget(panel_izquierdo)
        splitter_horizontal.addWidget(self.canvas)
        splitter_horizontal.setSizes([350, 850])  # Ajusta el tamaño inicial

        main_layout.addWidget(splitter_horizontal)

        # Agregar primera entrada
        self.agregar_entrada()
        
    def init_teclado(self):
        # Teclado numérico básico
        teclas = [
            '7', '8', '9', '/', '^',
            '4', '5', '6', '*', '(',
            '1', '2', '3', '-', ')',
            '0', '.', '=', '+', 'x'
        ]
        
        grid = QGridLayout()
        for i, tecla in enumerate(teclas):
            btn = QPushButton(tecla)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(self.tecla_presionada)
            grid.addWidget(btn, i//5, i%5)
        
        self.teclado_layout.addLayout(grid)
        
    def tecla_presionada(self):
        sender = self.sender()
        if self.entradas:
            entrada_actual = self.entradas[-1].entrada
            entrada_actual.insert(sender.text())
        
    def toggle_teclado(self):
        visible = self.btn_teclado.isChecked()
        self.teclado_widget.setVisible(visible)
        self.btn_teclado.setText("🧮 Ocultar Teclado" if visible else "🧮 Mostrar Teclado")
        
    def agregar_entrada(self):
        nombre = chr(self.nombre_actual)
        self.nombre_actual += 1

        entrada = EntradaFuncionWidget(nombre, self)
        self.entradas.append(entrada)
        self.scroll_layout.addWidget(entrada)

    def configurar_grafico(self):
        """Configura los elementos básicos del gráfico"""
        self.ax.clear()
        # Ejes centrales
        self.ax.axhline(0, color='black', linewidth=0.5)
        self.ax.axvline(0, color='black', linewidth=0.5)
        # Cuadrícula
        self.ax.grid(True, linestyle='--', alpha=0.5)
        # Límites de los ejes
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        # Etiquetas
        self.ax.set_xlabel('x', fontsize=10)
        self.ax.set_ylabel('y', fontsize=10)
        # Título
        self.ax.set_title('Gráfico de Funciones', fontsize=12)
        # Mejorar el espaciado
        self.fig.tight_layout()

    def actualizar_grafico(self):
        self.configurar_grafico()
        colores = plt.cm.tab10.colors
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        for i, entrada in enumerate(self.entradas):
            color = colores[i % len(colores)]
            if entrada.visible:
                entrada.btn_visible.setStyleSheet(
                    f"background-color: rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}); color: white; border-radius: 5px;"
                )
            else:
                entrada.btn_visible.setStyleSheet(
                    "background-color: #ccc; color: #888; border-radius: 5px;"
                )
            if not entrada.visible:
                continue
            texto = entrada.entrada.text().replace(' ', '')
            if not texto:
                continue
            try:
                x_latex = 0
                y_latex = 1.2 * (i + 1)
                if texto.startswith('y='):
                    expr = sympify(texto[2:])
                    f = lambdify(x, expr, 'numpy')
                    x_vals = np.linspace(xlim[0], xlim[1], 400)
                    y_vals = f(x_vals)
                    self.ax.plot(x_vals, y_vals, color=color, linewidth=2)
                    self.ax.annotate(
                        f"${latex(Eq(y, expr))}$",
                        xy=(x_latex, y_latex),
                        xytext=(10, 0),
                        textcoords='offset points',
                        fontsize=14,
                        color=color,
                        va='bottom',
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=1, alpha=0.7)
                    )
                elif texto.startswith('x='):
                    expr = sympify(texto[2:])
                    f = lambdify(y, expr, 'numpy')
                    y_vals = np.linspace(ylim[0], ylim[1], 400)
                    x_vals = f(y_vals)
                    self.ax.plot(x_vals, y_vals, color=color, linewidth=2)
                    self.ax.annotate(
                        f"${latex(Eq(x, expr))}$",
                        xy=(x_latex, y_latex),
                        xytext=(10, 0),
                        textcoords='offset points',
                        fontsize=14,
                        color=color,
                        va='bottom',
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=1, alpha=0.7)
                    )
                elif '=' in texto:
                    izquierda, derecha = texto.split('=')
                    eq = Eq(sympify(izquierda), sympify(derecha))
                    try:
                        solucion = solve(eq, y)
                        if solucion:
                            expr = solucion[0]
                            f = lambdify(x, expr, 'numpy')
                            x_vals = np.linspace(xlim[0], xlim[1], 400)
                            y_vals = f(x_vals)
                            self.ax.plot(x_vals, y_vals, color=color, linewidth=2)
                            self.ax.annotate(
                                f"${latex(Eq(y, expr))}$",
                                xy=(x_latex, y_latex),
                                xytext=(10, 0),
                                textcoords='offset points',
                                fontsize=14,
                                color=color,
                                va='bottom',
                                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=1, alpha=0.7)
                            )
                            continue
                    except Exception:
                        pass
                    try:
                        solucion = solve(eq, x)
                        if solucion:
                            expr = solucion[0]
                            f = lambdify(y, expr, 'numpy')
                            y_vals = np.linspace(ylim[0], ylim[1], 400)
                            x_vals = f(y_vals)
                            self.ax.plot(x_vals, y_vals, color=color, linewidth=2)
                            self.ax.annotate(
                                f"${latex(Eq(x, expr))}$",
                                xy=(x_latex, y_latex),
                                xytext=(10, 0),
                                textcoords='offset points',
                                fontsize=14,
                                color=color,
                                va='bottom',
                                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=1, alpha=0.7)
                            )
                            continue
                    except Exception:
                        pass
                    continue
                else:
                    expr = sympify(texto)
                    f = lambdify(x, expr, 'numpy')
                    x_vals = np.linspace(xlim[0], xlim[1], 400)
                    y_vals = f(x_vals)
                    self.ax.plot(x_vals, y_vals, color=color, linewidth=2)
                    self.ax.annotate(
                        f"${latex(Eq(y, expr))}$",
                        xy=(x_latex, y_latex),
                        xytext=(10, 0),
                        textcoords='offset points',
                        fontsize=14,
                        color=color,
                        va='bottom',
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=1, alpha=0.7)
                    )
            except Exception as e:
                print(f"Error graficando {entrada.nombre}: {str(e)}")
                continue
        self.canvas.draw()

    def calcular_area(self):
        if len(self.entradas) < 1:
            self.resultado.setText("Ingresa al menos una función.")
            return

        try:
            expr1 = sympify(self.entradas[0].entrada.text())
            f1 = lambdify(x, expr1, 'numpy')

            # Toma los límites de los campos de entrada
            try:
                a = float(self.limite_inf.text())
                b = float(self.limite_sup.text())
            except Exception:
                self.resultado.setText("Límites inválidos.")
                return

            if a >= b:
                self.resultado.setText("El límite inferior debe ser menor que el superior.")
                return

            # Método de Simpson para integración numérica
            def simpson_integration(f, a, b, n=1000):
                if n % 2 != 0:
                    n += 1
                h = (b - a) / n
                x_vals = np.linspace(a, b, n+1)
                y_vals = f(x_vals)
                integral = h/3 * np.sum(y_vals[0:-1:2] + 4*y_vals[1::2] + y_vals[2::2])
                return integral

            if len(self.entradas) == 1:
                # Área bajo la curva respecto al eje x
                area = simpson_integration(f1, a, b)
                self.resultado.setText("")
                x_fill = np.linspace(a, b, 100)
                self.ax.fill_between(x_fill, f1(x_fill), 0,
                                     color='red', alpha=0.3)
                area_latex = f"$\\text{{Área}} = {area:.6f}$"
                self.ax.annotate(
                    area_latex,
                    xy=(0.98, 0.98),
                    xycoords='axes fraction',
                    fontsize=16,
                    color='red',
                    ha='right',
                    va='top',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", lw=1, alpha=0.8)
                )
            else:
                expr2 = sympify(self.entradas[1].entrada.text())
                f2 = lambdify(x, expr2, 'numpy')
                h = lambda x: np.abs(f1(x) - f2(x))
                area = simpson_integration(h, a, b)
                self.resultado.setText("")
                x_fill = np.linspace(a, b, 100)
                self.ax.fill_between(x_fill, f1(x_fill), f2(x_fill),
                                     where=(f1(x_fill) > f2(x_fill)),
                                     color='red', alpha=0.3)
                area_latex = f"$\\text{{Área}} = {area:.6f}$"
                self.ax.annotate(
                    area_latex,
                    xy=(0.98, 0.98),
                    xycoords='axes fraction',
                    fontsize=16,
                    color='red',
                    ha='right',
                    va='top',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", lw=1, alpha=0.8)
                )

            self.canvas.draw()

        except Exception as e:
            self.resultado.setText(f"Error: {str(e)}")

        
 

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = GeoGebraApp()
    window.show()
    sys.exit(app.exec_())