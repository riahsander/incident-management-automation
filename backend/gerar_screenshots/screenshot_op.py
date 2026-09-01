"""
screenshot_op.py

Módulo responsável pela captura automatizada de evidências operacionais.

Utilizando Playwright, o módulo acessa a plataforma de monitoramento,
realiza autenticação e captura screenshots dos cards operacionais
associados à operadora informada.

As imagens geradas são utilizadas como evidências em análises,
investigações e comunicações relacionadas ao incidente.

Funcionalidades:
    - Acesso automatizado à plataforma de monitoramento.
    - Autenticação utilizando credenciais configuradas.
    - Identificação dinâmica da operadora.
    - Captura do card operacional correspondente.
    - Armazenamento da evidência em formato PNG.

Dependências:
    - Playwright
    - python-dotenv

Variáveis de ambiente:
    - MON_OPERADORAS
    - USER
    - PASSWORD

Saída:
    Arquivos PNG contendo a visão operacional da operadora.
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
    Captura o card operacional de uma operadora.
     
    A função acessa automaticamente a plataforma de monitoramento,
    realiza autenticação, localiza o card correspondente à operadora
    informada e gera uma captura de tela da evidência.
     
    Args:
    operadora (str):
    Nome da operadora que será localizada na plataforma.
     
    pasta_saida (str):
    Diretório onde a captura será armazenada.
     
    Fluxo:
    1. Inicializa o navegador Chromium.
    2. Acessa a plataforma de monitoramento.
    3. Realiza autenticação.
    4. Localiza o card da operadora.
    5. Aguarda a exibição do componente.
    6. Captura a evidência operacional.
    7. Salva a imagem em formato PNG.
     
    Arquivos gerados:
    <operadora>.png
     
    Exemplo:
     
    print_operadora(
    operadora="BANCO_HORIZONTE",
    pasta_saida="output/printOP"
    )
     
    Returns:
    None
     
    Raises:
    Exception:
    Exibe mensagem de erro caso a operadora não seja
    encontrada ou ocorra falha durante a captura.
     
    Observação:
    O diretório de saída é criado automaticamente caso não exista.
    """
    """Gera o print da operadora e salva no arquivo correto dentro da pasta de saída."""
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
            print(f"Arquivo salvo em: {fullpath}")

        except Exception as e:
            print(f"Card {operadora} não encontrado ou erro ao tirar print: {e}")

        browser.close()
