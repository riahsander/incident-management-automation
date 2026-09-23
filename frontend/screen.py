"""
Interface gráfica da automação de incidentes.

O módulo utiliza Tkinter para disponibilizar as interfaces responsáveis
pela interação com o usuário durante os fluxos de registro e finalização
de incidentes.

Responsabilidades:
    - Permitir a seleção da operação desejada.
    - Coletar os dados necessários para registrar um incidente.
    - Coletar os dados necessários para finalizar um incidente.
    - Validar o preenchimento dos campos obrigatórios.
    - Persistir temporariamente as informações coletadas em JSON.

As informações retornadas pelas interfaces são utilizadas pelo módulo
principal para dar continuidade aos respectivos fluxos da automação.
"""

from backend.path_utils import get_path
from backend.logger_config import logger

import tkinter as tk
from tkinter import ttk, messagebox
import json
from backend.path_utils import get_path
import os
from backend.logger_config import logger

def selecionar_acao():
    """
    Exibe a interface inicial para seleção da operação.

    Permite ao usuário escolher entre registrar ou finalizar um
    incidente.

    Returns:
        str | None: Retorna "registrar" ou "finalizar" conforme
        a opção selecionada. Retorna None caso nenhuma opção seja
        selecionada ou ocorra uma falha.
    """
    logger.info("Iniciando interface de tomada de decisão.")
    try:
        acao = {"tipo": None}

        def registrar():
            acao["tipo"] = "registrar"
            janela.destroy()

        def finalizar():
            acao["tipo"] = "finalizar"
            janela.destroy()

        janela = tk.Tk()
        janela.title("Automação Incidente")
        janela.geometry("300x150")

        tk.Label(
            janela,
            text="Selecione a ação desejada",
            font=("Arial", 11, "bold")
        ).pack(pady=15)

        tk.Button(
            janela,
            text="Registrar Incidente",
            width=25,
            command=registrar
        ).pack(pady=5)

        tk.Button(
            janela,
            text="Finalizar Incidente",
            width=25,
            command=finalizar
        ).pack(pady=5)

        janela.mainloop()

        return acao["tipo"]
    except Exception as e:
        logger.exception("Erro na interface inicial: ", e)


def abrir_interface_de_registro():
    """
    Exibe o formulário para coleta dos dados de um novo incidente.

    Campos coletados:
        - Parceiro
        - Tipo de transação
        - Autorizador
        - Status das transações
        - Indisponibilidade
        - Hora de início

    Os campos obrigatórios são validados antes da confirmação.
    Após o preenchimento, os dados são armazenados em
    data/info_incidente.json e retornados para o fluxo principal.

    Returns:
        dict: Informações coletadas para o registro do incidente.
        Retorna um dicionário vazio caso a operação seja cancelada.
    """
    try:
        incidente = {}

        def registrar_incidente():
            """
            Valida e registra as informações de abertura do incidente.

            Coleta os dados preenchidos no formulário de registro,
            valida os campos obrigatórios e atualiza o dicionário do
            incidente.

            Após a validação, as informações são armazenadas em
            data/info_incidente.json e a interface é encerrada.

            Returns:
                None
            """
            parceiro = entry_parceiro.get()
            tipo_transacao = entry_tipo_transacao.get()
            autorizador = entry_autorizador.get()
            status = entry_status.get()
            indisponibilidade = entry_indisponibilidade.get()
            hora_inicio = entry_hora_inicio.get()

            if not parceiro or not autorizador or not status or not indisponibilidade or not hora_inicio:
                messagebox.showwarning("Erro", "Preencha todos os campos corretamente!")
                return

            incidente.update({
                "parceiro": parceiro,
                "tipo_transacao": tipo_transacao,
                "autorizador": autorizador,
                "status": status,
                "indisponibilidade": indisponibilidade,
                "hora_inicio": hora_inicio
            })

            file_path = get_path(os.path.join("data", "info_incidente.json"))
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(incidente, f, ensure_ascii=False, indent=4)

            messagebox.showinfo("Informação", "Dados salvos com sucesso!")
            janela.destroy()


        # Criar janela principal
        janela = tk.Tk()
        janela.title("Formulário de Registro de Incidente")

        # Parceiro
        tk.Label(janela, text="Parceiro:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_parceiro = ttk.Combobox(janela, values=[
            "BANCO_EXEMPLO",
            "OPERADORA_EXEMPLO",
            "PARCEIRO_EXEMPLO"], width=27)
        entry_parceiro.grid(row=0, column=1, padx=5, pady=5)

        # Tipo de transação
        tk.Label(janela, text="Tipo da Transação:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_tipo_transacao = ttk.Combobox(janela, values=["SAQUE", "DEPOSITO", "AMBOS"], width=27)
        entry_tipo_transacao.grid(row=1, column=1, padx=5, pady=5)

        # Autorizador 
        tk.Label(janela, text="Autorizador:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_autorizador =ttk.Combobox(janela, values=["Sim", "Não"], width=27)
        entry_autorizador.grid(row=2, column=1, padx=5, pady=5)

        # Status Transações
        tk.Label(janela, text="Status Transações:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        entry_status = ttk.Combobox(janela, values=["Negadas", "Pendentes", "Desfeitas", "Erro", "Negadas e Pendentes", "Desfeitas e Pendentes"], width=27)
        entry_status.grid(row=3, column=1, padx=5, pady=5)

        # Indisponibilidade
        tk.Label(janela, text="Indisponibilidade:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        entry_indisponibilidade = ttk.Combobox(janela, values=["Total", "Parcial"], width=27)
        entry_indisponibilidade.grid(row=4, column=1, padx=5, pady=5)

        # Hora Início 
        tk.Label(janela, text="Hora Início:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        entry_hora_inicio = tk.Entry(janela, width=30)
        entry_hora_inicio.grid(row=5, column=1, padx=5, pady=5)

        # Botão de salvar
        btn_salvar = tk.Button(janela, text="Salvar", command=registrar_incidente)
        btn_salvar.grid(row=6, column=0, columnspan=2, pady=20)

        logger.info("Informações do incidente coletadas.")
        janela.mainloop()
        return incidente
    except Exception:
        logger.exception("Erro na captura das informações.")


def abrir_interface_de_encerramento():
    """
    Exibe o formulário para coleta dos dados de finalização do incidente.

    Campos coletados:
        - Hora de fim
        - Origem
        - Causa/Resolução
        - Chamado
        - Escopo

    Os campos obrigatórios são validados antes da confirmação.
    Após o preenchimento, os dados são armazenados em
    data/info_incidente.json e retornados para o fluxo principal.

    Returns:
        dict: Informações coletadas para a finalização do incidente.
        Retorna um dicionário vazio caso a operação seja cancelada.
    """
    incidente = {}

    def finalizar_incidente():
        """
        Valida e registra as informações de finalização do incidente.

        Coleta os dados preenchidos no formulário de encerramento,
        valida os campos obrigatórios e atualiza o dicionário do
        incidente.

        Após a validação, as informações são armazenadas em
        data/info_incidente.json e a interface é encerrada.

        Dados processados:
            - Hora de fim
            - Origem
            - Causa/Resolução
            - Chamado
            - Escopo

        Returns:
            None
        """
        hora_fim = entry_hora_fim.get()
        origem = entry_origem.get()
        causa = entry_causa.get()
        chamado = entry_chamado.get()
        escopo = entry_escopo.get()
        

        if  not hora_fim or not origem or not causa or not chamado:
            messagebox.showwarning("Erro", "Preencha todos os campos corretamente!")
            return

        incidente.update({
            "hora_fim": hora_fim,
            "origem": origem,
            "causa": causa,
            "chamado": chamado,
            "escopo": escopo
        })


        file_path = get_path(os.path.join("data", "info_incidente.json"))
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(incidente, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Informação", "Dados salvos com sucesso!")
        janela.destroy()

    janela = tk.Tk()
    janela.title("Formulário de Encerramento de Incidente")


    tk.Label(janela, text="Hora Fim:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_hora_fim = tk.Entry(janela, width=30)
    entry_hora_fim.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(janela, text="Origem:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_origem = ttk.Combobox(janela, values=['EXTERNA', 'INTERNA'], width=30)
    entry_origem.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(janela, text="Causa/Resolução:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_causa = tk.Entry(janela, width=30)
    entry_causa.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(janela, text="Chamado:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_chamado = tk.Entry(janela, width=30)
    entry_chamado.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(janela, text="Escopo:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    entry_escopo = ttk.Combobox(janela,values=['SAQUE', 'DEPOSITO', 'GERAL'], width=30)
    entry_escopo.grid(row=4, column=1, padx=5, pady=5)

    btn_salvar = tk.Button(janela, text="Salvar", command=finalizar_incidente)
    btn_salvar.grid(row=5, column=0, columnspan=2, pady=20)

    janela.mainloop()
    return incidente

