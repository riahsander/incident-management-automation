"""
screenshot_trans.py

Módulo responsável pela captura automatizada de gráficos transacionais.

Através do Playwright, o módulo realiza autenticação na plataforma
de monitoramento, localiza o gráfico correspondente à operadora
informada e gera uma evidência visual em formato PNG.

As imagens geradas são utilizadas posteriormente nas comunicações
e análises do incidente.

Funcionalidades:
    - Acesso automatizado à plataforma.
    - Autenticação utilizando credenciais configuradas.
    - Busca dinâmica da operadora informada.
    - Captura de screenshot do gráfico.
    - Armazenamento organizado das evidências.

Dependências:
    - Playwright
    - python-dotenv

Variáveis de ambiente:
    - TRANSACIONAL_GRAF
    - USER
    - PASSWORD

Saída:
    Arquivos PNG contendo os gráficos da operadora selecionada.
"""

import os, sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import re
from backend.path_utils import get_output_path  # para salvar prints corretamente

load_dotenv()
transacional_graf = os.getenv("TRANSACIONAL_GRAF")
user = os.getenv("USER")
password = os.getenv("PASSWORD")


def print_grafico(operadora, pasta_saida):
    """
    Captura o gráfico transacional de uma operadora e salva a
    evidência em formato PNG.
     
    A função acessa automaticamente a plataforma de monitoramento,
    realiza autenticação, localiza o gráfico correspondente à
    operadora solicitada e gera uma captura de tela do componente.
     
    Args:
    operadora (str):
    Nome da operadora cujo gráfico será capturado.
     
    pasta_saida (str):
    Diretório onde a imagem será armazenada.
     
    Fluxo:
    1. Inicia o navegador Chromium.
    2. Acessa a plataforma de monitoramento.
    3. Realiza login utilizando credenciais configuradas.
    4. Localiza o gráfico da operadora.
    5. Captura a evidência visual.
    6. Salva a imagem em formato PNG.
     
    Arquivos gerados:
    <operadora>.png
     
    Exemplo:
     
    print_grafico(
    operadora="BANCO_HORIZONTE",
    pasta_saida="screenshots"
    )
     
    Returns:
    None
     
    Observação:
    O diretório informado é criado automaticamente caso não exista.
"""
    """Gera o print do gráfico da operadora e salva no arquivo correto dentro da pasta de saída."""
    with sync_playwright() as p:
        # Determina o caminho do navegador Chromium utilizado pelo Playwright.
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        chromium_path = os.path.join(base_path, "chromium-1234", "chrome-win64", "chrome.exe")

        browser = p.chromium.launch(executable_path=chromium_path)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(transacional_graf)

        # Realiza autenticação na plataforma de monitoramento.
        page.fill("input[name='user']", user)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        # Oculta o menu lateral para maximizar a área do gráfico.
        botao_fechar_aba_lateral = page.locator("#dock-menu-button")
        botao_fechar_aba_lateral.click()
        page.wait_for_selector("section", state="visible", timeout=5000)

        try:
            # Busca o painel que contém o gráfico da operadora informada.
            card_grafico = page.locator("section").filter(
                has=page.locator("h2", has_text=re.compile(fr"^\s*{operadora}\s*$", re.IGNORECASE))
            )
            card_grafico.wait_for(state="visible", timeout=10000)
            card_grafico.scroll_into_view_if_needed()

            # Obtém o diretório de saída e monta o caminho final da imagem.
            pasta_saida = get_output_path(pasta_saida)  # garante que a pasta exista
            filename = f"{operadora}.png"
            full_path = os.path.join(pasta_saida, filename)

            # Garante que o arquivo seja salvo com a extensão PNG.
            if not full_path.lower().endswith(".png"):
                full_path += ".png"

            # Captura e salva a evidência visual do gráfico.
            card_grafico.screenshot(path=full_path)
            print(f"Arquivo salvo em: {full_path}")

        except Exception as e:
            print(f"ERRO ao tirar print do gráfico da operadora {operadora}: {e}")

        browser.close()
