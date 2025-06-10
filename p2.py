import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Integrales Avanzada")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
            }
        """)

        # Widgets principales
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Grupo: Entrada de datos
        group_input = QGroupBox("Ingresa los datos de la integral")
        layout_input = QVBoxLayout(group_input)

        self.label_funcion = QLabel("Función f(x):")
        self.entrada_funcion = QLineEdit("x**2 + sin(x)")
        
        self.label_lim_inf = QLabel("Límite inferior (a):")
        self.entrada_lim_inf = QLineEdit("0")
        
        self.label_lim_sup = QLabel("Límite superior (b):")
        self.entrada_lim_sup = QLineEdit("3.14")  # Ejemplo con π
        
        self.boton_calcular = QPushButton("Calcular Integral")
        self.boton_calcular.clicked.connect(self.calcular_y_graficar)
        
        self.label_resultado = QLabel("Resultado: -")
        self.label_resultado.setFont(QFont("Arial", 16, QFont.Bold))

        # Agregar widgets al grupo de entrada
        layout_input.addWidget(self.label_funcion)
        layout_input.addWidget(self.entrada_funcion)
        layout_input.addWidget(self.label_lim_inf)
        layout_input.addWidget(self.entrada_lim_inf)
        layout_input.addWidget(self.label_lim_sup)
        layout_input.addWidget(self.entrada_lim_sup)
        layout_input.addWidget(self.boton_calcular)
        layout_input.addWidget(self.label_resultado)

        # Grupo: Gráfico
        group_graph = QGroupBox("Gráfico de la integral")
        layout_graph = QVBoxLayout(group_graph)
        
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        layout_graph.addWidget(self.canvas)

        # Agregar grupos al layout principal
        layout.addWidget(group_input)
        layout.addWidget(group_graph)

    def calcular_y_graficar(self):
        funcion = self.entrada_funcion.text()
        lim_inf = float(self.entrada_lim_inf.text())
        lim_sup = float(self.entrada_lim_sup.text())
        
        x = sp.symbols('x')
        try:
            f = sp.sympify(funcion)  # Convierte el string en una función simbólica
            integral = sp.integrate(f, (x, lim_inf, lim_sup))  # Calcula la integral
            
            # Limpiar gráfico anterior
            self.ax.clear()
            
            # Generar datos para el gráfico
            x_vals = np.linspace(lim_inf, lim_sup, 400)
            f_numeric = sp.lambdify(x, f, 'numpy')  # Convierte la función a numérica
            y_vals = f_numeric(x_vals)
            
            # Dibujar la función y el área bajo la curva
            self.ax.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'$f(x) = {funcion}$')
            self.ax.fill_between(x_vals, y_vals, color='skyblue', alpha=0.4, 
                                label=f'Área ≈ {integral.evalf():.4f}')
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('f(x)')
            self.ax.legend()
            self.ax.grid(True)
            self.ax.set_title(f'Integral de ${funcion}$ entre ${lim_inf}$ y ${lim_sup}$')
            
            # Actualizar gráfico
            self.canvas.draw()
            self.label_resultado.setText(f"Resultado: {integral.evalf():.6f}")
        except Exception as e:
            self.label_resultado.setText(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())