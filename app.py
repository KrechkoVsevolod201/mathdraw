from flask import Flask, request, render_template, send_from_directory, Response
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import re
import numpy as np
import os
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm

app = Flask(__name__)

def take_math_equation(equation_str, variables_count=1):
    """Преобразует строку с уравнением в лямбда-функцию"""
    try:
        # Безопасное преобразование математических выражений
        equation_str = equation_str.replace('^', '**')
        equation_str = equation_str.replace('X', 'x')
        equation_str = equation_str.replace('Y', 'y')
        equation_str = equation_str.replace('Z', 'z')
        
        # Создаем безопасное лямбда-выражение
        allowed_names = {
            'x': None, 'y': None, 'z': None,
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
        
        if variables_count == 3:
            return lambda x, y, z: eval(equation_str, {'__builtins__': {}}, allowed_names | {'x': x, 'y': y, 'z': z})
        elif variables_count == 2:
            return lambda x, y: eval(equation_str, {'__builtins__': {}}, allowed_names | {'x': x, 'y': y})
        else:
            return lambda x: eval(equation_str, {'__builtins__': {}}, allowed_names | {'x': x})
    
    except Exception as e:
        raise ValueError(f"Ошибка в уравнении: {e}")

def get_colormap(color_name):
    """Возвращает цветовую карту по имени"""
    colormaps = {
        'blue': cm.Blues,
        'orange': cm.Oranges,
        'green': cm.Greens,
        'red': cm.Reds,
        'purple': cm.Purples,
        'black': cm.Greys,
        'rainbow': cm.rainbow,
        'hot': cm.hot,
        'cool': cm.cool,
        'viridis': cm.viridis,
        'plasma': cm.plasma,
        'magma': cm.magma
    }
    return colormaps.get(color_name, cm.Blues)

def get_single_color(color_name):
    """Возвращает одиночный цвет для линейных графиков"""
    colors = {
        'blue': '#1f77b4',
        'orange': '#ff7f0e',
        'green': '#2ca02c',
        'red': '#d62728',
        'purple': '#9467bd',
        'black': '#000000'
    }
    return colors.get(color_name, '#1f77b4')

def create_plot(func, color_name, variables_count=1, format='png'):
    """Создает график функции и возвращает его в указанном формате"""
    try:
        plt.figure(figsize=(8, 6), dpi=100, facecolor='white')
        
        if variables_count == 3:
            # Для функций с тремя переменными (x, y, z)
            x = np.linspace(-5, 5, 30)
            y = np.linspace(-5, 5, 30)
            z_val = np.linspace(-5, 5, 30)
            X, Y, Z = np.meshgrid(x, y, z_val)
            
            # Вычисляем значение функции
            W = func(X, Y, Z)
            
            # Визуализируем 2D срез при z=0
            z_index = np.abs(z_val).argmin()  # Индекс ближайшего к нулю z
            Z_slice = Z[:, :, z_index]
            W_slice = W[:, :, z_index]
            
            colormap = get_colormap(color_name)
            plt.contourf(X[:, :, z_index], Y[:, :, z_index], W_slice, levels=50, cmap=colormap)
            
        elif variables_count == 2:
            # Для функций с двумя переменными (x, y)
            x = np.linspace(-10, 10, 100)
            y = np.linspace(-10, 10, 100)
            X, Y = np.meshgrid(x, y)
            Z = func(X, Y)
            
            colormap = get_colormap(color_name)
            plt.contourf(X, Y, Z, levels=50, cmap=colormap)
                
        else:
            # Для функций с одной переменной (x)
            x = np.linspace(-10, 10, 1000)
            y = func(x)
            
            if color_name in ['rainbow', 'hot', 'cool', 'viridis', 'plasma', 'magma']:
                # Для цветовых схем используем градиент
                colormap = get_colormap(color_name)
                for i in range(len(x)-1):
                    color = colormap(i/len(x))
                    plt.plot(x[i:i+2], y[i:i+2], color=color, linewidth=3)
            else:
                # Для одиночных цветов
                color = get_single_color(color_name)
                plt.plot(x, y, color=color, linewidth=3)
        
        # Убираем все оси и обозначения
        plt.axis('off')
        plt.tight_layout(pad=0)
        
        # Сохраняем в буфер в указанном формате
        buf = BytesIO()
        plt.savefig(buf, format=format, bbox_inches='tight', pad_inches=0,
                   facecolor='white', edgecolor='none', transparent=True)
        plt.close()
        buf.seek(0)
        
        return buf
    
    except Exception as e:
        raise ValueError(f"Ошибка построения графика: {e}")

def print_graph(func, color_name, variables_count=1):
    """Создает график функции и возвращает его как base64 строку"""
    buf = create_plot(func, color_name, variables_count, 'png')
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html', plot_data=None, error=None)

@app.route('/plot', methods=['POST'])
def plot():
    equation = request.form.get('equation', '')
    color_name = request.form.get('color', 'blue')
    function_type = request.form.get('function_type', 'x')
    
    if not equation:
        return render_template('index.html', plot_data=None, error="Введите уравнение")
    
    try:
        if function_type == 'xyz':
            variables_count = 3
        elif function_type == 'xy':
            variables_count = 2
        else:
            variables_count = 1
            
        func = take_math_equation(equation, variables_count)
        plot_data = print_graph(func, color_name, variables_count)
        
        return render_template('index.html', 
                             plot_data=plot_data, 
                             error=None, 
                             equation=equation, 
                             color=color_name,
                             function_type=function_type)
    
    except Exception as e:
        return render_template('index.html', 
                             plot_data=None, 
                             error=str(e), 
                             equation=equation, 
                             color=color_name,
                             function_type=function_type)

@app.route('/download', methods=['POST'])
def download():
    format = request.form.get('format')
    equation = request.form.get('equation', '')
    color_name = request.form.get('color', 'blue')
    function_type = request.form.get('function_type', 'x')
    
    if not equation or not format:
        return "Ошибка: уравнение или формат не указаны", 400
    
    try:
        if function_type == 'xyz':
            variables_count = 3
        elif function_type == 'xy':
            variables_count = 2
        else:
            variables_count = 1
            
        func = take_math_equation(equation, variables_count)
        
        if format not in ['png', 'svg']:
            return "Неверный формат", 400
        
        buf = create_plot(func, color_name, variables_count, format)
        
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