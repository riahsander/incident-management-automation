"""
Comunicação por e-mail da automação de incidentes.

O módulo utiliza o Microsoft Outlook para gerar e enviar as comunicações
relacionadas ao registro e à finalização de incidentes.

Responsabilidades:
    - Consultar os destinatários configurados para cada parceiro.
    - Criar e enviar o e-mail de registro do incidente.
    - Anexar as evidências geradas pela automação.
    - Criar e enviar o e-mail de normalização do incidente.
    - Sincronizar o Outlook antes e após o envio das mensagens.
    - Fornecer as comunicações utilizadas como gatilho pelos fluxos
      do Power Automate.

As informações utilizadas nas mensagens são obtidas principalmente
do arquivo data/info_incidente.json.
"""

import json
import win32com.client as win32
from dotenv import load_dotenv
from backend.path_utils import get_path
import os
from backend.logger_config import logger
import time


load_dotenv()

def get_emails(operadora):
    """
    Obtém os destinatários de e-mail configurados para uma operadora.

    A função consulta data/email_op.json e recupera a lista de
    destinatários associados ao parceiro informado. Os endereços
    encontrados são concatenados utilizando ponto e vírgula para
    utilização pelo Outlook.

    Args:
        operadora (str): Nome da operadora utilizada na consulta.

    Returns:
        str: Endereços de e-mail separados por ponto e vírgula.
        Retorna uma string vazia caso nenhum destinatário seja
        encontrado ou ocorra uma falha.
    """
    logger.info("Buscando e-mails de destino...")
    try:
        with open(get_path(os.path.join("data", "email_op.json")), "r", encoding="utf-8") as ie:
            info_email = json.load(ie)
    
        emails = info_email.get(operadora, {}).get("emails", [])

        if not emails:
            logger.info(f"Nenhum e-mail cadastrado para {operadora}")
            print(f"Nenhum e-mail cadastrado para {operadora}")
            return " "

        logger.info("E-mails de destino encontrados.")
        return ";".join(emails)
    except Exception:
        logger.exception("Erro na etapa de busca dos e-mails:")
        return " "


def sincronizar_outlook(outlook):
    """
    Solicita a sincronização de envio e recebimento do Outlook.

    A função tenta executar diferentes mecanismos disponíveis na
    integração COM do Outlook para aumentar a confiabilidade da
    sincronização das mensagens.

    Estratégias utilizadas:
        - Session.SendAndReceive.
        - MAPI SendAndReceive.
        - Comando SendReceiveAll da interface ativa.

    A falha em uma estratégia não impede a tentativa das demais.

    Args:
        outlook: Instância da aplicação Outlook criada através
        da integração COM.

    Returns:
        bool: True quando pelo menos uma estratégia de sincronização
        é executada com sucesso. False quando todas falham.
    """
    sucesso = False

    try:
        outlook.Session.SendAndReceive(True)
        logger.info("Session.SendAndReceive executado com sucesso")
        sucesso = True
    except Exception as e:
        logger.warning(f"Falha Session.SendAndReceive: {e}")
    time.sleep(1)
    try:
        namespace = outlook.GetNamespace("MAPI")
        namespace.SendAndReceive(False)
        logger.info("MAPI SendAndReceive executado com sucesso")
        sucesso = True
    except Exception as e:
        logger.warning(f"Falha MAPI SendAndReceive: {e}")
    time.sleep(1)
    try:
        explorer = outlook.ActiveExplorer()
        if explorer:
            explorer.CommandBars.ExecuteMso("SendReceiveAll")
            logger.info("SendReceiveAll executado com sucesso")
            sucesso = True
        else:
            logger.warning("ActiveExplorer não disponível")
    except Exception as e:
        logger.warning(f"Falha ExecuteMso: {e}")

    return sucesso

    

def enviar_email(chamado):
    """
    Cria e envia a comunicação de registro do incidente.

    A função carrega as informações do incidente, identifica os
    destinatários do parceiro, monta o assunto e o corpo da mensagem
    e adiciona as evidências disponíveis como anexos.

    Após a criação da mensagem, o Outlook é sincronizado e o e-mail
    é enviado. Essa comunicação também é utilizada como gatilho para
    continuidade do fluxo de registro no Power Automate.

    Args:
        chamado (str): Número do chamado aberto no Qualitor.

    Evidências anexadas quando disponíveis:
        - Card da operadora.
        - Gráfico transacional.
        - Detalhamento transacional da operadora.

    Returns:
        None
    """
    logger.info("Enviando e-mail...")
    print("Enviando e-mail...")
    try:
        # Carrega dados do incidente
        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "r", encoding="utf-8") as o:
            info_incidente = json.load(o)

        # Busca assinatura automaticamente
        logger.info("Buscando assinatura...")
        try:
            assinatura_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Signatures")
            assinatura_html = ""
            if os.path.exists(assinatura_dir):
                for fname in os.listdir(assinatura_dir):
                    if fname.endswith(".htm"):
                        with open(os.path.join(assinatura_dir, fname), "r", encoding="utf-8") as f:
                            assinatura_html = f.read()
                        break
        except Exception:
            logger.exception("Assinatura não encontrada.")

        # Busca a hora de início
        hora_inicio_incidente = info_incidente.get("hora_inicio", "99:99")

        logger.info("Criando conexão e corpo do e-mail...")
        # Cria objeto Outlook
        outlook = win32.Dispatch("outlook.application")
        email = outlook.CreateItem(0)


        parceiro = info_incidente.get("parceiro", "DESCONHECIDO")
        status = info_incidente.get("status", "N/A")
        tipo_transacao = info_incidente.get("tipo_transacao" , "AMBOS")

        email.To = get_emails(parceiro)
        

        if info_incidente.get("parceiro") == 'BANCO TOPAZIO ATM':
            parceiro = 'TOPAZIO PIX'
        else:
            parceiro = info_incidente.get("parceiro", "DESCONHECIDO")

        email.CC = "noc@gmail.com; equipedeapoio@email.com"
        if tipo_transacao == "SAQUE":
            email.Subject = f"Status Transações {status} - {parceiro} - {tipo_transacao} - Chamado {chamado}"
        elif tipo_transacao == "DEPOSITO":
            email.Subject = f"Status Transações {status} - {parceiro} - {tipo_transacao} - Chamado {chamado}"
        else:
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
            <p>Automation Service</p>
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

        sincronizar_outlook(outlook)
        email.Send()
        logger.info('E-mail enviado com sucesso')
        print("E-mail enviado com sucesso!")

        time.sleep(3)

        sincronizar_outlook(outlook)

    except Exception:
        logger.exception("Erro ao enviar email.")




def fecha_email():
    logger.info("Enviando e-mail...")
    print("Enviando e-mail...")
    try:
        # Carrega dados do incidente
        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "r", encoding="utf-8") as o:
            info_incidente = json.load(o)

        # Busca assinatura automaticamente
        logger.info("Buscando assinatura...")
        try:
            assinatura_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Signatures")
            assinatura_html = ""
            if os.path.exists(assinatura_dir):
                for fname in os.listdir(assinatura_dir):
                    if fname.endswith(".htm"):
                        with open(os.path.join(assinatura_dir, fname), "r", encoding="utf-8") as f:
                            assinatura_html = f.read()
                        break
        except Exception:
            logger.exception("Assinatura não encontrada.")

        logger.info("Criando conexão e corpo do e-mail...")
        # Cria objeto Outlook
        outlook = win32.Dispatch("outlook.application")
        email = outlook.CreateItem(0)


        parceiro = info_incidente.get("parceiro", "DESCONHECIDO")
        escopo = info_incidente.get("escopo")
        chamado = info_incidente.get("chamado")
        perda_media = info_incidente.get("perda_media")
        data_inicio = info_incidente.get("data_inicio")
        hora_inicio = info_incidente.get("hora_inicio")
        data_fim = info_incidente.get("data_fim")
        hora_fim = info_incidente.get("hora_fim")
        causa = info_incidente.get("causa")
        origem = info_incidente.get("origem")

        email.To = "noc@gmail.com"

        if escopo == "SAQUE":
            email.Subject = f"Normalização Incidente com o {parceiro} - {escopo} - Chamado {chamado}"
        elif escopo == "DEPOSITO":
            email.Subject = f"Normalização Incidente com o {parceiro} - {escopo} - Chamado {chamado}"
        else:
            email.Subject = f"Normalização Incidente com o {parceiro} - Chamado {chamado}"

        # Corpo do e-mail
        email.HTMLBody = f"""
        <html>
        <body style="font-family: Arial, sans-serif; font-size: 11pt;">

        <p>Prezados, para registro:</p>

        <p>
        Informamos a normalização do incidente transacional junto ao parceiro
        <strong>{parceiro}</strong>, referente ao chamado
        <strong>{chamado}</strong>.
        </p>

        <p><strong>Informações da ocorrência:</strong></p>

        <ul>
            <li><strong>Data do incidente:</strong> {data_inicio}</li>
            <li><strong>Horário de início:</strong> {hora_inicio}</li>
            <li><strong>Data de normalização:</strong> {data_fim}</li>
            <li><strong>Horário de normalização:</strong> {hora_fim}</li>
            <li><strong>Causa:</strong> {causa}</li>
            <li><strong>Perda média estimada:</strong> {perda_media}</li>
            <li><strong>Escopo:</strong> {escopo}</li>
            <li><strong>Origem:</strong> {origem}</li>
        </ul>

        <hr style="border:none; border-top:1px solid #ccc; margin:16px 0;">

        <p>Automation Service - Encerramento</p>

        <br>{assinatura_html}

        </body>
        </html>
        """

        sincronizar_outlook(outlook)
        email.Send()
        logger.info('E-mail enviado com sucesso')
        print("E-mail enviado com sucesso!")

        time.sleep(3)

        sincronizar_outlook(outlook)
    except Exception:
        logger.exception("Erro ao enviar email.")