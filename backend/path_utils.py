"""
Utilitários para resolução de caminhos da aplicação.

O módulo abstrai diferenças entre a execução diretamente pelo código
Python e a execução através da versão empacotada da automação.

Responsabilidades:
    - Resolver caminhos de recursos utilizados pela aplicação.
    - Localizar arquivos incluídos no executável empacotado.
    - Determinar diretórios apropriados para arquivos gerados.
    - Criar automaticamente diretórios de saída quando necessário.
"""

import os, sys
from backend.logger_config import logger

def get_path(relative_path):
    """
    Resolve o caminho absoluto de um recurso da aplicação.

    Durante a execução empacotada, utiliza o diretório temporário
    disponibilizado pelo empacotador. Durante o desenvolvimento,
    utiliza o diretório raiz do projeto.

    Args:
        relative_path (str): Caminho relativo do recurso.

    Returns:
        str: Caminho absoluto correspondente ao recurso.
    """
    try:
        if getattr(sys, 'frozen', False):
            # Pasta do .exe
            base_path = sys._MEIPASS
        else:
            # Pasta raiz do projeto
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    except Exception:
        logger.exception("Erro ao retornar os caminhos para os arquivos")


def get_output_path(relative_path):
    """
    Resolve e prepara um diretório destinado aos arquivos de saída.

    Quando a aplicação está empacotada, utiliza como referência
    o diretório do executável. Durante o desenvolvimento, utiliza
    a raiz do projeto.

    O diretório é criado automaticamente caso ainda não exista.

    Args:
        relative_path (str): Caminho relativo do diretório de saída.

    Returns:
        str: Caminho absoluto do diretório preparado para gravação.
    """
    try:
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        full_path = os.path.join(base_path, relative_path)
        os.makedirs(full_path, exist_ok=True)  # garante que a pasta exista
        return full_path
    except Exception:
        logger.exception("Erro ao retornar os caminhos onde os arquivos devem ser salvos")