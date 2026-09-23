@echo off

REM ============================================================
REM Instalacao da Automacao de Incidentes
REM
REM Responsavel por:
REM - Preparar os diretorios utilizados pela aplicacao.
REM - Copiar o executavel gerado pelo processo de build.
REM - Disponibilizar as configuracoes necessarias.
REM - Copiar os arquivos de dados utilizados pela automacao.
REM ============================================================

echo Instalando AutomacaoIncidente...

REM Copia o executável para a pasta principal
copy dist\main.exe "%~dp0"

REM Copia o arquivo .env
copy .env "%~dp0"

REM Copia a pasta data
xcopy data "%~dp0data" /E /I /Y

echo Instalacao concluida!
pause
