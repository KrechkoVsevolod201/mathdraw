from flask import Flask, request, render_template, send_from_directory, Response
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import re
import numpy as np
import os

app = Flask(__name__)

def take_math_equation(equation_str, has_y=False):
    """Преобразует строку с уравнением в лямбда-функцию"""
    try:
        # Безопасное преобразование математических выражений
        equation_str = equation_str.replace('^', '**')
        equation_str = equation_str.replace('X', 'x')
        equation_str = equation_str.replace('Y', 'y')
        
        # Создаем безопасное лямбда-выражение
        allowed_names = {
            'x': None, 'y': None,
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
        
        if has_y:
            return lambda x, y: eval(equation_str, {'__builtins__': {}}, allowed_names | {'x': x, 'y': y})
        else:
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

def create_plot(func, color_scheme, has_y=False, format='png'):
    """Создает график функции и возвращает его в указанном формате"""
    try:
        plt.figure(figsize=(8, 6), dpi=100, facecolor='white')
        
        if has_y:
            # Для функций с двумя переменными (x, y)
            x = np.linspace(-10, 10, 100)
            y = np.linspace(-10, 10, 100)
            X, Y = np.meshgrid(x, y)
            Z = func(X, Y)
            
            plt.contour(X, Y, Z, levels=20, colors=color_scheme)
            plt.colorbar()
            plt.title(f'z = f(x, y)')
        else:
            # Для функций с одной переменной (x)
            x = np.linspace(-10, 10, 1000)
            y = func(x)
            
            plt.plot(x, y, color=color_scheme, linewidth=2)
            plt.title(f'y = f(x)')
        
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        plt.grid(True, alpha=0.3)
        plt.xlabel('x')
        plt.ylabel('y' if not has_y else 'z')
        plt.tight_layout()
        
        # Сохраняем в буфер в указанном формате
        buf = BytesIO()
        plt.savefig(buf, format=format, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        buf.seek(0)
        
        return buf
    
    except Exception as e:
        raise ValueError(f"Ошибка построения графика: {e}")

def print_graph(func, color_scheme, has_y=False):
    """Создает график функции и возвращает его как base64 строку"""
    buf = create_plot(func, color_scheme, has_y, 'png')
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html', plot_data=None, error=None)

@app.route('/plot', methods=['POST'])
def plot():
    equation = request.form.get('equation', '')
    color_scheme_name = request.form.get('color', 'blue')
    function_type = request.form.get('function_type', 'x')
    
    if not equation:
        return render_template('index.html', plot_data=None, error="Введите уравнение")
    
    try:
        has_y = (function_type == 'xy')
        color_scheme = get_color_scheme(color_scheme_name)
        func = take_math_equation(equation, has_y)
        plot_data = print_graph(func, color_scheme, has_y)
        
        return render_template('index.html', 
                             plot_data=plot_data, 
                             error=None, 
                             equation=equation, 
                             color=color_scheme_name,
                             function_type=function_type)
    
    except Exception as e:
        return render_template('index.html', 
                             plot_data=None, 
                             error=str(e), 
                             equation=equation, 
                             color=color_scheme_name,
                             function_type=function_type)

@app.route('/download', methods=['POST'])
def download():
    format = request.form.get('format')
    equation = request.form.get('equation', '')
    color_scheme_name = request.form.get('color', 'blue')
    function_type = request.form.get('function_type', 'x')
    
    if not equation or not format:
        return "Ошибка: уравнение или формат не указаны", 400
    
    try:
        has_y = (function_type == 'xy')
        color_scheme = get_color_scheme(color_scheme_name)
        func = take_math_equation(equation, has_y)
        
        if format not in ['png', 'svg']:
            return "Неверный формат", 400
        
        buf = create_plot(func, color_scheme, has_y, format)
        
        filename = f"graph.{format}"
        return Response(
            buf.getvalue(),
            mimetype=f'image/{format}',
            headers={'Content-Disposition': f'attachment;filename={filename}'}
        )
    
    except Exception as e:
        return f"Ошибка: {str(e)}", 400

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # Создаем необходимые папки
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)