import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLabel, QLineEdit, QPushButton)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class IntegralCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Integrales (Método de Simpson)")
        self.setGeometry(100, 100, 800, 600)
        
        # Widgets
        self.label_funcion = QLabel("Función f(x) (usa numpy: np.sin(x), np.log(x), etc.):")
        self.entrada_funcion = QLineEdit("np.sin(x)")
        
        self.label_lim_inf = QLabel("Límite inferior:")
        self.entrada_lim_inf = QLineEdit("0")
        
        self.label_lim_sup = QLabel("Límite superior:")
        self.entrada_lim_sup = QLineEdit("3.1416")
        
        self.label_particiones = QLabel("Número de particiones (par):")
        self.entrada_particiones = QLineEdit("100")
        
        self.boton_calcular = QPushButton("Calcular Integral")
        self.boton_calcular.clicked.connect(self.calcular_integral)
        
        self.label_resultado = QLabel("Resultado: -")
        
        # Gráfico
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_funcion)
        layout.addWidget(self.entrada_funcion)
        layout.addWidget(self.label_lim_inf)
        layout.addWidget(self.entrada_lim_inf)
        layout.addWidget(self.label_lim_sup)
        layout.addWidget(self.entrada_lim_sup)
        layout.addWidget(self.label_particiones)
        layout.addWidget(self.entrada_particiones)
        layout.addWidget(self.boton_calcular)
        layout.addWidget(self.label_resultado)
        layout.addWidget(self.canvas)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def calcular_integral(self):
        # Obtener datos de la interfaz
        funcion_str = self.entrada_funcion.text().strip()
        a = float(self.entrada_lim_inf.text())
        b = float(self.entrada_lim_sup.text())
        n = int(self.entrada_particiones.text())
        
        # Validar que n sea par
        if n % 2 != 0:
            self.label_resultado.setText("Error: El número de particiones debe ser par.")
            return
        
        # Método de Simpson 1/3
        def simpson(f, a, b, n):
            h = (b - a) / n
            x = np.linspace(a, b, n+1)
            y = f(x)
            suma_impares = np.sum(y[1:-1:2])
            suma_pares = np.sum(y[2:-1:2])
            integral = (h / 3) * (y[0] + 4 * suma_impares + 2 * suma_pares + y[-1])
            return integral, x, y
        
        try:
            # Crear función dinámicamente
            f = lambda x: eval(funcion_str, {'np': np, 'x': x})
            
            # Calcular integral
            integral, x_vals, y_vals = simpson(f, a, b, n)
            
            # Graficar
            self.ax.clear()
            self.ax.plot(x_vals, y_vals, 'b-', label=f'f(x) = {funcion_str}')
            self.ax.fill_between(x_vals, y_vals, color='skyblue', alpha=0.4, label=f'Área ≈ {integral:.6f}')
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('f(x)')
            self.ax.legend()
            self.ax.grid(True)
            self.ax.set_title(f'Integral aproximada por Simpson (n={n})')
            self.canvas.draw()
            
            self.label_resultado.setText(f"Resultado: {integral:.6f}")
        except Exception as e:
            self.label_resultado.setText(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    window = IntegralCalculator()
    window.show()
    app.exec_()