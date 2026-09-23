"""
Automação de abertura de chamados no Qualitor.

O módulo utiliza Playwright para acessar o Qualitor e registrar um
novo incidente com base nas informações armazenadas em
data/info_incidente.json.

Responsabilidades:
    - Carregar as credenciais e configurações do ambiente.
    - Ler as informações do incidente.
    - Aplicar regras de conversão necessárias ao formulário.
    - Autenticar no Qualitor.
    - Preencher os dados do incidente.
    - Registrar os status transacionais correspondentes.
    - Processar a abertura do chamado.
    - Capturar e retornar o número do chamado criado.
"""

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from backend.path_utils import get_path
import os, sys
import json
from backend.logger_config import logger

load_dotenv()
qualitor = os.getenv("QUALITOR")
user = os.getenv("USER")
password = os.getenv("PASSWORD")


def marcar_status(pagina, lista):
    """
    Seleciona no formulário do Qualitor os status das transações.

    O status recebido através dos dados do incidente é convertido
    para os respectivos campos disponíveis no formulário do Qualitor.

    Status suportados:
        - Negadas
        - Pendentes
        - Desfeitas
        - Erro
        - Negadas e Pendentes
        - Desfeitas e Pendentes

    Args:
        pagina: Página Playwright utilizada para interação com o Qualitor.
        lista (dict): Dados do incidente contendo a chave "status".

    Returns:
        None
    """
    if lista['status'] == "Negadas":
        pagina.click("label[for='Status_3']")
    elif lista['status'] == "Pendentes":
        pagina.click("label[for='Status_2']")
    elif lista['status'] == "Desfeitas":
        pagina.click("label[for='Status_1']")
    elif lista['status'] == "Erro":
        pagina.click("label[for='Status_4']")
    elif lista['status'] == "Negadas e Pendentes":
        pagina.click("label[for='Status_3']")
        pagina.click("label[for='Status_2']")
    elif lista['status'] == "Desfeitas e Pendentes":
        pagina.click("label[for='Status_2']")
        pagina.click("label[for='Status_1']")

def pega_chamado():
    """
    Realiza a abertura de um chamado de incidente no Qualitor.

    O processo lê as informações armazenadas em
    data/info_incidente.json, autentica no Qualitor através
    do Playwright e preenche o formulário de abertura.

    Durante o preenchimento são aplicadas as conversões necessárias
    para parceiro, indisponibilidade e status das transações.

    Após o processamento, o número do chamado criado é capturado
    e retornado para o fluxo principal da automação.

    Returns:
        str: Número do chamado criado no Qualitor.
    """
    logger.info("Inciando abertura de chamado no Qualitor.")
    try:
        # Lê os dados do incidente
        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "r", encoding="utf-8") as o:
            lista_operadoras = json.load(o)

        # Ajusta nome da operadora
        if lista_operadoras["parceiro"] == "PARCEIRO_EXEMPLO":
            operadora = "OPERADORA_EXEMPLO"
        else:
            operadora = lista_operadoras["parceiro"]

        # Ajusta indisponibilidade
        indisponibilidade = "Sim" if lista_operadoras['indisponibilidade'] == "Total" else "N"

        # Lança navegador
        with sync_playwright() as p:
            # Ajusta caminho do Chromium
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS

                chromium_path = os.path.join(
                    base_path,
                    "chromium-1234",
                    "chrome-win64",
                    "chrome.exe"
                )

                browser = p.chromium.launch(executable_path=chromium_path)

            else:
                browser = p.chromium.launch()

            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(qualitor)

            # Login
            logger.info("Iniciando Login no Qualitor...")
            page.fill("input[placeholder='Usuário']", user)
            page.press("input[name='cdusuario']", "Tab")
            page.click("#cdsenha.input")
            page.wait_for_selector("#cdsenha:not([disabled])")
            page.fill("input[placeholder='Senha']", password)
            page.click("#btnLogin")
            page.wait_for_timeout(2000)
            page.wait_for_load_state("networkidle")
            logger.info("Sucesso no Login.")

            # Preenche formulário
            page.goto(qualitor)
            page.wait_for_timeout(1000)
            page.select_option("#Parceiro", value=operadora)
            page.select_option("#ConexaoAutorizador", value=lista_operadoras['autorizador'])
            page.select_option("#indisp", value=indisponibilidade)
            marcar_status(page, lista_operadoras)
            page.fill("#HoraInicio", lista_operadoras['hora_inicio'])
            page.fill('#dschamado', f"Transações {lista_operadoras['status']} com o parceiro {lista_operadoras['parceiro']}\nTipo da transação: {lista_operadoras['tipo_transacao']}.")

            # Espera 1 segundo
            page.wait_for_timeout(1000)
        
            # Clica em Processar
            page.locator("button[title='Processar']").click()

            page.wait_for_timeout(1000)

            # Aguarda o modal de confirmação aparecer
            page.wait_for_selector("td.COLORLABEL b")

            # # Captura o número do chamado
            chamado = page.locator("td.COLORLABEL b").inner_text().strip()

            page.click('#btnNO')

            page.wait_for_timeout(3000)

            browser.close()
            logger.info(f"Chamado aberto com sucesso. Chamado {chamado}")
            return chamado
    except Exception:
        logger.exception("Erro ao abrir o chamado.")
 
