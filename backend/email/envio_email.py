"""
envio_email.py

Módulo responsável pela geração e preparação das comunicações de
incidentes por meio do Microsoft Outlook.

A partir das informações coletadas durante a execução da aplicação,
o módulo identifica os destinatários da operadora afetada, monta uma
comunicação padronizada em HTML, incorpora a assinatura do Outlook e
adiciona automaticamente as evidências geradas pelo sistema.

Funcionalidades:
    - Carregamento automático de destinatários por operadora.
    - Leitura dos dados do incidente.
    - Recuperação da assinatura padrão do Outlook.
    - Construção dinâmica do assunto do e-mail.
    - Geração de conteúdo HTML formatado.
    - Inclusão automática de anexos.
    - Integração com Microsoft Outlook.

Arquivos utilizados:
    - data/email_op.json
    - data/info_incidente.json

Dependências:
    - pywin32
    - python-dotenv
    - json
    - datetime

Saída:
    - Nova mensagem de e-mail aberta no Outlook.
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
    grupos de e-mail cadastrados para cada operadora e
    retorna os endereços formatados para utilização no Outlook.
     
    Args:
    operadora (str):
    Nome da operadora utilizada na busca.
     
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
     
    A função recupera as informações registradas durante o fluxo da
    aplicação, identifica os destinatários responsáveis pela operadora
    afetada e prepara uma mensagem pronta para envio.
     
    Fluxo:
    1. Carrega os dados do incidente.
    2. Obtém os destinatários configurados.
    3. Recupera a assinatura padrão do Outlook.
    4. Cria uma nova mensagem.
    5. Monta o assunto do incidente.
    6. Gera o conteúdo HTML da comunicação.
    7. Adiciona evidências como anexos.
    8. Exibe o e-mail para revisão e envio.
     
    Args:
    chamado (str | int):
    Identificador do chamado associado ao incidente.
     
    Anexos suportados:
    - print_operadora
    - print_grafico
    - print_op_detalhado
     
    Informações exibidas na comunicação:
    - Parceiro
    - Status das transações
    - Presença de erros no autorizador
    - Tipo de indisponibilidade
    - Hora de início do incidente
    - Número do chamado
     
    Returns:
    None
     
    Raises:
    Exception:
    Registra no console qualquer erro ocorrido durante
    a montagem da comunicação.
    """
    print("Enviando e-mail...")
    try:
        # Carrega dados do incidente
        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "r", encoding="utf-8") as o:
            info_incidente = json.load(o)

        # Busca assinatura automaticamente
        assinatura_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Signatures")
        assinatura_html = ""
        if os.path.exists(assinatura_dir):
            for fname in os.listdir(assinatura_dir):
                if fname.endswith(".htm"):
                    with open(os.path.join(assinatura_dir, fname), "r", encoding="utf-8") as f:
                        assinatura_html = f.read()
                    break

        # Recupera o horário de início informado durante o registro do incidente.
        hora_inicio_incidente = info_incidente.get("hora_inicio", "99:99")

        # Cria objeto Outlook
        outlook = win32.Dispatch("outlook.application")
        email = outlook.CreateItem(0)

        parceiro = info_incidente.get("parceiro", "DESCONHECIDO")
        status = info_incidente.get("status", "N/A")

        email.To = get_emails(parceiro)
        email.CC = "noc@empresa.com.br; sustentacaoti@empresa.com.br"
        email.Subject = f"Status Transações {status} - {parceiro} - Chamado {chamado}"

        # Corpo do e-mail
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
                    <td style="padding:4px 8px;">{hora_inicio_incidente}</td></tr>
            </table>
            <hr style="border:none; border-top:1px solid #ccc; margin:16px 0;">
            <br>{assinatura_html}
        </body>
        </html>
        """

        # Anexos só se existirem
        if info_incidente.get("print_operadora") and os.path.exists(info_incidente["print_operadora"]):
            email.Attachments.Add(info_incidente["print_operadora"])

        if info_incidente.get("print_grafico") and os.path.exists(info_incidente["print_grafico"]):
            email.Attachments.Add(info_incidente["print_grafico"])

        if info_incidente.get("print_op_detalhado") and os.path.exists(info_incidente["print_op_detalhado"]):
            email.Attachments.Add(info_incidente["print_op_detalhado"])

        email.Display()
        print("Email enviado com sucesso!")
    except Exception as e:
        print("Erro ao enviar email:", e)
