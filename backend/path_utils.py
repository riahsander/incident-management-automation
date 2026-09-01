"""
path_utils.py

Módulo utilitário responsável pelo gerenciamento de caminhos
de arquivos e diretórios da aplicação.

O objetivo deste módulo é abstrair as diferenças entre os
ambientes de execução, permitindo que a aplicação funcione
corretamente tanto em desenvolvimento quanto em versões
empacotadas (.exe) geradas com PyInstaller.

Funcionalidades:
    - Localização de arquivos internos da aplicação.
    - Compatibilidade com execução em ambiente empacotado.
    - Criação automática de diretórios de saída.
    - Centralização do gerenciamento de caminhos.

Compatibilidade:
    - Execução local (.py)
    - Executáveis gerados com PyInstaller (.exe)
"""

import os, sys

def get_path(relative_path):
    """
    Retorna o caminho absoluto de um recurso da aplicação.
     
    A função identifica automaticamente o ambiente de execução
    e monta o caminho correto para acesso a arquivos internos.
     
    Em ambiente empacotado:
    Utiliza o diretório temporário criado pelo PyInstaller.
     
    Em ambiente de desenvolvimento:
    Utiliza a pasta raiz do projeto.
     
    Args:
    relative_path (str):
    Caminho relativo do arquivo desejado.
     
    Returns:
    str:
    Caminho absoluto do recurso solicitado.
     
    Exemplo:
     
    get_path("data/info_incidente.json")
     
    Resultado:
     
    C:/Projeto/data/info_incidente.json
    """
    """Retorna o caminho correto para arquivos empacotados no .exe."""
    if getattr(sys, 'frozen', False):
        # Pasta do .exe
        base_path = sys._MEIPASS
    else:
        # Pasta raiz do projeto
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



def get_output_path(relative_path):
    """
    Retorna o caminho destinado ao armazenamento de arquivos
    gerados pela aplicação.
     
    Em ambiente empacotado:
    Os arquivos são gravados na mesma pasta onde o
    executável está localizado.
     
    Em ambiente de desenvolvimento:
    Os arquivos são gravados na raiz do projeto.
     
    Caso o diretório informado não exista, ele será criado
    automaticamente.
     
    Args:
    relative_path (str):
    Caminho relativo do diretório de saída.
     
    Returns:
    str:
    Caminho absoluto do diretório criado ou localizado.
     
    Exemplo:
     
    get_output_path("output/printOP")
     
    Resultado:
     
    C:/Projeto/output/printOP
    """
    """Retorna caminho para salvar arquivos na mesma pasta do executável."""
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    full_path = os.path.join(base_path, relative_path)
    os.makedirs(full_path, exist_ok=True)  # garante que a pasta exista
    return full_path
