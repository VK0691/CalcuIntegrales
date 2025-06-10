import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Integrales (PyQt)")
        self.setGeometry(100, 100, 800, 600)
        
        # Widgets
        self.label_funcion = QLabel("Función f(x):")
        self.entrada_funcion = QLineEdit("x*2 + 1")
        
        self.label_lim_inf = QLabel("Límite inferior:")
        self.entrada_lim_inf = QLineEdit("0")
        
        self.label_lim_sup = QLabel("Límite superior:")
        self.entrada_lim_sup = QLineEdit("1")
        
        self.boton_calcular = QPushButton("Calcular Integral")
        self.boton_calcular.clicked.connect(self.calcular_y_graficar)
        
        self.label_resultado = QLabel("Resultado: -")
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_funcion)
        layout.addWidget(self.entrada_funcion)
        layout.addWidget(self.label_lim_inf)
        layout.addWidget(self.entrada_lim_inf)
        layout.addWidget(self.label_lim_sup)
        layout.addWidget(self.entrada_lim_sup)
        layout.addWidget(self.boton_calcular)
        layout.addWidget(self.label_resultado)
        
        # Gráfico de Matplotlib
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def calcular_y_graficar(self):
        funcion = self.entrada_funcion.text()
        lim_inf = float(self.entrada_lim_inf.text())
        lim_sup = float(self.entrada_lim_sup.text())
        
        x = sp.symbols('x')
        try:
            f = sp.sympify(funcion)
            integral = sp.integrate(f, (x, lim_inf, lim_sup))
            
            # Limpiar gráfico anterior
            self.ax.clear()
            
            # Generar datos
            x_vals = np.linspace(lim_inf, lim_sup, 400)
            f_numeric = sp.lambdify(x, f, 'numpy')
            y_vals = f_numeric(x_vals)
            
            # Dibujar
            self.ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'$f(x) = {funcion}$')
            self.ax.fill_between(x_vals, y_vals, color='skyblue', alpha=0.4, label=f'Área ≈ {integral.evalf():.4f}')
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('f(x)')
            self.ax.legend()
            self.ax.grid(True)
            self.ax.set_title(f'Integral de ${funcion}$ entre ${lim_inf}$ y ${lim_sup}$')
            
            self.canvas.draw()
            self.label_resultado.setText(f"Resultado: {integral.evalf():.6f}")
        except Exception as e:
            self.label_resultado.setText(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())