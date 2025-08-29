@echo off
chcp 65001 >nul
echo 🚀 Установка зависимостей для Построителя Графиков
echo ================================================

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не установлен или не добавлен в PATH
    pause
    exit /b 1
)

echo ✅ Python обнаружен: 
python --version

:: Создаем виртуальное окружение
echo 🔧 Создаю виртуальное окружение...
python -m venv venv

:: Активируем виртуальное окружение
echo 🔧 Активирую виртуальное окружение...
call venv\Scripts\activate.bat

:: Обновляем pip
echo 📦 Обновляю pip...
python -m pip install --upgrade pip

:: Устанавливаем зависимости
echo 📦 Устанавливаю зависимости...
pip install -r requirements.txt

:: Проверяем установку
echo 🔍 Проверяю установку...
python -c "
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

echo.
echo 🎉 Установка завершена!
echo.
echo 📋 Чтобы запустить приложение:
echo    venv\Scripts\activate.bat
echo    python app.py
echo.
echo 🌐 Затем откройте: http://localhost:5000
echo.
pause