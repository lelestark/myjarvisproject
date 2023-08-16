import pyautogui
import pygetwindow as gw
import speech_recognition as sr
import time
import requests
import re
import subprocess
import os
import json
import tkinter as tk
from screeninfo import get_monitors
from tkinter import ttk
from datetime import timedelta
from collections import defaultdict
from datetime import datetime
from voice_assistant import speak, listen

PROGRAMS = {
    'bloco de notas': 'C:\\Windows\\System32\\notepad.exe',
    'calculadora': 'C:\\Windows\\System32\\calc.exe',
    'lychee': 'C:\\Windows\\System32\\calc.exe',
    'liche': 'C:\\Windows\\System32\\calc.exe',
    'prusa': 'C:\\Windows\\System32\\calc.exe',
    'laser': 'C:\\Windows\\System32\\calc.exe',
    'referências': 'C:\\Windows\\System32\\calc.exe',
    'fusion': 'C:\\Windows\\System32\\calc.exe',
    'illustrator': 'C:\\Windows\\System32\\calc.exe',
    'photoshop': 'C:\\Windows\\System32\\calc.exe',
    'vs code': 'C:\\Windows\\System32\\calc.exe',
    'whatsapp': 'C:\\Windows\\System32\\calc.exe',
    'discord': 'C:\\Users\\lele_\\AppData\\Local\\Discord\\app-1.0.9013',
    'liga': 'C:\\Windows\\System32\\calc.exe',
    'steam': 'C:\\Windows\\System32\\calc.exe',
    'stim': 'C:\\Windows\\System32\\calc.exe',
    # Adicione mais programas aqui
}

# Caminho para o arquivo JSON onde as anotações serão salvas
NOTES_FILE = 'notes.json'

def test_google_speech_api_latency():
    recognizer = sr.Recognizer()

    print("Teste de Latência da API Google Web Speech")

    while True:
        try:
            with sr.Microphone() as source:
                print("Aguardando comando...")
                recognizer.adjust_for_ambient_noise(source)
                start_time = time.time()
                audio = recognizer.listen(source, timeout=5)
                end_time = time.time()

                try:
                    recognized_text = recognizer.recognize_google(audio, language="pt-BR")
                    latency = end_time - start_time
                    print(f"Texto Reconhecido: {recognized_text}")
                    print(f"Latência: {latency:.2f} segundos")
                except sr.UnknownValueError:
                    print("Não foi possível reconhecer o áudio.")
                except sr.RequestError:
                    print("Erro ao se comunicar com a API do Google.")
                
        except KeyboardInterrupt:
            print("Teste encerrado.")
            break

def move_window_to_monitor(app_name, monitor_number):
    # Obtenha todas as janelas
    all_windows = gw.getAllWindows()

    # Procure por janelas cujo título contenha a palavra ou frase fornecida
    matching_windows = [window for window in all_windows if app_name.lower() in window.title.lower()]

    # Verifique se encontrou alguma janela com o título fornecido
    if not matching_windows:
        print(f"Janela com o título '{app_name}' não encontrada.")
        return

    window = matching_windows[0]  # Pegue a primeira janela encontrada
    print(f"Janela selecionada: {window.title}")
    print(f"Posição atual da janela: {window.left}, {window.top}")

    # Obtenha as informações do monitor desejado
    monitors = get_monitors()
    monitor = monitors[monitor_number]
    x = monitor.x
    y = monitor.y
    width = monitor.width
    height = monitor.height

    print(f"Movendo para o monitor {monitor_number}: Largura {monitor.width}, Altura {monitor.height}, Esquerda {monitor.x}, Topo {monitor.y}")

    # Mova a janela para o monitor desejado
    window.moveTo(x, y)
    window.resizeTo(width, height)
    window.activate()
    print(f"Nova posição da janela: {window.left}, {window.top}")
    print(f"Janela '{app_name}' movida para o monitor {monitor_number + 1}.")

def switch_application() -> None:
    pyautogui.keyDown("alt")
    pyautogui.press("tab")
    pyautogui.keyUp("alt")

def extract_action_and_city(command):
    match = re.search(r'(clima|previsão do tempo)(?: para| em)?\s*(.*)', command, re.IGNORECASE)
    if match:
        action = match.group(1)
        city_name = match.group(2).strip()
        return action, city_name
    return None, None

def clima(city_name):
    api_key = "888df64ddd77794f931b604710c82cc5"
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name + "&units=metric&lang=pt"
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]
        current_humidiy = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        speak(" Temperatura é de " +
            str(current_temperature) +
            "\n A porcentagem de humidade do ar é de " +
            str(current_humidiy) +
            "\n Descrição  " +
            str(weather_description))

def previsao_tempo(city_name):
    api_key = "888df64ddd77794f931b604710c82cc5"
    base_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units=metric&lang=pt"
    response = requests.get(base_url)
    data = response.json()

    if data["cod"] != "404":
        # Data de amanhã
        tomorrow_date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        temperatures = []
        humidity = []
        
        # Agregando as previsões de amanhã
        for forecast in data["list"]:
            time_str = forecast["dt_txt"]
            date_str = time_str.split()[0]
            if date_str == tomorrow_date:
                temperatures.append(forecast["main"]["temp"])
                humidity.append(forecast["main"]["humidity"])  # Acessando a umidade
        
        # Calculando a média diária e fornecendo a previsão
        avg_temperature = sum(temperatures) / len(temperatures)
        avg_humidity = sum(humidity) / len(humidity)  # Calculando a umidade média
        date_obj = datetime.strptime(tomorrow_date, "%Y-%m-%d")
        formatted_date = format_date(date_obj)  # Usando a função de formatação de data
        speak(f"Previsão para {formatted_date}: temperatura média de {avg_temperature:.1f}°C, com umidade média de {avg_humidity:.1f}%.")
    else:
        speak("Cidade não encontrada. Por favor, tente novamente.")

def format_date(date):
    formatted_date = date.strftime("%d de %B de %Y")
    
    meses = {
        "January": "janeiro", "February": "fevereiro", "March": "março",
        "April": "abril", "May": "maio", "June": "junho",
        "July": "julho", "August": "agosto", "September": "setembro",
        "October": "outubro", "November": "novembro", "December": "dezembro"
    }
    
    for eng, pt in meses.items():
        formatted_date = formatted_date.replace(eng, pt)

    return formatted_date

def get_current_date():
    now = datetime.datetime.now()
    dia = now.strftime("%d/%m/%Y")
    if dia:
        speak(f"Data de hoje é {now.strftime('%d/%m/%Y')}")

def get_current_day_of_week():
    now = datetime.datetime.now()
    dia = now.strftime("%A")
    if dia:
        speak("Data de hoje é" + dia)

def open_program(program_name: str) -> None:
    program_path = PROGRAMS.get(program_name.lower())
    if program_path:
        subprocess.Popen(program_path)
        print(f"{program_name} aberto com sucesso!")
    else:
        print(f"Programa '{program_name}' não encontrado.")

def turn_off_computer() -> None:
    os.system("shutdown /s /t 0")

def initialize_notes_file():
    try:
        with open('notes.json', 'r') as file:
            json.load(file)  # Tentar ler o arquivo para verificar se ele é válido
    except FileNotFoundError:
        with open('notes.json', 'w') as file:
            json.dump([], file)  # Criar um arquivo com uma lista vazia se ele não existir
    except json.JSONDecodeError:
        with open('notes.json', 'w') as file:
            json.dump([], file)  # Sobrescrever o arquivo com uma lista vazia se ele estiver corrompido

def capture_note_idea():
    while True:  # Loop infinito até que uma entrada válida seja fornecida
        print("Por favor, diga a ideia que você gostaria de anotar.")
        speak("Por favor, diga a ideia que você gostaria de anotar.")
        idea = listen().strip()
        if idea:  # Verifica se a ideia não está vazia
            break
        else:
            print("Desculpe, não consegui entender sua ideia. Por favor, tente novamente.")
            speak("Desculpe, não consegui entender sua ideia. Por favor, tente novamente.")

    while True:  # Loop infinito até que uma entrada válida seja fornecida
        print("Por favor, diga a categoria para esta ideia.")
        speak("Por favor, diga a categoria para esta ideia.")
        category = listen().strip()
        if category:  # Verifica se a categoria não está vazia
            break
        else:
            print("Desculpe, não consegui entender a categoria. Por favor, tente novamente.")
            speak("Desculpe, não consegui entender a categoria. Por favor, tente novamente.")

    return idea, category

def save_note_to_file(idea, category):
    note = {
        "idea": idea,
        "category": category,
        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    with open('notes.json', 'r+') as file:
        notes = json.load(file)
        notes.append(note)  # Adicionar a nova nota à lista de notas
        file.seek(0)
        json.dump(notes, file)
        speak("Anotação salva. O senhor é um gênio senhor Stark!")

def get_notes_by_category(category: str) -> None:
    try:
        with open(NOTES_FILE, 'r') as file:
            notes = json.load(file)
    except FileNotFoundError:
        print("Desculpe, não consegui encontrar nenhuma anotação.")
        return

    filtered_notes = [note for note in notes if note['category'].lower() == category.lower()]

    if filtered_notes:
        output_file_path = os.path.join(os.getcwd(), f'{category}_notes.txt')
        with open(output_file_path, 'w') as file:
            for note in filtered_notes:
                file.write(f"Ideia: {note['idea']}\nCategoria: {note['category']}\nData: {note['date']}\n\n")

        print(f"Anotações na categoria {category} foram salvas em {output_file_path}")
        speak(f"Anotações na categoria {category} foram salvas em {output_file_path}")
    else:
        print(f"Desculpe, não consegui encontrar anotações na categoria {category}.")
        speak(f"Desculpe, não consegui encontrar anotações na categoria {category}.")

def load_notes_from_file():
    try:
        with open('notes.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def view_notes():
    # Carregar as anotações do arquivo
    notes = load_notes_from_file()

    # Criar a janela
    window = tk.Tk()
    window.title("Sua Lista de Anotações")

    window_width = 800
    window_height = 600

    # Calcula a posição para centralizar a janela na tela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    window.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    # Criar um rótulo para o filtro de categoria
    category_label = tk.Label(window, text="Filtrar por categoria:")
    category_label.pack(pady=10)

    # Criar uma caixa de entrada para o filtro de categoria
    category_entry = tk.Entry(window)
    category_entry.pack(pady=10)

    # Criar uma Treeview para as anotações
    tree = ttk.Treeview(window, columns=("Idea", "Category", "Date"), show="headings")
    tree.heading("Idea", text="Ideia")
    tree.heading("Category", text="Categoria")
    tree.heading("Date", text="Data")
    tree.pack(pady=10)

    # Função para atualizar a lista de anotações
    def update_notes_list():
        category_filter = category_entry.get().strip().lower()
        tree.delete(*tree.get_children())
        for note in notes:
            if not category_filter or note['category'].lower() == category_filter:
                tree.insert("", tk.END, values=(note['idea'], note['category'], note['date']))

    # Função para remover a anotação selecionada
    def remove_selected_note():
        selected_item = tree.selection()[0]
        selected_index = tree.index(selected_item)
        notes.pop(selected_index)
        with open('notes.json', 'w') as file:
            json.dump(notes, file)
        update_notes_list()

    # Adicionar botão para atualizar a lista com o filtro de categoria
    filter_button = tk.Button(window, text="Filtrar", command=update_notes_list)
    filter_button.pack(pady=10)

    # Adicionar botão para remover a anotação selecionada
    remove_button = tk.Button(window, text="Remover Anotação Selecionada", command=remove_selected_note)
    remove_button.pack(pady=10)

    # Atualizar a lista de anotações no início
    update_notes_list()

    # Executar a janela
    window.mainloop()

def extract_hours_and_minutes(command):
    pattern = r"(\d+) horas?(?: e)? ?(\d+)? minutos?"
    match = re.search(pattern, command)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return hours, minutes
    return None, None

def timer_thread(name, duration):
    hours, minutes = divmod(duration, 60)
    print(f"Timer '{name}' setado para {hours} horas e {minutes} mintos.")
    time.sleep(duration * 60)
    speak(f"Timer '{name}' terminou!")

def set_timer(name, hours, minutes):
    duration = hours * 60 + minutes
    if duration <= 0:
        speak("Por favor, forneça um tempo válido em horas e minutos.")
        return

    timer_thread = threading.Thread(target=timer_thread, args=(name, duration))
    timer_thread.start()
    speak(f"Timer '{name}' setado para {hours} horas e {minutes} minutos.")