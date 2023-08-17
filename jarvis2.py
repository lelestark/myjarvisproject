from screeninfo import get_monitors
import threading
from datetime import datetime
import re
import asyncio
import random
from stark_studios_updated import main_window
from voice_assistant import speak, listen, wishMe, get_random_thanks, wake_up_word_detected
from task_manager import load_tasks_from_file, add_task_to_list, remind_upcoming_tasks, capture_shopping_list_item, add_item_to_shopping_list, view_shopping_list, initialize_shopping_list, mark_task_as_completed, view_task_list, add_standard_answer, show_standard_answer
from web_navigation import open_website, search_on_google, noticias, search_images
from system_utilities import move_window_to_monitor, switch_application, test_google_speech_api_latency, get_current_date, get_current_day_of_week, turn_off_computer, open_program, initialize_notes_file, capture_note_idea, save_note_to_file, get_notes_by_category, view_notes
from ai import bing, gpt

emotional_support_phrases = [
    "Estou me sentindo um pouco para baixo hoje. Você pode conversar comigo por um momento?",
    "Estou passando por um momento difícil. Pode me oferecer algum apoio?",
    "Sinto-me sozinho(a) e precisando de alguém para conversar. Você pode me ajudar?",
    "Estou me sentindo sobrecarregado(a). Você tem algum conselho ou palavras de encorajamento?",
    "Estou enfrentando alguns desafios e poderia usar uma palavra amiga. Você pode me ajudar?",
    "Sinto que preciso de alguma orientação ou suporte emocional. Você está disponível para conversar?",
    "Estou me sentindo um pouco perdido(a). Você pode me oferecer alguma orientação ou apoio?",
    "Estou enfrentando algumas dificuldades pessoais e apreciaria sua empatia e apoio.",
    "Estou me sentindo desanimado(a). Você tem alguma história inspiradora ou palavras de motivação?",
    "Preciso de alguém que me entenda e me ofereça suporte emocional. Você pode ser essa pessoa?"
]

def main():
    global tasks
    initialize_notes_file()
    initialize_shopping_list()
    tasks = load_tasks_from_file()
    reminder_thread = threading.Thread(target=remind_upcoming_tasks, args=(tasks,))
    reminder_thread.start()

    while True:  # Loop infinito para wake-up word
        detected_word = wake_up_word_detected()

        if detected_word:
            if detected_word == 'jarvis':
                #wishMe()
                print("Wake-up word detectada: Jarvis. Modo de escuta ativado.")
            elif detected_word == 'friday':
                gpt()
            elif detected_word == 'edith':
                asyncio.run(bing())

            while detected_word == 'jarvis':  
                command = listen().lower()

                if "gerenciador" in command:
                    speak("Abrindo o gerenciador do estúdio de impressão e pintura.")
                    main_window()  # Chame a função para abrir a interface gráfica

                elif "dispensado" in command:
                    print("Modo de escuta desativado. Aguardando wake-up word...")
                    speak("Até logo senhor! Entrando em modo de espera. Precisando de algo, é só chamar.")
                    break

                elif "abrir" in command:
                    open_website(command)

                elif "buscar por" in command:
                    search_on_google(command)

                elif "buscar imagem" in command:
                    search_images(command)

                elif "lista de tarefas" in command:
                    view_task_list(tasks)

                elif "teste" in command:
                    test_google_speech_api_latency()

                elif "adicionar tarefa" in command:
                    add_task_to_list(tasks)

                elif "tarefa completa" in command:
                    speak("Qual tarefa você gostaria de marcar como completa?")
                    task_name = listen().lower()
                    mark_task_as_completed(tasks, task_name)

                if "me ajuda" in command:
                    random_response = random.choice(emotional_support_phrases)
                    gpt(random_response)

                if "anotar" in command or "ideia" in command:
                    idea, category = capture_note_idea()
                    save_note_to_file(idea, category)

                elif "consultar anotações" in command:
                    speak("Qual categoria você gostaria de consultar?")
                    category = listen()
                    get_notes_by_category(category)

                elif "mostrar anotações" in command:
                    view_notes()

                if "adicionar resposta" in command:
                    add_standard_answer()

                elif "mostrar respostas" in command:
                    show_standard_answer()

                if "setar timer" in command:
                    pass

                if "obrigado" in command:
                    random_response = get_random_thanks()
                    print(random_response)
                    speak(random_response)
                        
                if 'quantas horas' in command:
                    strTime = datetime.now().strftime("%H:%M:%S")
                    print(f"Comando 'quantas horas' detectado. Hora atual: {strTime}")  # Linha de depuração
                    speak(f"São {strTime}")

                elif 'notícias' in command:
                    noticias()
                
                if "alt tab" in command:
                    switch_application()

                if "mover" in command and "para monitor" in command:
                    print(f"Comando recebido: {command}")  # Imprime o comando para depuração
                    # Extrai o nome da aplicação e o número do monitor usando uma expressão regular
                    match = re.match(r'mover (.*?) para monitor (\d+)', command)
                    if match:
                        app_name, monitor_number_str = match.groups()
                        monitor_number = int(monitor_number_str) - 1  # Converte para índice (por exemplo, "1" se torna 0, "2" se torna 1, etc.)
                        print(f"Nome da aplicação: {app_name}, Número do Monitor: {monitor_number + 1}")  # Imprime os detalhes extraídos

                        monitors = get_monitors()
                        if 0 <= monitor_number < len(monitors):
                            move_window_to_monitor(app_name, monitor_number)
                            speak(f"A aplicação {app_name} foi movida para o monitor {monitor_number + 1}.")
                        else:
                            speak(f"Desculpe, o monitor {monitor_number + 1} não existe. Por favor, tente novamente.")
                    else:
                        print(f"Erro ao extrair detalhes do comando: {command}")  # Imprime o erro se os detalhes não puderem ser extraídos
                        speak("Desculpe, não consegui entender o comando. Por favor, tente novamente.")

                if "que dia é hoje" in command:
                    get_current_date()
                
                elif "dia da semana" in command:
                    get_current_day_of_week()

                if "abrir programa" in command:
                    program_name = command.replace("abrir programa", "").strip()
                    open_program(program_name)

                elif "desligar computador" in command:
                    turn_off_computer()

                if "adicionar na lista de compras" in command:
                    product, quantity, category = capture_shopping_list_item()
                    add_item_to_shopping_list(product, quantity, category)
                    speak(f"Item {product} adicionado à lista de compras.")

                elif "lista de compras" in command:
                    view_shopping_list()

        else:
            print("Wake-up word não detectada. Tentando novamente...")

if __name__ == "__main__":
    main()

