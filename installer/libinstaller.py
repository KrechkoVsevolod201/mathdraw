#!/usr/bin/env python3
"""
Автоматический установщик зависимостей для построителя графиков
"""

import subprocess
import sys
import os

def check_python_version():
    """Проверяет версию Python"""
    if sys.version_info < (3, 7):
        print("❌ Требуется Python 3.7 или выше")
        print(f"📋 Текущая версия: {sys.version}")
        return False
    print(f"✅ Python {sys.version} - подходит")
    return True

def install_requirements():
    """Устанавливает зависимости из requirements.txt"""
    try:
        print("📦 Устанавливаю зависимости...")
        
        # Проверяем существование requirements.txt
        if not os.path.exists('requirements.txt'):
            print("❌ Файл requirements.txt не найден")
            return False
        
        # Устанавливаем зависимости
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            '--upgrade', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Все зависимости успешно установлены!")
            return True
        else:
            print("❌ Ошибка при установке зависимостей:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False

def create_virtual_env():
    """Создает виртуальное окружение (опционально)"""
    try:
        print("\n🔧 Создаю виртуальное окружение...")
        
        # Проверяем, существует ли уже виртуальное окружение
        if os.path.exists('venv'):
            print("✅ Виртуальное окружение уже существует")
            return True
            
        result = subprocess.run([
            sys.executable, '-m', 'venv', 'venv'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Виртуальное окружение создано")
            return True
        else:
            print("⚠️ Не удалось создать виртуальное окружение:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"⚠️ Ошибка при создании виртуального окружения: {e}")
        return False

def check_installation():
    """Проверяет успешность установки"""
    print("\n🔍 Проверяю установку...")
    
    try:
        # Пробуем импортировать основные библиотеки
        import flask
        import matplotlib
        import numpy
        import scipy
        
        print("✅ Flask установлен:", flask.__version__)
        print("✅ Matplotlib установлен:", matplotlib.__version__)
        print("✅ NumPy установлен:", numpy.__version__)
        print("✅ SciPy установлен:", scipy.__version__)
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def main():
    """Основная функция установки"""
    print("🚀 Автоматическая установка зависимостей для Построителя Графиков")
    print("=" * 60)
    
    # Проверяем версию Python
    if not check_python_version():
        sys.exit(1)
    
    # Предлагаем создать виртуальное окружение
    create_env = input("\n🔄 Создать виртуальное окружение? (y/n): ").lower().strip()
    if create_env in ['y', 'yes', 'да']:
        if create_virtual_env():
            # Активируем виртуальное окружение
            if sys.platform == 'win32':
                python_path = os.path.join('venv', 'Scripts', 'python.exe')
                pip_path = os.path.join('venv', 'Scripts', 'pip.exe')
            else:
                python_path = os.path.join('venv', 'bin', 'python')
                pip_path = os.path.join('venv', 'bin', 'pip')
            
            if os.path.exists(python_path):
                print(f"✅ Использую Python из виртуального окружения: {python_path}")
                sys.executable = python_path
    
    # Устанавливаем зависимости
    if install_requirements():
        # Проверяем установку
        if check_installation():
            print("\n🎉 Установка завершена успешно!")
            print("\n📋 Чтобы запустить приложение, выполните:")
            print("   python app.py")
            print("\n🌐 Затем откройте в браузере: http://localhost:5000")
        else:
            print("\n⚠️ Установка завершена с ошибками проверки")
    else:
        print("\n❌ Установка не удалась")
        sys.exit(1)

if __name__ == "__main__":
    main()