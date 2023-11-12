@echo off
title start-system
cd /d "%~dp0"
call tesis_env\Scripts\activate
:: Ejecuta start-server.bat
start "" call start-camara.bat
python cod_modelo_035_frames.py
:: Pregunta al usuario si desea cerrar el programa
set /p cerrar=¿Quiere cerrar el programa? [s] 
:: Verifica si la respuesta es 's' (sin distinguir mayúsculas o minúsculas)
if /i "%cerrar%"=="s" (
    echo Cerrando el programa...
    exit /b 0
