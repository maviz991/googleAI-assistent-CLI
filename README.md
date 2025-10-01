# googleAI-assistent-CLI
Gemini assitente via API no terminal

# Criando um Assistente Gemini na Linha de Comando (CLI)

Este guia esquematiza os passos para criar um comando global `gemini` no seu terminal Linux (Debian/WSL) para interagir com a API do Google Gemini.

#### Pré-requisitos
- Python 3 e `pip3` instalados.
- Uma API Key do Google AI Studio.
- Ambiente Linux (Usei WSL com Debian ou similar).

#### Passo 1: Configuração da Chave de API
Crie um arquivo `.env` no seu diretório home para armazenar a chave de forma segura.

```bash
# Substitua SUA_API_KEY_AQUI pela sua chave real
echo 'GOOGLE_API_KEY="SUA_API_KEY_AQUI"' > ~/.env
```
Crie sua Google AI Studio key aqui ['Google IA Studio API Key'](https://aistudio.google.com/app/apikey)
#### Passo 2: O Script Python (`gemini-chat.py`)
Crie o arquivo [`gemini-chat.py`](/gemini-chat.py) (em uma pasta de projetos) com o código Python final que se conecta à API, lê argumentos e gerencia a conversa. *Use o código completo da resposta anterior.*

#### Passo 3: Instalação das Dependências Globais
Para que o comando funcione de qualquer lugar, as bibliotecas precisam ser instaladas no ambiente Python global do sistema.

```bash
pip3 install google-generativeai python-dotenv
```

#### Passo 4: Transformando o Script em Comando Global

1.  **Dar Permissão de Execução:**
    ```bash
    # Navegue até a pasta onde salvou o script
    chmod +x gemini-chat.py
    ```

2.  **Garantir que o Diretório de Binários Locais está no PATH:**
    O diretório `~/.local/bin` é o local padrão para scripts de usuário.
    ```bash
    # Adiciona a linha ao seu .bashrc se ela não existir
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    # Recarrega o terminal para aplicar a mudança
    source ~/.bashrc
    ```

3.  **Criar o Link Simbólico (o comando `gemini`):**
    Isso cria um "atalho" chamado `gemini` dentro da pasta que o sistema usa para encontrar comandos.
    ```bash
    # Execute este comando de dentro da pasta onde está o gemini-chat.py
    ln -s "$(pwd)/gemini-chat.py" ~/.local/bin/gemini
    ```

#### Passo 5: Solução de Problemas Comuns

- **Erro `env: ‘python3\r’: No such file or directory`**:
  - **Causa**: Quebras de linha no formato Windows (CRLF).
  - **Solução**: `sudo apt install dos2unix && dos2unix gemini-chat.py`

- **Erro `ModuleNotFoundError: No module named 'google'`**:
  - **Causa**: Bibliotecas instaladas em um `venv` e não no ambiente global.
  - **Solução**: `pip3 install google-generativeai python-dotenv` (sem `venv` ativo).

- **Resposta da IA "Não consigo ler arquivos locais"**:
  - **Causa**: O prompt está acionando o "reflexo de segurança" da IA.
  - **Solução**: Ajustar o prompt para ser mais direto, tratando o conteúdo como "contexto" ou "texto", não como um "arquivo". (O script final já faz isso).

---
### Como Usar seu Novo Comando

#### Modo de Comando Único (com flags)

- **Pergunta Rápida:**
  ```bash
  gemini "Qual a capital da Mongólia?"
  ```
- **Resumir um Arquivo:**
  ```bash
  gemini -f ./meu_script.js
  ```
- **Fazer uma Pergunta sobre um Arquivo:**
  ```bash
  gemini -f ./relatorio.txt "quais foram os principais pontos levantados no terceiro trimestre?"
  ```
- **Salvar a Saída em um Arquivo:**
  ```bash
  gemini -f ./codigo.py "documente esta função em markdown" -o documentacao.md
  ```

#### Modo Conversacional (Interativo)

- **Iniciar uma Conversa:**
  ```bash
  gemini
  ```
- **Comandos Especiais (Dentro do Chat):**
  - **`/load <arquivo> <pergunta>`**: Faz uma pergunta sobre um arquivo e adiciona a análise ao histórico da conversa, permitindo perguntas de acompanhamento.
    ```
    🧑 Você: /load ./meu_codigo.py qual o objetivo principal deste script?
    ```
  - **`/save <arquivo>`**: Salva o histórico completo da conversa atual em um arquivo.
    ```
    🧑 Você: /save minha_conversa.md
    ```
  - **`/help`**: Mostra a lista de comandos disponíveis.
  - **`/exit`, `/quit`, `/sair`**: Encerra a sessão de chat.

---

### Fluxograma
- **Fazer uma Pergunta sobre um Arquivo:**
  ```bash
  gemini quais foram os principais pontos levantados no terceiro trimestre? -f ./relatorio.txt"
  ```

```mermaid
flowchart TD
    A[Início: Comando 'gemini' executado] --> B{Flags -f ou -o usadas?}

    B -- Sim --> C1
    B -- Não --> D1

    subgraph ModoComandoUnico [Modo de Comando Único]
        direction LR
        C1[Lê arquivo se -f] --> C2[Monta prompt robusto]
        C2 --> C3["Chama model.generate_content()"]
        C3 --> C4{Flag -o usada?}
        C4 -- Sim --> C5[Salva resposta em arquivo]
        C4 -- Não --> C6[Exibe resposta no terminal]
    end

    subgraph ModoConversacional [Modo Conversacional]
        D1[Inicia loop de chat] --> D2{Input começa com '/'}
        
        D2 -- Não --> D3{Contexto de arquivo carregado?}
        D3 -- Sim --> D4[Envia prompt + Objeto do Arquivo]
        D4 --> D5[Limpa contexto do arquivo]
        D5 --> D6[Exibe resposta da IA]
        D6 --> D1
        D3 -- Não --> D7[Envia somente o prompt de texto]
        D7 --> D6

        D2 -- Sim --> D8{Qual comando?}
        D8 -- /load --> D9[Faz Upload do Arquivo via API File]
        D9 --> D10[Armazena objeto do arquivo em contexto]
        D10 --> D1
        
        D8 -- /save --> D11[Salva histórico]
        D11 --> D1
        
        D8 -- /help --> D12[Mostra ajuda]
        D12 --> D1
        
        D8 -- /exit --> Fim([Fim do Programa])
    end

    C5 --> Fim
    C6 --> Fim

