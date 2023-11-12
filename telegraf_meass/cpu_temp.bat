@echo off
WMIC /namespace:\\root\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature