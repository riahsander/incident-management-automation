"""
geral_function.py

Módulo responsável pela orquestração da geração de evidências do incidente.

A partir das informações registradas pelo usuário, o módulo identifica
a operadora afetada e coordena a captura das evidências utilizadas nas
análises e comunicações do incidente.

Funcionalidades:
    - Leitura dos dados do incidente.
    - Geração de evidências operacionais.
    - Geração de evidências operacionais detalhadas.
    - Geração de evidências transacionais.
    - Atualização do arquivo do incidente com os caminhos dos arquivos gerados.

Arquivos utilizados:
    - data/info_incidente.json
    - data/operadoras.json

Arquivos gerados:
    - output/printOP/*.png
    - output/printOP_detalhado/*.png
    - output/printGraf/*.png

Dependências internas:
    - screenshot_op.py
    - screenshot_detalhado.py
    - screenshot_trans.py
    - path_utils.py

Fluxo:
    Incidente → Captura de Evidências → Atualização dos Dados → Comunicação
"""

import json
import os
from backend.gerar_screenshots.screenshot_op import print_operadora
from backend.gerar_screenshots.screenshot_trans import print_grafico
from backend.path_utils import get_path, get_output_path
from backend.gerar_screenshots.screenshot_detalhado import print_opdetalhado

file_path = get_path(os.path.join("data", "operadoras.json"))
with open(file_path, "r", encoding="utf-8") as f:
    grafico_operadora = json.load(f)

def gerar_screenshot():
    """
    Gera todas as evidências visuais associadas ao incidente.
     
    A função recupera os dados registrados no incidente, identifica
    a operadora selecionada e executa os módulos responsáveis pela
    captura das evidências operacionais, operacionais detalhadas e
    transacionais.
     
    Fluxo:
    1. Carrega os dados do incidente.
    2. Identifica a operadora informada.
    3. Gera a evidência operacional.
    4. Gera a evidência operacional detalhada.
    5. Verifica se existe gráfico associado à operadora.
    6. Gera a evidência transacional.
    7. Atualiza o arquivo do incidente com os caminhos das
    evidências produzidas.
     
    Evidências geradas:
    - print_operadora
    - print_op_detalhado
    - print_grafico
     
    Diretórios utilizados:
    - output/printOP
    - output/printOP_detalhado
    - output/printGraf
     
    Exemplo de atualização:
     
    {
    "parceiro": "BANCO_HORIZONTE",
    "print_operadora":
    "output/printOP/BANCO_HORIZONTE.png",
    "print_op_detalhado":
    "output/printOP_detalhado/BANCO_HORIZONTE_detalhado.png",
    "print_grafico":
    "output/printGraf/Transacoes PIX.png"
    }
     
    Returns:
    None
     
    Raises:
    Exception:
    Exibe mensagens de erro caso ocorra alguma falha durante
    a geração das evidências.
    """
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

    except Exception as e:
        print("ERRO:", e)
