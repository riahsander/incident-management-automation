"""
envio_email.py

Módulo responsável pela geração e preparação das comunicações de
incidentes via Microsoft Outlook.

A partir das informações registradas durante a execução da aplicação,
o módulo identifica os destinatários da operadora afetada, monta o
conteúdo do e-mail, anexa as evidências geradas e abre uma nova
mensagem no Outlook pronta para envio.

Funcionalidades:
    - Carregamento dos destinatários por operadora.
    - Leitura das informações do incidente.
    - Recuperação automática da assinatura do Outlook.
    - Geração dinâmica do assunto do e-mail.
    - Construção do corpo da mensagem em HTML.
    - Inclusão automática de evidências como anexos.
    - Integração com Microsoft Outlook.

Arquivos utilizados:
    - data/email_op.json
    - data/info_incidente.json

Dependências:
    - pywin32
    - python-dotenv
    - json
    - datetime
"""

import json
import win32com.client as win32
from datetime import datetime
from dotenv import load_dotenv
from backend.path_utils import get_path
import os

load_dotenv()

def get_emails(operadora):
    """
    Recupera os destinatários associados a uma operadora.
     
    A função consulta o arquivo de configuração contendo os
    destinatários cadastrados e retorna uma string formatada
    para utilização no campo "Para" do Outlook.
     
    Args:
    operadora (str):
    Nome da operadora utilizada para busca.
     
    Returns:
    str:
    Lista de destinatários separados por ponto e vírgula.
     
    Exemplo:
     
    "noc@empresa-exemplo.com;
    suporte@empresa-exemplo.com"
    """
    with open(get_path(os.path.join("data", "email_op.json")), "r", encoding="utf-8") as ie:
        info_email = json.load(ie)

    emails = info_email.get(operadora, {}).get("emails", [])
    return ";".join(emails)


def enviar_email(chamado):
    """
    Cria uma comunicação de incidente utilizando Microsoft Outlook.
     
    A função carrega os dados do incidente registrados pela aplicação,
    obtém a lista de destinatários da operadora selecionada, monta o
    conteúdo da mensagem em HTML e adiciona as evidências geradas
    durante o processamento.
     
    Fluxo:
    1. Carrega as informações do incidente.
    2. Obtém os destinatários configurados.
    3. Recupera a assinatura padrão do Outlook.
    4. Cria um novo e-mail.
    5. Monta o assunto da comunicação.
    6. Gera o conteúdo HTML.
    7. Adiciona evidências como anexos.
    8. Exibe o e-mail para revisão e envio.
     
    Args:
    chamado (str):
    Identificador do chamado associado ao incidente.
     
    Anexos possíveis:
    - Evidência operacional.
    - Evidência transacional.
     
    Returns:
    None
     
    Raises:
    Exception:
    Registra no console qualquer erro ocorrido durante a
    preparação da comunicação.
    """
    print("Enviando e-mail...")
    try:
        # Carrega as informações previamente registradas para o incidente.
        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "r", encoding="utf-8") as o:
            info_incidente = json.load(o)

        # Recupera automaticamente a assinatura padrão configurada no Outlook.
        assinatura_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Signatures")
        assinatura_html = ""
        if os.path.exists(assinatura_dir):
            for fname in os.listdir(assinatura_dir):
                if fname.endswith(".htm"):
                    with open(os.path.join(assinatura_dir, fname), "r", encoding="utf-8") as f:
                        assinatura_html = f.read()
                    break

        # Atualiza a referência temporal utilizada na comunicação
        # com o horário da geração do e-mail.
        info_incidente["hora_inicio"] = datetime.now().strftime("%H:%M")

        # Inicializa a integração com o Microsoft Outlook.
        outlook = win32.Dispatch("outlook.application")
        email = outlook.CreateItem(0)

        parceiro = info_incidente.get("parceiro", "DESCONHECIDO")
        status = info_incidente.get("status", "N/A")

        email.To = get_emails(parceiro)
        email.CC = "noc@empresa.com.br"
        email.Subject = f"Transações {status} - {parceiro} - Chamado {chamado}"

        # Monta dinamicamente o conteúdo HTML da comunicação.
        email.HTMLBody = f"""
        <html>
        <body style="font-family: Calibri, Arial, sans-serif; font-size: 12pt; color: #1a1a1a; line-height: 1.5;">
            <p>Prezados,</p>
            <p>Identificamos em nosso monitoramento o aumento de transações 
            <strong style="color:#d32f2f;">{status}</strong> 
            com o parceiro <strong>{parceiro}</strong>.</p>
            <p>Em anexo, seguem as evidências para validação.</p>
            <hr style="border:none; border-top:1px solid #ccc; margin:16px 0;">
            <table style="border-collapse:collapse; width:100%; font-size:11pt;">
                <tr><td style="padding:4px 8px; font-weight:bold;">Apresenta erros no Autorizador:</td>
                    <td style="padding:4px 8px;">{info_incidente.get("autorizador","N/A")}</td></tr>
                <tr><td style="padding:4px 8px; font-weight:bold;">Status das transações:</td>
                    <td style="padding:4px 8px;">{status}</td></tr>
                <tr><td style="padding:4px 8px; font-weight:bold;">Indisponibilidade:</td>
                    <td style="padding:4px 8px;">{info_incidente.get("indisponibilidade","N/A")}</td></tr>
                <tr><td style="padding:4px 8px; font-weight:bold;">Hora Início:</td>
                    <td style="padding:4px 8px;">{info_incidente["hora_inicio"]}</td></tr>
            </table>
            <hr style="border:none; border-top:1px solid #ccc; margin:16px 0;">
            <br>{assinatura_html}
        </body>
        </html>
        """

        # Adiciona as evidências geradas ao e-mail quando disponíveis.
        if info_incidente.get("print_operadora") and os.path.exists(info_incidente["print_operadora"]):
            email.Attachments.Add(info_incidente["print_operadora"])

        if info_incidente.get("print_grafico") and os.path.exists(info_incidente["print_grafico"]):
            email.Attachments.Add(info_incidente["print_grafico"])

        email.Display()
        print("Email enviado com sucesso!")
    except Exception as e:
        print("Erro ao enviar email:", e)
