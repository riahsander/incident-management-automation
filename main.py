"""
main.py
 
Ponto de entrada da aplicação.
 
Este módulo coordena o fluxo completo de tratamento de incidentes,
integrando interface gráfica, coleta de informações, geração de
evidências e envio de notificações.
 
Fluxo da execução:
1. Coleta os dados do incidente através da interface gráfica.
2. Obtém o identificador do chamado registrado no sistema de gestão.
3. Persiste os dados do incidente em arquivo JSON.
4. Gera evidências visuais (screenshots).
5. Envia a comunicação por e-mail.
 
Módulos envolvidos:
- frontend.screen
- backend.qualitor.abertura_chamado
- backend.gerar_screenshots
- backend.email.envio_email
 
Arquivos gerados:
- data/info_incidente.json
 
Autor:
Riah Sander Cavalheiro
 
Versão:
1.0.1
"""

import json
import os
from frontend.screen import abrir_interface
from backend.gerar_screenshots.geral_function import gerar_screenshot
from backend.email.envio_email import enviar_email
from backend.qualitor.abertura_chamado import pega_chamado
from backend.path_utils import get_path

def main():
    """
    Executa o fluxo principal da aplicação.

    A função centraliza a chamada dos módulos responsáveis pelo
    processamento de um incidente operacional.

    Etapas:
        1. Coleta os dados informados pelo usuário.
        2. Recupera o número do chamado registrado.
        3. Persiste as informações para reutilização.
        4. Gera screenshots para evidência.
        5. Envia a notificação por e-mail.

    Returns:
        None
    """
    # Coleta as informações do incidente através da interface gráfica.
    info_incidente = abrir_interface()

    # Usuário cancelou ou fechou a janela
    if not info_incidente:
        print("Operação cancelada pelo usuário.")
        return
    
    # Obtém o identificador do chamado registrado no sistema.
    chamado = pega_chamado()

    # Salva os dados para consumo dos demais módulos da aplicação.
    file_path = get_path(os.path.join("data", "info_incidente.json"))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(info_incidente, f, ensure_ascii=False, indent=4)

    # Gera as evidências visuais utilizadas na comunicação.
    gerar_screenshot()

    # Monta e envia a notificação de incidente.
    enviar_email(chamado)

if __name__ == "__main__":
    main()
