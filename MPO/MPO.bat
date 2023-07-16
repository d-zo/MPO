@echo off
rem @call ifortvars.bat intel64 vs2015
@call "C:\Path\to\Intel\oneAPI\compiler\latest\env\vars.bat" intel64 vs2019
C:\Path\to\Python\python.exe MPO.pyz
pause
