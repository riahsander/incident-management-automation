"""
Configuração centralizada de logging da automação.

O módulo disponibiliza um logger compartilhado pelos componentes da
aplicação e configura a gravação simultânea dos eventos no console
e em arquivo.

Responsabilidades:
    - Criar o diretório destinado aos logs.
    - Configurar o formato padrão das mensagens.
    - Registrar eventos no console e em arquivo.
    - Aplicar rotação automática do arquivo de log.
    - Evitar a duplicação de handlers durante a execução.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("AutomaçãoIncidente")

def configurar_logger(output_dir):
    """
    Configura e retorna o logger compartilhado pela automação.

    Os logs são gravados no console e no arquivo
    output/logs/automacao.log.

    O arquivo utiliza rotação automática ao atingir 5 MB,
    mantendo até cinco arquivos anteriores como histórico.

    Args:
        output_dir (str): Diretório base utilizado para armazenar
        os arquivos de saída da aplicação.

    Returns:
        logging.Logger: Logger configurado para uso pela automação.
    """
    if logger.handlers:
        return logger

    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    logs_file = os.path.join(logs_dir, "automacao.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        logs_file,
        maxBytes=5 * 1024 * 1024, # 5MB
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger