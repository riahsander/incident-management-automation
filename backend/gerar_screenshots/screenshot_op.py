"""
Captura de evidência do card principal da operadora.

O módulo utiliza Playwright para acessar o monitoramento de operadoras,
localizar o card correspondente ao parceiro do incidente e gerar uma
captura de tela do componente.

A imagem resultante é armazenada no diretório de evidências definido
pelo fluxo principal.
"""

import os, sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import re
from backend.path_utils import get_output_path
from backend.logger_config import logger

load_dotenv()
mon_operadoras = os.getenv("MON_OPERADORAS")
user = os.getenv("USER")
password = os.getenv("PASSWORD")


def print_operadora(operadora, pasta_saida):
    """
    Captura o card principal de uma operadora.

    A função acessa o monitoramento de operadoras, autentica no sistema,
    localiza o card correspondente e salva uma captura de tela.

    Args:
        operadora (str): Nome da operadora que será localizada.
        pasta_saida (str): Diretório onde a imagem será armazenada.

    Returns:
        None
    """
    logger.info("Capturando evidências do Transacional Operadoras")
    try:
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

            # Login
            page.goto(mon_operadoras)
            page.fill("input[name='user']", user)
            page.fill("input[name='password']", password)
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")

            # Fecha aba lateral
            botao = page.locator("#dock-menu-button")
            botao.click()

            page.wait_for_selector(".card-operadora .card-header")

            try:
                # Localiza card da operadora
                operadora_card = page.locator(".card-operadora").filter(
                    has=page.locator(".card-header", has_text=re.compile(fr"^\s*{operadora}\s*$", re.IGNORECASE))
                )

                operadora_card.wait_for(state="visible", timeout=10000)
                operadora_card.scroll_into_view_if_needed()

                # Ajusta caminho de saída (arquivo completo, não pasta)
                pasta_saida = get_output_path(pasta_saida)  # garante que a pasta exista
                filename = f"{operadora}.png"
                fullpath = os.path.join(pasta_saida, filename)

                # Garante que termina com .png
                if not fullpath.lower().endswith(".png"):
                    fullpath += ".png"

                # Salva o print diretamente no arquivo
                operadora_card.screenshot(path=fullpath)
                logger.info(f"Arquivo salvo em: {fullpath}")
                print(f"Arquivo salvo em: {fullpath}")

            except Exception:
                logger.exception(f"Card {operadora} não encontrado ou erro ao tirar print.")

            browser.close()
    except Exception:
        logger.exception('Erro ao gerar screenshot de Operadoras.')