"""
Orquestração da geração de evidências do incidente.

O módulo coordena as rotinas responsáveis pela captura das evidências
utilizadas durante o registro de um incidente.

Responsabilidades:
    - Ler as informações do incidente.
    - Identificar o parceiro relacionado ao incidente.
    - Preparar os diretórios de saída das evidências.
    - Gerar a captura do card da operadora.
    - Gerar a captura detalhada das transações.
    - Gerar o gráfico transacional quando disponível.
    - Registrar os caminhos das evidências em info_incidente.json.

As evidências geradas são posteriormente utilizadas por outros
componentes da automação.
"""

import json
import os
from backend.gerar_screenshots.screenshot_op import print_operadora
from backend.gerar_screenshots.screenshot_trans import print_grafico
from backend.path_utils import get_path, get_output_path
from backend.gerar_screenshots.screenshot_detalhado import print_opdetalhado
from backend.logger_config import logger


file_path = get_path(os.path.join("data", "operadoras.json"))
with open(file_path, "r", encoding="utf-8") as f:
    grafico_operadora = json.load(f)

def gerar_screenshot():
    """
    Coordena a geração das evidências associadas ao incidente.

    A função lê o parceiro armazenado em info_incidente.json e executa
    as rotinas de captura disponíveis para a operadora.

    Evidências geradas:
        - Card da operadora.
        - Detalhamento transacional da operadora.
        - Gráfico transacional, quando configurado para o parceiro.

    Após as capturas, os caminhos dos arquivos gerados são adicionados
    ao arquivo data/info_incidente.json.

    Returns:
        None
    """
    logger.info("Iniciando a criação de evidências...")
    file_info = get_path(os.path.join("data", "info_incidente.json"))
    with open(file_info, "r", encoding="utf-8") as f:
        info_incidente = json.load(f)

    operadora = info_incidente.get("parceiro", "DESCONHECIDO")

    try:
        # Usa get_output_path para garantir que as pastas existam
        pasta_print_op = get_output_path(os.path.join("output", "printOP"))
        pasta_print_graf = get_output_path(os.path.join("output", "printGraf"))
        pasta_print_OPdetalhado = get_output_path(os.path.join("output", "printOP_detalhado"))

        # Gera print da operadora
        print_operadora(operadora, pasta_print_op)
        info_incidente["print_operadora"] = os.path.join(pasta_print_op, f"{operadora}.png")

        # Gera print das transações detalhado
        print_opdetalhado(operadora, pasta_print_OPdetalhado)
        info_incidente["print_op_detalhado"] = os.path.join(pasta_print_OPdetalhado, f"{operadora}_detalhado.png")

        # Gera print do gráfico (se existir)
        if operadora in grafico_operadora:
            grafico_nome = grafico_operadora[operadora]
            print_grafico(grafico_nome, pasta_print_graf)
            info_incidente["print_grafico"] = os.path.join(pasta_print_graf, f"{grafico_nome}.png")

        # Atualiza JSON com os caminhos dos prints
        with open(file_info, "w", encoding="utf-8") as f:
            json.dump(info_incidente, f, ensure_ascii=False, indent=4)

    except Exception:
        logger.exception("ERRO na geração de evidências.")

