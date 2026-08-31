"""
abertura_chamado.py

Módulo responsável pela automação do registro de incidentes em uma
plataforma de gerenciamento de chamados.

Através do Playwright, o módulo acessa a aplicação web, realiza
autenticação, preenche automaticamente os campos necessários e
submete as informações coletadas pela aplicação.

Funcionalidades:
    - Leitura dos dados do incidente.
    - Conversão de informações para o formato esperado pelo sistema.
    - Autenticação automática.
    - Preenchimento automatizado de formulários.
    - Registro do incidente.
    - Recuperação do identificador do chamado.

Arquivos utilizados:
    - data/info_incidente.json

Dependências:
    - Playwright
    - python-dotenv

Variáveis de ambiente:
    - QUALITOR
    - USER
    - PASSWORD

Fluxo:
    Incidente → Portal de Chamados → Preenchimento Automático → Chamado
"""

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from backend.path_utils import get_path
import os, sys
import json

load_dotenv()
qualitor = os.getenv("QUALITOR")
user = os.getenv("USER")
password = os.getenv("PASSWORD")


def marcar_status(pagina, lista):
    """
    Seleciona os status das transações no formulário de abertura
    do chamado.
     
    A função converte o status informado pelo usuário para os
    controles correspondentes da interface web.
     
    Status suportados:
    - Negadas
    - Pendentes
    - Desfeitas
    - Erro
    - Negadas e Pendentes
    - Desfeitas e Pendentes
     
    Args:
    pagina:
    Objeto Page do Playwright utilizado para interação
    com a aplicação.
     
    lista (dict):
    Dicionário contendo os dados do incidente.
     
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
    Realiza a abertura automática de um chamado.

    A função recupera as informações registradas no incidente,
    acessa o sistema de chamados e preenche automaticamente os
    campos necessários para registro da ocorrência.

    Fluxo:
        1. Carrega os dados do incidente.
        2. Ajusta informações para compatibilidade com o sistema.
        3. Inicia o navegador automatizado.
        4. Realiza autenticação.
        5. Preenche o formulário de chamado.
        6. Registra a ocorrência.
        7. Retorna o identificador do chamado.

    Campos preenchidos:
        - Parceiro
        - Conexão com autorizador
        - Indisponibilidade
        - Status das transações
        - Horário de início
        - Descrição da ocorrência

    Returns:
        int:
            Número identificador do chamado gerado.

    Raises:
        Exception:
            Qualquer erro durante a navegação ou preenchimento
            poderá interromper o processo.
    """
    # Carrega as informações previamente registradas para o incidente.
    file_path = get_path(os.path.join("data", "info_incidente.json"))
    with open(file_path, "r", encoding="utf-8") as o:
        lista_operadoras = json.load(o)

    # Realiza conversões necessárias para compatibilidade com o sistema.
    if lista_operadoras['parceiro'] == 'BANCO XI':
        operadora = 'XI PIX'
    else:
        operadora = lista_operadoras['parceiro']

    # Converte o tipo de indisponibilidade para o formato esperado.
    indisponibilidade = "Sim" if lista_operadoras['indisponibilidade'] == "Total" else "N"

    # Inicializa o navegador utilizado na automação.
    with sync_playwright() as p:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        # Define o executável Chromium utilizado pelo Playwright.
        chromium_path = os.path.join(base_path, "chromium-1234", "chrome-win64", "chrome.exe")

        browser = p.chromium.launch(executable_path=chromium_path)

        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(qualitor)

        # Realiza autenticação na plataforma de chamados.
        page.fill("input[placeholder='Usuário']", user)
        page.press("input[name='cdusuario']", "Tab")
        page.click("#cdsenha.input")
        page.wait_for_selector("#cdsenha:not([disabled])")
        page.fill("input[placeholder='Senha']", password)
        page.click("#btnLogin")
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        # Preenche automaticamente os campos do formulário de incidente.
        page.goto(qualitor)
        page.wait_for_timeout(1000)
        page.select_option("#Parceiro", value=operadora)
        page.select_option("#ConexaoAutorizador", value=lista_operadoras['autorizador'])
        page.select_option("#indisp", value=indisponibilidade)
        marcar_status(page, lista_operadoras)
        page.fill("#HoraInicio", lista_operadoras['hora_inicio'])
        page.fill('#dschamado', f"Transações {lista_operadoras['status']} com o parceiro {lista_operadoras['parceiro']}.")

        # Espera 1 segundo
        page.wait_for_timeout(1000)
    
        # Clica em Processar
        page.locator("button[title='Processar']").click()

        page.wait_for_timeout(1000)

        # Aguarda o modal de confirmação aparecer
        page.wait_for_selector("td.COLORLABEL b")

        # Captura o número do chamado
        chamado = page.locator("td.COLORLABEL b").inner_text().strip()

        page.click('#btnNO')

        page.wait_for_timeout(3000)

        browser.close()
        return chamado
 
