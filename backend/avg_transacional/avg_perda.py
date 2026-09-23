"""
Análise transacional para estimativa de perda do incidente.

O módulo consulta o Portal Transacional utilizando Playwright para
estimar a perda média associada ao período de indisponibilidade.

Responsabilidades:
    - Ler as informações do incidente.
    - Determinar um período histórico comparável ao incidente.
    - Considerar dias úteis, finais de semana e feriados na comparação.
    - Selecionar a operadora e o escopo transacional correspondente.
    - Consultar o volume de transações no período de referência.
    - Registrar a perda média em data/info_incidente.json.

O módulo é utilizado durante o processo de encerramento do chamado
para complementar as informações do incidente.
"""

from dotenv import load_dotenv
from backend.path_utils import get_path
from backend.logger_config import logger
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import holidays
import json
import os
import re


load_dotenv()
portal = os.getenv("PORTAL")
user = os.getenv("USER")
password = os.getenv("PASSWORD")



def validador_data(data_de_inicio, data_de_fim, hora_inicio, hora_fim):
    """
    Calcula um período histórico comparável ao período do incidente.

    A função calcula a duração real do incidente e procura, aproximadamente
    um mês antes, uma data que possua o mesmo perfil transacional da data
    de início do incidente.

    Os dias são classificados como:
        - ALTA_TRANSACIONAL: dias úteis que não sejam feriados.
        - BAIXA_TRANSACIONAL: finais de semana ou feriados brasileiros.

    Após encontrar a data de referência, a duração original do incidente
    é aplicada para determinar o fim do período histórico.

    Args:
        data_de_inicio (str): Data de início no formato DD/MM/AAAA.
        data_de_fim (str): Data de término no formato DD/MM/AAAA.
        hora_inicio (str): Hora de início no formato HH:MM.
        hora_fim (str): Hora de término no formato HH:MM.

    Returns:
        tuple: Período histórico contendo:
            - Data inicial no formato AAAA/MM/DD.
            - Data final no formato AAAA/MM/DD.
            - Hora inicial no formato HH:MM.
            - Hora final no formato HH:MM.

    Raises:
        Exception: Propaga erros ocorridos durante o cálculo do período.
    """
    logger.info('Calculando data mais próxima do incidente no último mês...')

    try:
        feriados_br = holidays.BR()

        # Monta datetime completo
        data_inicio = datetime.strptime(
            f"{data_de_inicio} {hora_inicio}",
            "%d/%m/%Y %H:%M"
        )

        data_fim = datetime.strptime(
            f"{data_de_fim} {hora_fim}",
            "%d/%m/%Y %H:%M"
        )

        # Duração real do incidente (dias, horas e minutos)
        duracao_incidente = data_fim - data_inicio

        def obter_tipo_dia(data):
            """
            Classifica uma data conforme seu perfil transacional.

            Args:
                data (datetime): Data que será classificada.

            Returns:
                str: "BAIXA_TRANSACIONAL" para finais de semana ou feriados
                brasileiros e "ALTA_TRANSACIONAL" para os demais dias.
            """
            data_base = data.date()

            if data_base.weekday() >= 5 or data_base in feriados_br:
                return "BAIXA_TRANSACIONAL"

            return "ALTA_TRANSACIONAL"

        tipo_inicio = obter_tipo_dia(data_inicio)

        # Volta exatamente 1 mês mantendo o horário
        data_referencia = data_inicio - relativedelta(months=1)

        alvo_inicio_retroativo = None

        # Procura a data mais próxima com o mesmo perfil transacional
        for deslocamento in range(31):

            anterior = data_referencia - timedelta(days=deslocamento)

            if obter_tipo_dia(anterior) == tipo_inicio:
                alvo_inicio_retroativo = anterior
                break

            posterior = data_referencia + timedelta(days=deslocamento)

            if obter_tipo_dia(posterior) == tipo_inicio:
                alvo_inicio_retroativo = posterior
                break

        if alvo_inicio_retroativo is None:
            alvo_inicio_retroativo = data_referencia

        # Mantém exatamente a mesma duração do incidente
        alvo_fim_retroativo = alvo_inicio_retroativo + duracao_incidente

        return (
            alvo_inicio_retroativo.strftime("%Y/%m/%d"),
            alvo_fim_retroativo.strftime("%Y/%m/%d"),
            alvo_inicio_retroativo.strftime("%H:%M"),
            alvo_fim_retroativo.strftime("%H:%M")
        )

    except Exception:
        logger.exception("Erro ao encontrar a data correta.")
        raise


def calcula_perda(browser):
    """
    Calcula a perda média estimada do incidente.

    A função utiliza as informações armazenadas em
    data/info_incidente.json para consultar o Portal Transacional.

    O período utilizado na consulta é determinado por validador_data(),
    buscando um período histórico com perfil transacional equivalente
    e com a mesma duração do incidente.

    Durante a consulta são considerados:
        - Parceiro/operadora.
        - Escopo do incidente.
        - Período histórico de referência.
        - Tipo de transação correspondente.

    A quantidade de registros encontrada na consulta é utilizada como
    perda média estimada e armazenada na chave "perda_media" do arquivo
    data/info_incidente.json.

    Args:
        browser: Instância do navegador Playwright compartilhada com
        o fluxo de encerramento do chamado.

    Returns:
        None
    """
    logger.info('Entrando no Portal Transacional...')
    try:
        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "r", encoding="utf-8") as o:
            info_incidente = json.load(o)


        operadora = info_incidente['parceiro']
        if operadora == 'BANCO EXEMPLO':
            operadora = 'Banco Exemplo Atm'
        elif operadora == 'BANCO SUPER MAIS':
            operadora = 'Mais'
        elif operadora == "BANCO DA CIDADE - TRANSACOES":
            operadora = 'Banco da Cidade'
        else:
            operadora = operadora.title()
        data_inicio = info_incidente['data_inicio'] 
        hora_inicio = info_incidente["hora_inicio"] 
        data_fim = info_incidente["data_fim"] 
        hora_fim = info_incidente['hora_fim']

        page = browser.new_page()
        page.set_viewport_size({"width": 2800, "height": 1600})
        page.goto(portal)
        page.get_by_role("link", name="Login").click()
        page.locator("input[name='j_username']").fill(user)
        page.locator("input[name='j_password']").fill(password)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        logger.info("Login concluído!")
                
        page.goto(portal)
        page.locator("input[value='captura']").check()
        seletor_operadoras = page.locator("select[ng-model='consulta.operadoras']")
        seletor_operadoras.scroll_into_view_if_needed()
        seletor_operadoras.select_option(label=operadora)
        if operadora == 'Banco Topazio Atm':
            if info_incidente['escopo'] == 'GERAL':
                select_transacao = page.locator("#tipoTransacao")
                select_transacao.scroll_into_view_if_needed()
                todos_valores = select_transacao.evaluate("select => Array.from(select.options).map(option => option.value)")
                select_transacao.select_option(value=todos_valores)
            elif info_incidente['escopo'] == 'SAQUE':
                select_transacao = page.locator("#tipoTransacao")
                select_transacao.scroll_into_view_if_needed()
                select_transacao.select_option(label='PIX SAQUE')
            elif info_incidente['escopo'] == 'DEPOSITO':
                select_transacao = page.locator("#tipoTransacao")
                select_transacao.scroll_into_view_if_needed()
                select_transacao.select_option(label='PIX DEPOSITO')
        else:
            if info_incidente['escopo'] == 'GERAL':
                select_transacao = page.locator("#tipoTransacao")
                select_transacao.scroll_into_view_if_needed()
                todos_valores = select_transacao.evaluate("select => Array.from(select.options).map(option => option.value)")
                select_transacao.select_option(value=todos_valores)
            elif info_incidente['escopo'] == 'SAQUE':
                select_transacao = page.locator("#tipoTransacao")
                select_transacao.scroll_into_view_if_needed()
                select_transacao.select_option(label='Saque')
            elif info_incidente['escopo'] == 'DEPOSITO':
                select_transacao = page.locator("#tipoTransacao")
                select_transacao.scroll_into_view_if_needed()
                select_transacao.select_option(label='Depósito Varejista')

                    
        data_inicial_ajustada, data_final_ajustada, hora_inicio_ref,hora_fim_ref = validador_data(data_inicio, data_fim, hora_inicio, hora_fim)
        campo_data_inicial = page.locator("input[ng-model='consulta.dataInicial']")
        campo_data_inicial.click()
        campo_data_inicial.fill(f'{data_inicial_ajustada} {hora_inicio_ref}')
        logger.info(f"Campo 'Data Inicial' preenchido com: {data_inicial_ajustada} {hora_inicio_ref}")
        campo_data_final = page.locator("input[ng-model='consulta.dataFinal']")
        campo_data_final.click()
        campo_data_final.fill(f'{data_final_ajustada} {hora_fim_ref}')
        logger.info(f"Campo 'Data Final' preenchido com: {data_final_ajustada} {hora_fim_ref}")
        page.click("button[type='submit']")
        page.wait_for_timeout(2000)
        elemento_registros = page.locator("td.ng-binding:has-text('registros encontrados.')")
        elemento_registros.scroll_into_view_if_needed()
        texto_completo = elemento_registros.text_content()
        busca_numero = re.search(r'\d+', texto_completo)
        if busca_numero:
            total_registros = int(busca_numero.group())
            logger.info(f"Total de registros encontrados: {total_registros}")
        else:
            total_registros = 0
            logger.warning("Nenhum número de registro foi localizado no texto.")
        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "r", encoding="utf-8") as o:
            info_incidente = json.load(o)
        info_incidente['perda_media'] = total_registros
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(info_incidente, f, ensure_ascii=False, indent=4)

        page.close()

    except Exception:
          logger.exception(f"Erro no calculo de perda.")


