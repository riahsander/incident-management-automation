import os, sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import re
from backend.path_utils import get_output_path  # para salvar prints corretamente

load_dotenv()
mon_operadoras = os.getenv("MON_OPERADORAS")
user = os.getenv("USER")
password = os.getenv("PASSWORD")


def print_opdetalhado(operadora, pasta_saida):
    with sync_playwright() as p:
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
        page.set_viewport_size({"width": 2800, "height": 1600})

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

            with page.expect_popup() as popup_transacoes:
                operadora_card.get_by_text("TOTAL", exact=True).click()

            print("Aguardando popup...")
            aba_op_detalhada = popup_transacoes.value

            print("Aguardando carregamento...")
            aba_op_detalhada.wait_for_load_state("networkidle")

            print("Diminuindo a tela")
            aba_op_detalhada.evaluate(""" document.body.style.zoom = '70%' """)

            print("Aguardando painel...")
            aba_op_detalhada.wait_for_selector(".css-1wux2l8", state="visible",timeout=5000)

            print("Painel encontrado...")
            container = aba_op_detalhada.locator(".css-1wux2l8").first

            aba_op_detalhada.wait_for_timeout(3000)

            # Ajusta caminho de saída (arquivo completo, não pasta)
            pasta_saida = get_output_path(pasta_saida)  # garante que a pasta exista
            filename = f"{operadora}_detalhado.png"
            fullpath = os.path.join(pasta_saida, filename)

            # Garante que termina com .png
            if not fullpath.lower().endswith(".png"):
                fullpath += ".png"

            # Salva o print diretamente no arquivo
            container.screenshot(path=fullpath)
            print(f"Arquivo salvo em: {fullpath}")

        except Exception as e:
            print(f"Card {operadora} não encontrado ou erro ao tirar print: {e}")

        browser.close()

