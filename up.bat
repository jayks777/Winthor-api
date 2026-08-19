@echo off

cd /d "C:\App\API"

echo Atualizando o codigo com Git...
git pull

echo Atualizando dependencias...
C:\App\API\venv\Scripts\python.exe -m pip install --upgrade pip
C:\App\API\venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo Reiniciando o servico do FastAPI...

powershell -Command "Stop-Service -Name 'FastAPI'"
powershell -Command "Start-Service -Name 'FastAPI'"

echo.
echo Processo concluido com sucesso!
pause
