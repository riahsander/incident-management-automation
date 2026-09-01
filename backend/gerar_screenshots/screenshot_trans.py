"""
screenshot_trans.py

Módulo responsável pela captura automatizada de gráficos transacionais.

Utilizando Playwright, o módulo acessa a plataforma de monitoramento,
realiza autenticação e captura screenshots dos gráficos associados
à operadora informada.

As evidências geradas auxiliam na análise do comportamento das
transações e são utilizadas posteriormente nas comunicações de
incidentes.

Funcionalidades:
    - Acesso automatizado à plataforma de monitoramento.
    - Autenticação utilizando credenciais configuradas.
    - Localização dinâmica do gráfico da operadora.
    - Captura do painel gráfico.
    - Armazenamento da evidência em formato PNG.

Dependências:
    - Playwright
    - python-dotenv

Variáveis de ambiente:
    - TRANSACIONAL_GRAF
    - USER
    - PASSWORD

Saída:
    Arquivos PNG contendo os gráficos transacionais da operadora.
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
    Captura o gráfico transacional associado a uma operadora.
     
    A função acessa a plataforma de monitoramento, realiza login,
    localiza o gráfico correspondente à operadora informada e gera
    uma captura de tela da evidência.
     
    Args:
    operadora (str):
    Nome da operadora utilizada na busca do gráfico.
     
    pasta_saida (str):
    Diretório onde a evidência será armazenada.
     
    Fluxo:
    1. Inicializa o navegador Chromium.
    2. Acessa a plataforma de monitoramento.
    3. Realiza autenticação.
    4. Localiza o gráfico da operadora.
    5. Aguarda a exibição do componente.
    6. Captura a evidência gráfica.
    7. Salva a imagem em formato PNG.
     
    Arquivos gerados:
    <operadora>.png
     
    Exemplo:
     
    print_grafico(
    operadora="TRANSACOES_PIX",
    pasta_saida="output/printGraf"
    )
     
    Returns:
    None
     
    Raises:
    Exception:
    Exibe mensagem de erro caso o gráfico não seja
    encontrado ou ocorra falha durante a captura.
     
    Observação:
    O diretório de saída é criado automaticamente caso não exista.
    """
    """Gera o print do gráfico da operadora e salva no arquivo correto dentro da pasta de saída."""
    with sync_playwright() as p:
        # Ajusta caminho do Chromium
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS

            chromium_path = os.path.join(base_path, "chromium-1234", "chrome-win64", "chrome.exe")

            browser = p.chromium.launch(executable_path=chromium_path)
        else:
            browser = p.chromium.launch()

        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(transacional_graf)

        # Login
        page.fill("input[name='user']", user)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        # Fecha aba lateral
        botao_fechar_aba_lateral = page.locator("#dock-menu-button")
        botao_fechar_aba_lateral.click()
        page.wait_for_selector("section", state="visible", timeout=5000)

        try:
            # Localiza card do gráfico
            card_grafico = page.locator("section").filter(
                has=page.locator("h2", has_text=re.compile(fr"^\s*{operadora}\s*$", re.IGNORECASE))
            )
            card_grafico.wait_for(state="visible", timeout=10000)
            card_grafico.scroll_into_view_if_needed()

            # Ajusta caminho de saída (arquivo completo, não pasta)
            pasta_saida = get_output_path(pasta_saida)  # garante que a pasta exista
            filename = f"{operadora}.png"
            full_path = os.path.join(pasta_saida, filename)

            # Garante que o caminho termina com .png
            if not full_path.lower().endswith(".png"):
                full_path += ".png"

            # Salva o print diretamente no arquivo
            card_grafico.screenshot(path=full_path)
            print(f"Arquivo salvo em: {full_path}")

        except Exception as e:
            print(f"ERRO ao tirar print do gráfico da operadora {operadora}: {e}")

        browser.close()
