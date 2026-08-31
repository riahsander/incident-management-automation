"""
geral_function.py

Módulo responsável pela geração e gerenciamento das evidências
utilizadas no fluxo de tratamento de incidentes.

A partir das informações registradas pelo usuário, o módulo
identifica a operadora envolvida, gera as capturas de tela
necessárias e atualiza o arquivo de incidente com os caminhos
das evidências produzidas.

Funcionalidades:
    - Carregamento das configurações de operadoras.
    - Leitura das informações do incidente.
    - Geração de evidências operacionais.
    - Geração de evidências transacionais.
    - Atualização do arquivo de dados do incidente.

Arquivos utilizados:
    - data/operadoras.json
    - data/info_incidente.json

Arquivos gerados:
    - printOP/*.png
    - printGraf/*.png

Dependências internas:
    - screenshot_op.py
    - screenshot_trans.py
    - path_utils.py
"""

import json
import os
from backend.gerar_screenshots.screenshot_op import print_operadora
from backend.gerar_screenshots.screenshot_trans import print_grafico
from backend.path_utils import get_path, get_output_path

file_path = get_path(os.path.join("data", "operadoras.json"))
with open(file_path, "r", encoding="utf-8") as f:
    grafico_operadora = json.load(f)

def gerar_screenshot():
    """
    Gera todas as evidências visuais relacionadas ao incidente.
     
    A função recupera as informações registradas pelo usuário,
    identifica a operadora afetada e executa os módulos
    responsáveis pela captura das evidências operacionais e
    transacionais.
     
    Fluxo:
    1. Carrega os dados do incidente.
    2. Identifica a operadora selecionada.
    3. Gera o screenshot operacional.
    4. Verifica a existência de gráfico associado.
    5. Gera o screenshot transacional.
    6. Atualiza o arquivo do incidente com os caminhos
    das evidências geradas.
     
    Atualizações realizadas:
    - print_operadora
    - print_grafico
     
    Exemplo de atualização:
     
    {
    "parceiro": "BANCO_HORIZONTE",
    "print_operadora": "printOP/BANCO_HORIZONTE.png",
    "print_grafico": "printGraf/Transacoes PIX.png"
    }
     
    Returns:
    None
     
    Raises:
    Exception:
    Exibe mensagem de erro no console caso ocorra alguma
    falha durante a geração das evidências.
    """
    file_info = get_path(os.path.join("data", "info_incidente.json"))
    with open(file_info, "r", encoding="utf-8") as f:
        info_incidente = json.load(f)

    operadora = info_incidente.get("parceiro", "DESCONHECIDO")

    try:
        # Cria ou recupera os diretórios destinados ao armazenamento das evidências.
        pasta_print_op = get_output_path("printOP")
        pasta_print_graf = get_output_path("printGraf")

        # Gera a evidência operacional da operadora selecionada.       
        print_operadora(operadora, pasta_print_op)
        info_incidente["print_operadora"] = os.path.join(pasta_print_op, f"{operadora}.png")

        # Gera a evidência transacional associada à operadora, quando disponível.
        if operadora in grafico_operadora:
            grafico_nome = grafico_operadora[operadora]
            print_grafico(grafico_nome, pasta_print_graf)
            info_incidente["print_grafico"] = os.path.join(pasta_print_graf, f"{grafico_nome}.png")

        # Registra no incidente os caminhos dos arquivos gerados.
        with open(file_info, "w", encoding="utf-8") as f:
            json.dump(info_incidente, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print("ERRO:", e)
