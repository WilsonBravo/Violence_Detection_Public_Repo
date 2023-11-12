@echo off
title start-telegraf
cd /d "%~dp0"
:: Ejecuta start-server.bat
start "" call start-influx.bat
cd /d "C:\Program Files\InfluxData\telegraf\telegraf-1.28.1"
call set INFLUX_TOKEN=
timeout /t 120
call .\telegraf.exe --config http://localhost:8086/api/v2/telegrafs/0bcf2fe5ef9f7000
:: call .\telegraf.exe --test --config http://localhost:8086/api/v2/telegrafs/0bcf2fe5ef9f7000