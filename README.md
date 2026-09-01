# Sistema de Monitoramento e Comunicação de Incidentes

Projeto desenvolvido em Python para automatizar o registro, documentação e comunicação de incidentes operacionais.

A aplicação centraliza a coleta de informações, registra ocorrências em uma plataforma de chamados, gera evidências visuais automaticamente e prepara comunicações para as equipes responsáveis.

Essa automação ainda está em estágio inicial, no futuro será feito correções, atualizações e melhorias. 

Futuras melhorias: Adicionar um criador de logs para facilitar a identificação de erros, integrar o preenchimento de planilhas Excel e automatizar o envio de mensagens via Teams.

> **Importante**
>
> Esta é uma versão demonstrativa do projeto.
> Todos os clientes, operadoras, destinatários, URLs, credenciais e demais informações corporativas foram anonimizados e substituídos por dados fictícios para fins de portfólio.

---

# Objetivo

O objetivo da automação é reduzir o tempo de tratamento de incidentes através da integração entre:

- Registro de informações
- Abertura de chamados
- Captura de evidências
- Comunicação por e-mail

Todo o processo é executado de forma automatizada a partir de um único formulário.

---

# Funcionalidades

✅ Interface gráfica para registro de incidentes

✅ Persistência das informações em JSON

✅ Integração com plataforma de chamados via Playwright

✅ Geração automática de evidências operacionais

✅ Geração automática de gráficos transacionais

✅ Atualização automática dos dados do incidente

✅ Preparação de comunicação via Microsoft Outlook

✅ Inclusão automática de anexos

✅ Compatibilidade com execução local e executável (.exe)

---

# Tecnologias Utilizadas

- Python
- Tkinter
- Playwright
- PyWin32 (Outlook)
- JSON
- Python Dotenv
- PyInstaller

---

# Fluxo da Aplicação

```text
Usuário
   │
   ▼
Interface de Registro
   │
   ▼
Persistência dos Dados
   │
   ▼
Abertura Automática de Chamado
   │
   ▼
Geração de Evidências
   │
   ├── Screenshot Operacional
   │
   └── Screenshot Transacional
   │
   ▼
Atualização do Incidente
   │
   ▼
Geração do E-mail
   │
   ▼
Outlook
```

---

# Estrutura do Projeto

```text
.
├── main.py
│
├── frontend/
│   └── screen.py
│
├── backend/
│   │
│   ├── email/
│   │   └── envio_email.py
│   │
│   ├── gerar_screenshots/
│   │   ├── geral_function.py
│   │   ├── screenshot_op.py
│   │   └── screenshot_trans.py
│   │
│   ├── qualitor/
│   │   └── abertura_chamado.py
│   │
│   └── path_utils.py
│
├── data/
│   ├── info_incidente.json
│   ├── email_op.json
│   └── operadoras.json
│
└── README.md
```

---

# Módulos

## main.py

Ponto de entrada da aplicação.

Responsável por coordenar todo o fluxo de execução:

- Coleta informações do incidente
- Registra o chamado
- Gera evidências
- Aciona a comunicação

---

## frontend/screen.py

Interface gráfica desenvolvida com Tkinter.

Permite o registro de:

- Parceiro
- Status das transações
- Existência de autorizador
- Tipo de indisponibilidade
- Horário de início

Os dados são armazenados em:

```text
data/info_incidente.json
```

---

## backend/qualitor/abertura_chamado.py

Responsável pela automação da abertura de chamados.

Utiliza Playwright para:

- Realizar login
- Preencher formulários
- Registrar ocorrências
- Obter o identificador do chamado

---

## backend/gerar_screenshots/screenshot_op.py

Responsável pela captura de evidências operacionais.

Principais ações:

- Acesso à plataforma de monitoramento
- Localização do card da operadora
- Captura automática da evidência

Saída:

```text
printOP/
```

---

## backend/gerar_screenshots/screenshot_trans.py

Responsável pela captura de gráficos transacionais.

Principais ações:

- Login automatizado
- Busca do gráfico da operadora
- Captura da imagem

Saída:

```text
printGraf/
```

---

## backend/gerar_screenshots/geral_function.py

Camada de orquestração da geração de evidências.

Responsável por:

- Identificar a operadora
- Gerar screenshots
- Atualizar os caminhos dos arquivos gerados

---

## backend/email/envio_email.py

Responsável pela criação da comunicação do incidente.

Funcionalidades:

- Busca automática dos destinatários
- Montagem do assunto
- Geração do corpo HTML
- Recuperação da assinatura do Outlook
- Inclusão automática de anexos

---

## backend/path_utils.py

Módulo utilitário para gerenciamento de caminhos.

Garantias:

- Compatibilidade com execução local
- Compatibilidade com PyInstaller
- Criação automática de diretórios

---

# Arquivos de Configuração

## info_incidente.json

Armazena os dados coletados durante a execução.

Exemplo:

```json
{
    "parceiro": "BANCO_HORIZONTE",
    "autorizador": "Sim",
    "status": "Pendentes",
    "indisponibilidade": "Parcial",
    "hora_inicio": "08:15"
}
```

---

## email_op.json

Mapeia os destinatários responsáveis por cada parceiro.

---

## operadoras.json

Relaciona parceiros e suas respectivas configurações de monitoramento.

---

# Como Executar

## Clonar o repositório

```bash
git clone [https://github.com/seu-usuario/nome-repositorio.git](https://github.com/riahsander/incident-management-automation.git)
```

## Instalar dependências

```bash
pip install -r requirements.txt
```

## Configurar variáveis de ambiente

Crie um arquivo:

```text
.env
```

Exemplo:

```env
QUALITOR=https://portal-exemplo.com
MON_OPERADORAS=https://monitoramento-exemplo.com
TRANSACIONAL_GRAF=https://grafico-exemplo.com

USER=usuario_exemplo
PASSWORD=senha_exemplo
```

## Executar

```bash
python main.py
```

---

# Aprendizados Demonstrados

Este projeto demonstra conhecimentos em:

- Automação de processos
- Integração entre sistemas
- Manipulação de arquivos JSON
- Desenvolvimento de interfaces gráficas
- Automação Web com Playwright
- Integração com Microsoft Outlook
- Organização de projetos Python
- Tratamento de múltiplos módulos
- Empacotamento com PyInstaller

---

# Autor

**Riah Sander Cavalheiro**

Analista de Monitoria

Projeto desenvolvido para fins de estudo, automação de processos e demonstração técnica em portfólio.
