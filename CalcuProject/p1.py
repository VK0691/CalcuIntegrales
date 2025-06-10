import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

def calcular_integral(func_str, a, b):
    x = sp.symbols('x')
    f = sp.sympify(func_str)  # Convierte el string en una expresión simbólica
    integral = sp.integrate(f, (x, a, b))  # Calcula la integral definida
    
    # Graficar la función y el área bajo la curva
    f_numeric = sp.lambdify(x, f, 'numpy')  # Convierte la función a una forma evaluable
    x_vals = np.linspace(float(a), float(b), 1000)
    y_vals = f_numeric(x_vals)
    
    plt.figure(figsize=(8, 5))
    plt.plot(x_vals, y_vals, label=f'f(x) = {func_str}')
    plt.fill_between(x_vals, y_vals, alpha=0.3, label=f'Área = {integral.evalf():.4f}')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.legend()
    plt.grid(True)
    plt.title(f'Integral de {func_str} entre {a} y {b}')
    plt.show()
    
    return integral.evalf()

# Ejemplo de uso
funcion = input("Ingresa la función (ej: x**2 + 3*x + 2): ")
lim_inf = float(input("Límite inferior: "))
lim_sup = float(input("Límite superior: "))

resultado = calcular_integral(funcion, lim_inf, lim_sup)
print(f"El resultado de la integral es: {resultado}")