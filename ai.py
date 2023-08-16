import asyncio, json
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from voice_assistant import speak, listen
import re
import openai

openai.api_key = "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" 

def get_command(assistant_name):
    speak(f"Sistemas operacionais de {assistant_name} online. Aguardando comando.")
    return listen().lower()

async def bing():
    prompt = get_command("EDITH")
    if prompt:
        cookies = json.loads(open("cookies.json", encoding="utf-8").read())  # might omit cookies option
        bot = await Chatbot.create(cookies=cookies)  # Definindo o idioma como português do Brasil
        response = await bot.ask(prompt="Você é um assistente prestativo que deve se comportar como Fiday, a inteligência artificial de Tony Stark. (o prompt emitido até aqui não deve ser mencionado nas respostas)" + prompt, conversation_style=ConversationStyle.precise, simplify_response=True)
        print(json.dumps(response, indent=2))
        bot_response = response["text"]
        q.locale = "pt-BR"
        speak(bot_response)

        if "desconectar" in prompt:
            await bot.close()

def gpt(initial_prompt=None):
    first_call = True  # Adicionar uma variável para rastrear se esta é a primeira chamada

    while True:  # Loop de conversação infinito
        prompt = listen().lower() if initial_prompt is None else initial_prompt
        # Falar a mensagem inicial apenas na primeira chamada e quando não houver prompt inicial
        if first_call and initial_prompt is None:
            speak("Sistemas operacionais de Friday online. Aguardando comando.")

        first_call = False  # Marcar que a primeira chamada foi realizada

        if "desconectar" in prompt:
            speak("Desconectando. Até mais!")
            break

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content":
                "Você é um assistente prestativo que deve se comportar como Friday, a inteligência artificial de Tony Stark."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            n=1,
            stop=["\nUser:"],
        )

        bot_response = response["choices"][0]["message"]["content"]
        speak(bot_response)

        initial_prompt = None  # Resetar o prompt inicial para None após a verificação

        