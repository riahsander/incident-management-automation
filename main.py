"""
Módulo principal da automação de incidentes.

Responsável por orquestrar os fluxos de registro e finalização
de incidentes, integrando os módulos de interface, Qualitor,
geração de evidências, armazenamento de dados e envio de e-mails.

Fluxos disponíveis:
- Registro de incidente
- Finalização de incidente

As comunicações enviadas ao final dos processos são utilizadas
para dar continuidade à automação através do Power Automate.
"""

import json
import os
import time
from frontend.screen import selecionar_acao
from frontend.screen import abrir_interface_de_registro
from frontend.screen import abrir_interface_de_encerramento
from backend.gerar_screenshots.geral_function import gerar_screenshot
from backend.email.envio_email import enviar_email, fecha_email
from backend.qualitor.abertura_chamado import pega_chamado
from backend.path_utils import get_path
from backend.logger_config import configurar_logger
from backend.qualitor.encerra_chamado import fecha_chamado


def registrar():
    """
    Orquestra o fluxo de registro de um novo incidente.
    
    Etapas:
    1. Inicializa o logger.
    2. Coleta as informações do incidente pela interface.
    3. Obtém o chamado.
    4. Persiste os dados em info_incidente.json.
    5. Gera as evidências do incidente.
    6. Envia o e-mail de registro.
    
    A execução é interrompida caso o usuário cancele
    o preenchimento das informações.
    """
    inicio = time.time()

    output_dir = os.path.join(os.getcwd(), "output")

    logger = configurar_logger(output_dir)


    logger.info("=" * 60)
    logger.info("Iníciando automação...")

    # Coleta dados
    info_incidente = abrir_interface_de_registro()

    # Usuário cancelou ou fechou a janela
    if not info_incidente:
        logger.info("Operação cancelada pelo usuário.")
        return

    chamado = pega_chamado()

    # Salva em JSON para reuso
    file_path = get_path(os.path.join("data", "info_incidente.json"))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(info_incidente, f, ensure_ascii=False, indent=4)

    # Gera screenshots
    gerar_screenshot()

    # Envia email
    enviar_email(chamado)


    fim = time.time()
    logger.info(f"Execução de registrar incidente finalizada em {(fim - inicio):.2f} segundos.")
    logger.info("Fim da execução.")
    logger.info("=" * 60)



def finalizar():
    """
    Orquestra o fluxo de finalização de um incidente.

    Etapas:
        1. Inicializa o logger.
        2. Coleta as informações de encerramento pela interface.
        3. Persiste os dados em info_incidente.json.
        4. Executa o encerramento do chamado.
        5. Envia o e-mail de normalização/finalização.

    A execução é interrompida caso o usuário cancele
    o preenchimento das informações.
    """
    inicio = time.time()

    output_dir = os.path.join(os.getcwd(), "output")

    logger = configurar_logger(output_dir)


    info_incidente = abrir_interface_de_encerramento()

    if not info_incidente:
        logger.info("Operação cancelada pelo usuário.")
        return

    file_path = get_path(os.path.join("data", "info_incidente.json"))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(info_incidente, f, ensure_ascii=False, indent=4)

    fecha_chamado()

    fecha_email()


    fim = time.time()
    logger.info(f"Execução de encerrar incidente finalizada em {(fim - inicio):.2f} segundos.")
    logger.info("Fim da execução.")
    logger.info("=" * 60)


def main():
    """
    Executa o fluxo principal da aplicação.

    Solicita ao usuário a operação desejada e direciona
    a execução para o registro ou finalização do incidente.

    Também realiza o tratamento global de exceções e registra
    o tempo total de execução da automação.
    """
    inicio = time.time()

    output_dir = os.path.join(os.getcwd(), "output")

    logger = configurar_logger(output_dir)

    acao_incidente = selecionar_acao()

    try:
        if acao_incidente == "registrar":
            registrar()
        elif acao_incidente == "finalizar":
            finalizar()
        else:
            logger.info("Nenhuma das opções foram selecionadas corretamente.")
    except Exception:
        logger.exception("Erro na execução: ")

    fim = time.time()
    logger.info(f"Execução geral finalizada em {(fim - inicio):.2f} segundos.")
    logger.info("Fim da execução.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()



