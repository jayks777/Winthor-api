@echo off

@REM Troque por o endereço da sua api
cd /d "C:\App\API"

color 0b
echo Atualizando o codigo com Git...
color 07
git pull

echo Atualizando dependencias...
C:\App\API\venv\Scripts\python.exe -m pip install --upgrade pip
C:\App\API\venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Reiniciando o servico do FastAPI...

powershell -Command "Stop-Service -Name 'FastAPI'"
powershell -Command "Start-Service -Name 'FastAPI'"

echo.
color 0a
echo Processo concluido com sucesso!
pause
