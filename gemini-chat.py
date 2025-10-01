#Matheus Dias de Aviz

#!/usr/bin/env python3
"""
Assistente de Linha de Comando (CLI) para interagir com a API do Google Gemini.
Utiliza a API File para um tratamento robusto de arquivos no modo conversacional.
"""

import google.generativeai as genai
import os
import sys
import argparse
from dotenv import load_dotenv
import time

def save_chat_history(chat, output_file):
    # ... (função inalterada)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Histórico da Conversa com Gemini\n\n")
            for message in chat.history:
                role = "🧑 Você" if message.role == "user" else "🤖 Gemini"
                # Garante que a parte de texto exista antes de tentar acessá-la
                if message.parts and hasattr(message.parts[0], 'text'):
                    f.write(f"{role}:\n{message.parts[0].text}\n\n---\n\n")
        print(f"----------------------------------------------\n✅ Histórico da conversa salvo em: {output_file}")
    except Exception as e:
        print(f"----------------------------------------------\n❌ ERRO ao salvar o histórico: {e}")

def main():
    # argparse e configuração da API
    parser = argparse.ArgumentParser(description="Converse com o Gemini AI pelo terminal.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-f', '--file', type=str, help="Caminho do arquivo para usar como contexto (modo de comando único).")
    parser.add_argument('-o', '--output', type=str, help="Caminho do arquivo para salvar a resposta (modo de comando único).")
    parser.add_argument('prompt', nargs='*', help="Prompt inicial da conversa.")
    args = parser.parse_args()
    try:
        dotenv_path = os.path.join(os.path.expanduser('~'), '.env')
        load_dotenv(dotenv_path=dotenv_path)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("ERRO: A variável GOOGLE_API_KEY não foi encontrada no arquivo ~/.env")
            sys.exit(1)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        print(f"Ocorreu um erro na configuração: {e}")
        sys.exit(1)

    if args.file or args.output:
        # --- MODO DE COMANDO ÚNICO  ---
        print("Executando em modo de comando único...")
        file_content = ""
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f: file_content = f.read()
        user_prompt = " ".join(args.prompt)
        final_prompt = user_prompt
        if file_content and user_prompt:
            final_prompt = (f"Use o texto a seguir como contexto para responder à pergunta.\n\nCONTEXTO:\n---\n{file_content}\n---\n\nPERGUNTA: {user_prompt}")
        elif file_content:
            final_prompt = f"Faça um resumo do seguinte texto:\n\n---\n{file_content}\n---"
        response = model.generate_content(final_prompt)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f: f.write(response.text)
            print(f"----------------------------------------------\n✅ Resposta salva com sucesso em: {args.output}")
        else:
            print(response.text)
    else:
        # --- MODO CONVERSACIONAL com API File ---
        chat = model.start_chat(history=[])
        print("▶️ Iniciando conversa com Gemini. Digite /help para ver os comandos.")
        print("-" * 30)

        initial_prompt = " ".join(args.prompt)
        if initial_prompt:
            print(f"🧑 Você: {initial_prompt}")
            response = chat.send_message(initial_prompt)
            print(f"----------------------------------------------\n🤖 Gemini: {response.text}")

        uploaded_file_context = None # Variável para armazenar o "ticket" do arquivo

        while True:
            prompt_input = input("🧑 Você: ")
            
            if prompt_input.startswith('/'):
                command_parts = prompt_input.strip().split(' ', 1)
                command = command_parts[0]

                if command in ['/exit', '/quit', '/sair']:
                    print("🛑 Até logo!👋")
                    break
                
                elif command == '/help':
                    print("------------------- Comandos Disponíveis -------------------")
                    print("/load <arquivo>             - Faz 'upload' de um arquivo para a próxima pergunta.")
                    print("/save <arquivo>             - Salva o histórico da conversa.")
                    print("/help                       - Mostra esta ajuda.")
                    print("/exit, /quit, /sair         - Encerra a conversa.")
                    print("----------------------------------------------------------")
                    continue

                elif command == '/load':
                    if len(command_parts) < 2:
                        print("----------------------------------------------\n⚠️ Uso: /load <caminho_do_arquivo>")
                        continue
                    
                    file_path = command_parts[1]
                    try:
                        print(f"----------------------------------------------\n🔄 Fazendo upload de '{os.path.basename(file_path)}' para o Gemini...")
                        # RESPONSÁVEL POR PASSAR OS ARQUIVOS NA CONVERSA
                        uploaded_file = genai.upload_file(path=file_path)
                        uploaded_file_context = uploaded_file # Armazena o "ticket"
                        print(f"✅ Arquivo processado e pronto. Faça sua pergunta sobre ele na próxima mensagem.")
                    except FileNotFoundError:
                        print(f"----------------------------------------------\n❌ ERRO: Arquivo não encontrado em '{file_path}'")
                    except Exception as e:
                        print(f"----------------------------------------------\n❌ ERRO durante o upload: {e}")
                    continue

                # Exportar coversa
                elif command == '/save':
                    if len(command_parts) > 1:
                        save_chat_history(chat, command_parts[1])
                    else:
                        print("----------------------------------------------\n⚠️ Uso: /save <caminho_do_arquivo>")
                    continue
                else:
                    print(f"----------------------------------------------\n❌ Comando desconhecido: '{command}'.")
                    continue

            # --- Lógica de envio de mensagem ---
            if not prompt_input.strip():
                continue
            
            # Verifica se há um arquivo para ser enviado junto com o prompt
            if uploaded_file_context:
                # Envia o prompt de texto E o "ticket" do arquivo juntos
                response = chat.send_message([prompt_input, uploaded_file_context])
                uploaded_file_context = None # Limpa o contexto para a próxima mensagem ser normal
            else:
                # Envia apenas o prompt de texto
                response = chat.send_message(prompt_input)
            
            print(f"----------------------------------------------\n🤖 Gemini: {response.text}")

if __name__ == "__main__":
    main()
