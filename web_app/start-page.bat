title start-page
cd /d "%~dp0"
call env\Scripts\activate
:: Empezar la pagina
python manage.py runserver 192.168.3.101:8000
:: Pregunta al usuario si desea cerrar el programa
set /p cerrar=¿Quiere cerrar el programa? [s] 
:: Verifica si la respuesta es 's' (sin distinguir mayúsculas o minúsculas)
if /i "%cerrar%"=="s" (
    echo Cerrando el programa...
    exit /b 0