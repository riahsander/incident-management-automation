"""
abertura_chamado.py

Módulo responsável pela abertura automatizada de chamados em uma
plataforma de gerenciamento de incidentes.

Utilizando Playwright, o módulo acessa o portal, realiza autenticação,
preenche automaticamente o formulário de registro utilizando as
informações coletadas pela aplicação e obtém o identificador do
chamado gerado.

Funcionalidades:
    - Leitura dos dados do incidente.
    - Conversão de informações para o formato esperado pelo sistema.
    - Autenticação automática na plataforma.
    - Preenchimento automatizado de formulário.
    - Registro do incidente.
    - Captura do número do chamado gerado.

Dependências:
    - Playwright
    - python-dotenv

Variáveis de ambiente:
    - QUALITOR
    - USER
    - PASSWORD

Arquivos utilizados:
    - data/info_incidente.json

Saída:
    - Número do chamado registrado.
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
    Marca os status das transações no formulário de abertura
    do chamado.
     
    A função interpreta o status informado durante o registro
    do incidente e seleciona as opções correspondentes na
    interface da plataforma.
     
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
    com a plataforma.
     
    lista (dict):
    Dicionário contendo as informações do incidente.
     
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
    Registra automaticamente um chamado na plataforma.
     
    A função carrega os dados previamente informados pelo usuário,
    acessa o sistema de gerenciamento de incidentes e realiza o
    preenchimento automático dos campos necessários para registro
    da ocorrência.
     
    Fluxo:
    1. Carrega os dados do incidente.
    2. Realiza ajustes de compatibilidade das informações.
    3. Inicia o navegador automatizado.
    4. Realiza autenticação.
    5. Preenche o formulário do incidente.
    6. Processa o registro.
    7. Captura o número do chamado gerado.
    8. Fecha o navegador.
     
    Campos preenchidos:
    - Parceiro
    - Conexão com autorizador
    - Tipo de indisponibilidade
    - Status das transações
    - Hora de início
    - Descrição do incidente
     
    Returns:
    int | str:
    Número identificador do chamado.
     
    Raises:
    Exception:
    Pode interromper a execução caso ocorram erros
    de navegação, autenticação ou preenchimento.
    """
    # Lê os dados do incidente
    file_path = get_path(os.path.join("data", "info_incidente.json"))
    with open(file_path, "r", encoding="utf-8") as o:
        lista_operadoras = json.load(o)

    # Ajusta nome da operadora
    if lista_operadoras['parceiro'] == 'BANCO TOPAZIO ATM':
        operadora = 'TOPAZIO PIX'
    else:
        operadora = lista_operadoras['parceiro']

    # Ajusta indisponibilidade
    indisponibilidade = "Sim" if lista_operadoras['indisponibilidade'] == "Total" else "N"

    # Lança navegador
    with sync_playwright() as p:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        # Caminho do Chromium empacotado
        chromium_path = os.path.join(base_path, "chromium-1234", "chrome-win64", "chrome.exe")

        browser = p.chromium.launch(executable_path=chromium_path)

        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(qualitor)

        # Login
        page.fill("input[placeholder='Usuário']", user)
        page.press("input[name='cdusuario']", "Tab")
        page.click("#cdsenha.input")
        page.wait_for_selector("#cdsenha:not([disabled])")
        page.fill("input[placeholder='Senha']", password)
        page.click("#btnLogin")
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        # Preenche formulário
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

        chamado = 123445

        page.wait_for_timeout(3000)

        browser.close()
        return chamado
 
