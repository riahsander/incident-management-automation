"""
Automação de encerramento de chamados no Qualitor.

O módulo utiliza Playwright para localizar e encerrar um chamado
existente com base nas informações armazenadas em
data/info_incidente.json.

Responsabilidades:
    - Carregar as configurações e credenciais do ambiente.
    - Autenticar no Qualitor.
    - Localizar o chamado informado pelo usuário.
    - Acessar o atendimento correspondente.
    - Capturar informações complementares do chamado.
    - Atualizar os dados do incidente.
    - Executar o cálculo da perda média transacional.
    - Preencher as informações de atendimento.
    - Encerrar o chamado no Qualitor.
"""

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from backend.path_utils import get_path
import os, sys
import json
from backend.logger_config import logger
from datetime import datetime
from backend.avg_transacional.avg_perda import calcula_perda

load_dotenv()
qualitor = os.getenv("QUALITOR")
user = os.getenv("USER")
password = os.getenv("PASSWORD")

def fecha_chamado():
    """
    Executa o processo automatizado de encerramento de um chamado.

    O processo lê o número do chamado armazenado nos dados do
    incidente, autentica no Qualitor, localiza o atendimento e
    acessa o formulário correspondente.

    Durante o processamento, informações adicionais do chamado são
    capturadas e adicionadas ao arquivo info_incidente.json. Em seguida,
    é realizado o cálculo da perda média transacional e os dados
    necessários para o encerramento são preenchidos no Qualitor.

    Informações capturadas do Qualitor:
        - Parceiro
        - Data de abertura
        - Hora de início

    Informações complementadas pela automação:
        - Data de finalização
        - Perda média transacional

    Returns:
        None
    """
    logger.info("Inciando encerramento de chamado no Qualitor.")
    # Lê os dados do incidente
    try:
        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "r", encoding="utf-8") as o:
            info_incidente = json.load(o)

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
                browser = p.chromium.launch(headless=False)
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

            # Pesquisa no Qualitor o chamado
            campo_chamado = page.locator('#dsconteudolocalizacao')
            campo_chamado.click()
            campo_chamado.fill(info_incidente['chamado'])
            page.wait_for_timeout(1000)
            page.locator("i.fas.fa-search.fill").click()
            logger.info(f"Chamado {info_incidente['chamado']} encontrado")

            # Pegamos o ID do chamado (1454474) dinamicamente e montamos o comando exato que o botão executaria
            id_chamado = info_incidente['chamado']

            logger.info("Disparando comando direto via JS.")
            
            # Executa a função nativa do Qualitor em todos os contextos (ignora barreiras de frames)
            with page.expect_popup() as popup_chamado:
                page.evaluate(f"""
                    () => {{
                        // Procura a função na página principal ou em qualquer frame ativo e a executa
                        const executar = (win) => {{
                            if (typeof win.openChamado === 'function') {{
                                win.openChamado(win.decodificarHTML('{id_chamado}%2CC'));
                                return true;
                            }}
                            for (let i = 0; i < win.frames.length; i++) {{
                                try {{
                                    if (executar(win.frames[i])) return true;
                                }} catch(e) {{}}
                            }}
                            return false;
                        }};
                        executar(window);
                    }}
                """)

            aba_chamado = popup_chamado.value
            aba_chamado.locator('#btnNextEtapa').click()

            try:
                # --- CAPTURA DE INFORMAÇÕES DO CHAMADO ---
                logger.info("Iniciando a captura dos dados adicionais no formulário...")

                # 1. Capturar o campo "Parceiro"
                campo_parceiro = aba_chamado.locator("#vlinformacaoadicional2517")
                campo_parceiro.scroll_into_view_if_needed()
                parceiro_valor = campo_parceiro.input_value()
                logger.info(f"Parceiro capturado: {parceiro_valor}")


                # 2. Capturar o campo "Hora de Início"
                campo_hora = aba_chamado.locator("#vlinformacaoadicional2520")
                campo_hora.scroll_into_view_if_needed()
                hora_valor = campo_hora.input_value()
                logger.info(f"Hora de Início capturada: {hora_valor}")

                # 3. Captura data que a automação ta sendo executada.
                data_atual = datetime.now().strftime("%d/%m/%Y")

                # 4. Capturar o campo "Aberto em" (Apenas a Data)
                campo_data_completa = aba_chamado.locator("#label_dtchamado")
                campo_data_completa.scroll_into_view_if_needed()
                texto_data_completa = campo_data_completa.text_content()
                data_abertura = texto_data_completa.split(" - ")[0].strip()
                logger.info(f"Data de abertura capturada: {data_abertura}")

                file_path = get_path(os.path.join("data", "info_incidente.json"))
                with open(file_path, "r", encoding="utf-8") as o:
                    info_incidente = json.load(o)

                info_incidente["parceiro"] = parceiro_valor
                info_incidente['data_inicio'] = data_abertura
                info_incidente["hora_inicio"] = hora_valor
                info_incidente["data_fim"] = data_atual

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(info_incidente, f, indent=4, ensure_ascii=False)

                calcula_perda(browser)

                with open(file_path, "r", encoding="utf-8") as f:
                    info_incidente = json.load(f)

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(info_incidente, f, indent=4, ensure_ascii=False)

                logger.info("Arquivo data/info_incidente.json atualizado com sucesso com os dados do Qualitor!")
            except Exception:
                logger.exception(f"Erro ao atualizar os dados")

            logger.info("Iniciando preenchimento dos campos...")

            perda_media = info_incidente['perda_media']
            parceiro = info_incidente['parceiro']
            data_inicio = info_incidente['data_inicio']
            hora_inicio = info_incidente["hora_inicio"]
            data_encerramento = info_incidente["data_fim"]
            hora_encerramento = info_incidente['hora_fim']
            
            aba_chamado.wait_for_timeout(5000)
            texto_para_digitar = f"Acionado equipes do parceiro {parceiro} para validação do transacional."
            aba_chamado.fill("#vlinformacaoadicional1156", texto_para_digitar)

            campo_data_inicio = aba_chamado.locator("#vlinformacaoadicional2308")
            campo_data_inicio.click()
            campo_data_inicio.press_sequentially(data_inicio)
            aba_chamado.fill("#vlinformacaoadicional2306", hora_inicio)

            campo_data_fim = aba_chamado.locator("#vlinformacaoadicional2309")
            campo_data_fim.click()
            campo_data_fim.press_sequentially(data_encerramento)
            aba_chamado.fill("#vlinformacaoadicional2307", hora_encerramento)
            aba_chamado.fill("#vlinformacaoadicional2310", f'{perda_media},00')
            logger.info("Campos preenchidos corretamente")
            aba_chamado.wait_for_timeout(3000)
            aba_chamado.locator('#btnNextEtapa').click()
            aba_chamado.wait_for_timeout(3000)
            aba_chamado.locator("span", has_text="ENCERRAR ATENDIMENTO").click()
            aba_chamado.wait_for_timeout(3000)
            logger.info("Chamado encerrado com sucesso")
            aba_chamado.close()
    
    except Exception:
        logger.exception(f"Erro ao encerrar o chamado")