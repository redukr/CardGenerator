@echo off
chcp 65001 >nul

echo ===============================
echo   CardGenerator — Build Script
echo ===============================

echo.
echo --- Очистка старих збірок ---
echo.

IF EXIST dist (
    echo Видаляю dist...
    rmdir /s /q dist
)

IF EXIST build (
    echo Видаляю build...
    rmdir /s /q build
)

IF EXIST __pycache__ (
    echo Видаляю __pycache__...
    rmdir /s /q __pycache__
)

echo.
echo --- Запуск PyInstaller ---
echo.

"C:\Users\GDF\AppData\Local\Programs\Python\Python310\python.exe" -m PyInstaller CardGenerator.spec

echo.
echo ===============================
echo   Збірка завершена
echo ===============================
pause
