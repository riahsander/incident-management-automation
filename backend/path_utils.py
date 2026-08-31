"""
path_utils.py

Módulo utilitário responsável pelo gerenciamento de caminhos de arquivos
e diretórios da aplicação.

O objetivo deste módulo é abstrair as diferenças entre a execução do
projeto em ambiente de desenvolvimento e a execução da aplicação
empacotada como executável (.exe).

Funcionalidades:
    - Localizar arquivos internos da aplicação.
    - Determinar caminhos compatíveis com PyInstaller.
    - Criar e recuperar diretórios de saída para geração de arquivos.

Compatibilidade:
    - Python (.py)
    - Executável PyInstaller (.exe)
"""

import os, sys

def get_path(relative_path):
    """
    Retorna o caminho absoluto de um recurso da aplicação.
     
    A função identifica automaticamente se a aplicação está sendo
    executada em ambiente de desenvolvimento ou como executável
    gerado pelo PyInstaller.
     
    Quando executada como .exe, utiliza o diretório temporário criado
    pelo PyInstaller para acessar os arquivos empacotados.
     
    Args:
    relative_path (str):
    Caminho relativo do arquivo desejado.
     
    Returns:
    str:
    Caminho absoluto do recurso solicitado.
     
    Exemplo:
    get_path("data/info_incidente.json")
    """
    # Quando executado como .exe, utiliza a pasta temporária
    # criada pelo PyInstaller.
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    # Quando executado em desenvolvimento, utiliza a pasta
    # do próprio módulo.
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_output_path(relative_path):
    """
    Retorna o diretório utilizado para salvar arquivos gerados
    pela aplicação.
     
    Em ambiente empacotado (.exe), os arquivos são gravados na
    mesma pasta onde o executável está localizado.
     
    Em ambiente de desenvolvimento, os arquivos são gravados
    relativamente ao diretório do módulo.
     
    Caso o diretório não exista, ele será criado automaticamente.
     
    Args:
    relative_path (str):
    Nome da pasta ou caminho relativo a ser criado.
     
    Returns:
    str:
    Caminho absoluto para gravação dos arquivos.
     
    Exemplo:
    get_output_path("screenshots")
     
    Resultado:
    C:/Aplicacao/screenshots
    """
    # Salva arquivos na mesma pasta do executável.
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    # Em desenvolvimento utiliza a pasta do módulo.
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    full_path = os.path.join(base_path, relative_path)
    # Garante a existência do diretório informado.
    os.makedirs(full_path, exist_ok=True)  # garante que a pasta exista
    return full_path
