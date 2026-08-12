@echo off
:: Altere para o caminho da pasta onde está o seu projeto Git
cd /d "C:\App\API"

echo Atualizando o codigo com Git...
git pull

echo.
echo Reiniciando o servico do FastAPI...
:: Substitua "NomeDoSeuServico" pelo nome exato do servico no Windows
net stop "FastAPI"
net start "FastAPI"

echo.
echo Processo concluido com sucesso!
pause
