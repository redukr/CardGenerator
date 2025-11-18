@echo off
chcp 65001 >nul

echo ============================================
echo     CARD GENERATOR — AUTO BUILD SCRIPT
echo ============================================
echo.

REM Переходимо в директорію app/
cd /d "%~dp0"

echo [1/4] Очищаю старі збірки...
if exist build (rmdir /s /q build)
if exist dist (rmdir /s /q dist)
echo ✔ Очищено.
echo.

echo [2/4] Використовую portable Python 3.10...
set PYTHON=..\python310\python.exe

if not exist %PYTHON% (
    echo ❌ Помилка: portable Python не знайдено.
    echo Перевір шлях: ..\python310\python.exe
    pause
    exit /b
)

echo ✔ Python знайдено.
echo.

echo [3/4] Запускаю PyInstaller...
%PYTHON% -m PyInstaller CardGenerator.spec

if %errorlevel% neq 0 (
    echo ❌ Помилка під час збірки EXE!
    pause
    exit /b
)

echo ✔ PyInstaller успішно завершив роботу.
echo.

echo [4/4] Готовий EXE:
echo dist\CardGenerator\CardGenerator.exe
echo.

echo ============================================
echo          ✔ ЗБІРКА ЗАВЕРШЕНА
echo ============================================

pause
