#!/bin/bash
# Автоматическая установка для Linux/macOS

echo "🚀 Установка зависимостей для Построителя Графиков"
echo "================================================"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен. Установите Python 3.7+"
    exit 1
fi

echo "✅ Python3 обнаружен: $(python3 --version)"

# Создаем виртуальное окружение
echo "🔧 Создаю виртуальное окружение..."
python3 -m venv venv

# Активируем виртуальное окружение
echo "🔧 Активирую виртуальное окружение..."
source venv/bin/activate

# Обновляем pip
echo "📦 Обновляю pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "📦 Устанавливаю зависимости..."
pip install -r requirements.txt

# Проверяем установку
echo "🔍 Проверяю установку..."
python3 -c "
try:
    import flask, matplotlib, numpy, scipy
    print('✅ Все библиотеки успешно установлены!')
    print('   Flask:', flask.__version__)
    print('   Matplotlib:', matplotlib.__version__)
    print('   NumPy:', numpy.__version__)
    print('   SciPy:', scipy.__version__)
except ImportError as e:
    print('❌ Ошибка:', e)
    exit(1)
"

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📋 Чтобы запустить приложение:"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "🌐 Затем откройте: http://localhost:5000"