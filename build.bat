@echo off

REM ============================================================
REM Build da Automacao de Incidentes
REM
REM Responsavel por:
REM - Remover builds anteriores.
REM - Gerar o executavel atraves do PyInstaller.
REM - Incluir os modulos e arquivos de dados necessarios.
REM - Incluir o Chromium utilizado pelo Playwright.
REM ============================================================

echo Limpando build antigo...
rmdir /S /Q build
rmdir /S /Q dist

echo Compilando projeto com PyInstaller...
python -m PyInstaller --onefile --noconsole main.py ^
--add-data "data;data" ^
--add-data "backend;backend" ^
--add-data "frontend;frontend" ^
--add-data ".env;." ^
--add-data "%LOCALAPPDATA%\ms-playwright\chromium-1234;chromium-1234""

echo Build concluído!
pause
