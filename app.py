from flask import Flask, request, render_template, send_from_directory
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import re
import numpy as np
import os

app = Flask(__name__)

def take_math_equation(equation_str):
    """Преобразует строку с уравнением в лямбда-функцию"""
    try:
        # Безопасное преобразование математических выражений
        equation_str = equation_str.replace('^', '**')
        equation_str = equation_str.replace('X', 'x')
        
        # Создаем безопасное лямбда-выражение
        allowed_names = {
            'x': None,
            'np': np,
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'sqrt': np.sqrt, 'log': np.log, 'exp': np.exp,
            'pi': np.pi, 'e': np.e
        }
        
        # Проверяем безопасность выражения
        code = compile(equation_str, '<string>', 'eval')
        for name in code.co_names:
            if name not in allowed_names:
                raise ValueError(f"Использование '{name}' не разрешено")
        
        return lambda x: eval(equation_str, {'__builtins__': {}}, allowed_names | {'x': x})
    
    except Exception as e:
        raise ValueError(f"Ошибка в уравнении: {e}")

def get_color_scheme(color_name):
    """Возвращает цветовую схему по имени"""
    colors = {
        'blue': '#1f77b4',
        'orange': '#ff7f0e',
        'green': '#2ca02c',
        'red': '#d62728',
        'purple': '#9467bd',
        'black': '#000000'
    }
    return colors.get(color_name, '#1f77b4')

def print_graph(func, color_scheme):
    """Создает график функции и возвращает его как base64 строку"""
    try:
        plt.figure(figsize=(8, 6), dpi=100, facecolor='white')
        x = np.linspace(-10, 10, 1000)
        y = func(x)
        
        plt.plot(x, y, color=color_scheme, linewidth=3)
        plt.axis('off')  # Убираем оси
        plt.tight_layout(pad=0)
        
        # Сохраняем в буфер
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, 
                   facecolor='white', edgecolor='none')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    except Exception as e:
        raise ValueError(f"Ошибка построения графика: {e}")

@app.route('/')
def index():
    return render_template('index.html', plot_data=None, error=None)

@app.route('/plot', methods=['POST'])
def plot():
    equation = request.form.get('equation', '')
    color_scheme_name = request.form.get('color', 'blue')
    
    if not equation:
        return render_template('index.html', plot_data=None, error="Введите уравнение")
    
    try:
        color_scheme = get_color_scheme(color_scheme_name)
        func = take_math_equation(equation)
        plot_data = print_graph(func, color_scheme)
        return render_template('index.html', plot_data=plot_data, error=None, 
                              equation=equation, color=color_scheme_name)
    
    except Exception as e:
        return render_template('index.html', plot_data=None, error=str(e), 
                              equation=equation, color=color_scheme_name)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # Создаем необходимые папки
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)