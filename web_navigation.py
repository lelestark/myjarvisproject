import webbrowser
import requests
import json
from voice_assistant import speak, listen

def noticias():
    url = 'https://newsapi.org/v2/top-headlines?country=br&apiKey=365241d5c32740d0b316c0d862d09bd5'
    news = requests.get(url).text
    news_dict = json.loads(news)
    arts = news_dict['articles']
    for index, articles in enumerate(arts):
        speak(f"Titulo: {articles['title']}")
        speak(f"Descrição: {articles['description']}")
        print(f"Leia a notícia completa em: {articles['url']}")
        if index == 2:
            break
    speak('Quer ouvir mais notícias?')
    more_news = listen()
    if more_news == 'sim':
        noticias()
    else:
        speak('Vivo para servi-lo! Até a próxima!')

def open_website(command):
    url_mappings = {
        "navegador": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "twitch": "https://www.twitch.tv/",
        "instagram": "https://www.instagram.com",
        "planilha de custos": "https://docs.google.com/spreadsheets/",
        "chat gpt": "https://chat.openai.com/",
        "netflix" : "https://www.netflix.com/",
        "prime video" : "https://www.primevideo.com/",
        "bardo" : "https://bard.google.com/"
    }

    for site, url in url_mappings.items():
        if site in command:
            speak(f"Abrindo {site}.")
            webbrowser.open_new_tab(url)
            break  # Sair do loop após encontrar o primeiro site correspondente

def search_on_google(command):
    search_query = command.replace("buscar por", "").strip()
    speak(f"Buscando por {search_query}.")
    webbrowser.open_new_tab(f"https://www.google.com/search?q={search_query}")

def search_images(command):
    search_query = command.replace("buscar imagem", "").strip()
    speak(f"Buscando por {search_query}.")
    url = f"https://www.google.com/search?tbm=isch&q={search_query}"
    webbrowser.open_new_tab(url)