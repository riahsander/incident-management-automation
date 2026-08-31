"""
screenshot_op.py

Módulo responsável pela captura automatizada de evidências operacionais.

Utilizando o Playwright, o módulo acessa a plataforma de monitoramento,
realiza autenticação e captura screenshots dos cards operacionais
correspondentes à operadora informada.

As imagens geradas são utilizadas como evidências em comunicações,
análises e registros de incidentes.

Funcionalidades:
    - Acesso automatizado à plataforma de monitoramento.
    - Autenticação utilizando credenciais configuradas.
    - Busca dinâmica da operadora selecionada.
    - Captura de screenshots dos cards operacionais.
    - Armazenamento das evidências em formato PNG.

Dependências:
    - Playwright
    - python-dotenv

Variáveis de ambiente:
    - MON_OPERADORAS
    - USER
    - PASSWORD

Saída:
    Arquivos PNG contendo os cards operacionais capturados.
"""

import os, sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import re
from backend.path_utils import get_output_path  # para salvar prints corretamente

load_dotenv()
mon_operadoras = os.getenv("MON_OPERADORAS")
user = os.getenv("USER")
password = os.getenv("PASSWORD")


def print_operadora(operadora, pasta_saida):
    """
    Captura o card operacional de uma operadora e salva a
    evidência em formato PNG.
     
    A função acessa a plataforma de monitoramento, realiza login,
    localiza o card correspondente à operadora informada e gera
    uma captura de tela do componente.
     
    Args:
    operadora (str):
    Nome da operadora que será localizada na plataforma.
     
    pasta_saida (str):
    Diretório onde a imagem será armazenada.
     
    Fluxo:
    1. Inicia o navegador Chromium.
    2. Abre a plataforma de monitoramento.
    3. Realiza autenticação.
    4. Localiza o card da operadora.
    5. Captura a evidência visual.
    6. Salva o arquivo em formato PNG.
     
    Arquivos gerados:
    <operadora>.png
     
    Exemplo:
     
    print_operadora(
    operadora="BANCO_HORIZONTE",
    pasta_saida="evidencias"
    )
     
    Returns:
    None
     
    Observação:
    O diretório de saída é criado automaticamente caso não exista.
    """
    """Gera o print da operadora e salva no arquivo correto dentro da pasta de saída."""
    with sync_playwright() as p:
        # Define o caminho do navegador Chromium utilizado pelo Playwright.
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        chromium_path = os.path.join(base_path, "chromium-1234", "chrome-win64", "chrome.exe")

        browser = p.chromium.launch(executable_path=chromium_path)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        # Realiza autenticação na plataforma de monitoramento.
        page.goto(mon_operadoras)
        page.fill("input[name='user']", user)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        # Oculta o menu lateral para facilitar a visualização dos cards.
        botao = page.locator("#dock-menu-button")
        botao.click()

        page.wait_for_selector(".card-operadora .card-header")

        try:
            # Procura o card operacional da operadora informada.
            operadora_card = page.locator(".card-operadora").filter(
                has=page.locator(".card-header", has_text=re.compile(fr"^\s*{operadora}\s*$", re.IGNORECASE))
            )

            operadora_card.wait_for(state="visible", timeout=10000)
            operadora_card.scroll_into_view_if_needed()

            # Monta o caminho completo para armazenamento da evidência.
            pasta_saida = get_output_path(pasta_saida)  # garante que a pasta exista
            filename = f"{operadora}.png"
            fullpath = os.path.join(pasta_saida, filename)

           # Garante que o arquivo será salvo com extensão PNG.
            if not fullpath.lower().endswith(".png"):
                fullpath += ".png"

            # Captura e salva a evidência visual do card operacional.
            operadora_card.screenshot(path=fullpath)
            print(f"Arquivo salvo em: {fullpath}")

        except Exception as e:
            print(f"Card {operadora} não encontrado ou erro ao tirar print: {e}")

        browser.close()
