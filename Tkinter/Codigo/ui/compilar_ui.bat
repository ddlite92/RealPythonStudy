:inicio
@echo off
set /p nombre=Escribite el nombre uacho: 
set archivo_ui=%nombre%.ui
set archivo_py=%nombre%.py
:compilar
@echo on
call C:\Users\gutie\AppData\Roaming\Python\Python311\Scripts\pyuic5.exe %archivo_ui% -o %archivo_py%
@echo off
choice /c:SN /m "De vuelta?"
if %errorlevel% == 1 goto compilar

