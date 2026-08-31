"""
screen.py

Módulo responsável pela interface gráfica da aplicação.

A interface permite que o usuário registre as informações necessárias
para a abertura e comunicação de um incidente operacional.

As informações coletadas são validadas e armazenadas em um arquivo JSON,
que posteriormente será utilizado pelos demais módulos do sistema.

Campos disponíveis:
    - Parceiro
    - Autorizador
    - Status das transações
    - Tipo de indisponibilidade
    - Horário de início

Arquivo gerado:
    data/info_incidente.json

Tecnologias utilizadas:
    - Tkinter
    - JSON

Fluxo:
    Usuário → Formulário → Validação → Persistência em JSON
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from backend.path_utils import get_path
import os

def abrir_interface():
    """
    Exibe a interface gráfica para registro de incidentes.
     
    Cria uma janela contendo os campos necessários para coleta
    das informações operacionais utilizadas pelo sistema.
     
    Após o preenchimento e confirmação dos dados:
    1. Os campos são validados.
    2. As informações são armazenadas em um dicionário.
    3. Os dados são persistidos em arquivo JSON.
    4. A janela é encerrada.
     
    Returns:
    dict: Dados do incidente informados pelo usuário.
    """
    incidente = {}

    def registrar_incidente():
        """
        Valida e registra os dados informados no formulário.
         
        A função é acionada pelo botão "Salvar" e tem como
        responsabilidade capturar os valores preenchidos pelo
        usuário, validar campos obrigatórios e persistir as
        informações em arquivo JSON.
         
        Validações:
        - Parceiro preenchido.
        - Autorizador preenchido.
        - Status informado.
        - Indisponibilidade informada.
        - Hora de início informada.
         
        Ações executadas:
        - Atualiza o dicionário de incidente.
        - Salva os dados em data/info_incidente.json.
        - Exibe mensagem de sucesso.
        - Encerra a interface.
         
        Returns:
        None
        """
        parceiro = entry_parceiro.get()
        autorizador = entry_autorizador.get()
        status = entry_status.get()
        indisponibilidade = entry_indisponibilidade.get()
        hora_inicio = entry_hora_inicio.get()

        if not parceiro or not autorizador or not status or not indisponibilidade or not hora_inicio:
            messagebox.showwarning("Erro", "Preencha todos os campos corretamente!")
            return

        incidente.update({
            "parceiro": parceiro,
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
    janela.title("Formulário de Transações")

    # Campo para seleção do parceiro afetado.
    tk.Label(janela, text="Parceiro:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_parceiro = ttk.Combobox(janela, values=[
    "BANCO_HORIZONTE",
    "COOPERATIVA_NOVAERA",
    "PROCESSADORA_ORION",
    "BANCO_AMAZONIA_SUL",
    "BANCO_CRISTAL_ATM",
    "BANCO_INOVACAO",
    "BANCO_LITORAL",
    "BANCO_CAPITAL",
    "BANCO_NORTEBRASIL",
    "BANCO_SULFINANCE",
    "BANCO_REGIONAL",
    "BANCO_SUL_CORRESPONDENTE",
    "REDE_ATM_GLOBAL",
    "FINANCEIRA_CENTRAL",
    "PAGAMENTOS_CORPORATIVOS",
    "BANDEIRA_PREMIUM",
    "COOPERATIVA_UNIAO",
    "COOPERATIVA_VALOR",
    "COOPERATIVA_PRIME",
    "SOLUCOES_FINANCEIRAS"
], width=27)
    entry_parceiro.grid(row=0, column=1, padx=5, pady=5)

    # Autorizador 
    tk.Label(janela, text="Autorizador:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_autorizador =ttk.Combobox(janela, values=["Sim", "Não"], width=27)
    entry_autorizador.grid(row=1, column=1, padx=5, pady=5)

    # Status Transações
    tk.Label(janela, text="Status Transações:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_status = ttk.Combobox(janela, values=["Negadas", "Pendentes", "Desfeitas", "Erro", "Negadas e Pendentes", "Desfeitas e Pendentes"], width=27)
    entry_status.grid(row=2, column=1, padx=5, pady=5)

    # Indisponibilidade
    tk.Label(janela, text="Indisponibilidade:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_indisponibilidade = ttk.Combobox(janela, values=["Total", "Parcial"], width=27)
    entry_indisponibilidade.grid(row=3, column=1, padx=5, pady=5)

    # Hora Início 
    tk.Label(janela, text="Hora Início:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    entry_hora_inicio = tk.Entry(janela, width=30)
    entry_hora_inicio.grid(row=4, column=1, padx=5, pady=5)

    # Botão de salvar
    btn_salvar = tk.Button(janela, text="Salvar", command=registrar_incidente)
    btn_salvar.grid(row=5, column=0, columnspan=2, pady=20)


    janela.mainloop()
    return incidente

