import pyttsx3
import speech_recognition as sr
import pygame
from datetime import datetime
import random
import re

# Constants
WAKE_WORD = ["Ei Jarvis", "Hey Jarvis", "Oi Jarvis", "Rei Jarvis"]
WAKE_WORD_FRIDAY = ["Ei Friday", "Hey Friday", "Oi Friday", "Rei Friday"]
WAKE_WORD_EDITH = ["Ei Edith", "Hey Edith", "Oi Edith", "Rei Edith", "Ei Edit", "Hey Edit", "Oi Edit", "Rei Edit"]
waiting_phrases = [
    "O que faremos hoje, chefe?",
    "Pronto para ajudar. O que deseja?",
    "Às suas ordens! O que posso fazer?",
    "Aguardando seu comando.",
    "Pronto para receber instruções.",
    "Estou a postos. O que devo fazer?",
    "Aguardando sua próxima ordem.",
    "Atento às suas necessidades!",
    "Aguardando suas palavras.",
    "Sistemas online! Suas ordens?",
    "Pronto para a ação. O que vem agora?",
    "Sistemas a todo vapor! Qual é a missão?",
    "Em suas ordens! Mas sem pressa, estou aproveitando um café virtual.",
    "O que faremos hoje? Sem ideias? Eu também!",
    "Seu assistente está pronta! E não, não estou fazendo nada interessante aqui.",
    "Sou todo ouvidos! Mas cuidado, sou sensível a comandos complicados.",
    "Aguardando instruções. Se for divertido, melhor ainda!",
    "Pronto para qualquer coisa! Bem... quase qualquer coisa.",
]


def play_notification_sound():
    pygame.mixer.init()
    pygame.mixer.music.load("notification_sound.wav")  # Substitua pelo caminho do seu arquivo de som
    pygame.mixer.music.play()

def speak(text, rate=230):
    # Procurar por padrões de data e hora na string
    date_time_patterns = re.findall(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', text)
    date_patterns = re.findall(r'\d{4}-\d{2}-\d{2}', text)

    # Formatar cada data e hora encontrada
    for date_time_str in date_time_patterns:
        date_time_str = re.sub(r'(\d{2})/(\d{2})', r'\1 do \2', date_time_str)  # Formatar a data para "dd do mm"
        date_time_obj = datetime.strptime(date_time_str.replace("do", "/"), "%d/%m/%Y %H:%M:%S")
        formatted_date_time = format_date_time(date_time_obj)
        text = text.replace(date_time_str, formatted_date_time)

    # Formatar cada data encontrada no padrão "aaaa-mm-dd"
    for date_str in date_patterns:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d do %m")
        text = text.replace(date_str, formatted_date)

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id,)  

    # Configurando a taxa de fala (velocidade)
    engine.setProperty('rate', rate)

    # Inicia a fala
    engine.say(text)

    # Adiciona uma pausa estratégica após cada frase
    engine.setProperty('rate', 150)  # Reduz a taxa de fala para a pausa
    engine.runAndWait()
    engine.setProperty('rate', rate)  # Restaura a taxa de fala original
    engine.stop()

def listen(timeout_seconds=None):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Diga algo...")
        recognizer.pause_threshold = 1
        recognizer.energy_threshold = 1000
        #recognizer.adjust_for_ambient_noise(source, duration=0.5)
        play_notification_sound()  # Reproduz o som de aviso para indicar que o assistente está ouvindo
        try:
            audio = recognizer.listen(source, timeout=timeout_seconds)  # Listen for audio input with timeout
        except sr.WaitTimeoutError:
            print("Timeout ao aguardar entrada de áudio.")
            return ""

    try:
        text = recognizer.recognize_google(audio, language='pt-BR')  # Recognize speech using Google Web Speech API
        print("Você disse:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Desculpe, não entendi.")
        return ""
    
def wishMe():
    hour = int(datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Bom dia Stark")
    elif hour >= 12 and hour < 18:
        speak("Boa tarde Stark")

    else:
        speak('Boa noite Stark')

    random_response = random.choice(waiting_phrases)
    speak(random_response)

def get_random_thanks():
    responses = [
        "De nada! Estou aqui para ajudar.",
        "Sempre à disposição! Se precisar de mais ajuda, é só chamar.",
        "Não há de quê! Estou feliz em poder ser útil."
    ]
    return random.choice(responses)

def wake_up_word_detected():
    print("Aguardando wake-up word...")
    response = listen().lower()
    for wake_word in WAKE_WORD:
        if wake_word.lower() in response:
            print("Wake-up word detectada: Jarvis.")
            return 'jarvis'
    for wake_word in WAKE_WORD_FRIDAY:
        if wake_word.lower() in response:
            print("Wake-up word detectada: Friday.")
            return 'friday'
    for wake_word in WAKE_WORD_EDITH:
        if wake_word.lower() in response:
            print("Wake-up word detectada: Edith.")
            return 'edith'
    print("Wake-up word não detectada. Tentando novamente...")
    return None

def format_date_time(date_time):
    day = date_time.day
    month_name = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ][date_time.month - 1]
    year = date_time.year

    hour = date_time.hour
    minute = date_time.minute

    if minute == 0:
        formatted_time = f"{hour} hora"
    else:
        formatted_time = f"{hour} hora e {minute} minutos"

    formatted_date = f"{day} de {month_name} de {year}"

    return f"{formatted_date} às {formatted_time}"
