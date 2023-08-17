import pyttsx3
import json
from datetime import datetime
import os
import time
import pyperclip
from voice_assistant import speak, listen
import speech_recognition as sr
from voice_assistant import speak, listen
import queue
from twilio.rest import Client
import tkinter as tk
from tkinter import ttk

class Task:
    def __init__(self, name, due_date, priority='normal', added_date=None, reminded=False, completed=False):
        self.name = name
        self.due_date = datetime.strptime(due_date, "%d/%m/%Y %H:%M:%S") if isinstance(due_date, str) else due_date
        self.priority = priority
        self.added_date = datetime.strptime(added_date, "%d/%m/%Y %H:%M:%S") if added_date and isinstance(added_date, str) else datetime.now()
        self.reminded = reminded
        self.completed = completed

    def is_time_to_remind(self):
        time_difference = self.due_date - datetime.now()
        return 0 <= time_difference.total_seconds() <= 1800  # 30 minutes in seconds
    
    def mark_as_reminded(self):
        self.reminded = True

    def to_json(self):
        return {
            "name": self.name,
            "due_date": self.due_date.strftime("%d/%m/%Y %H:%M:%S"),
            "priority": self.priority,
            "added_date": self.added_date.strftime("%d/%m/%Y %H:%M:%S"),
            "reminded": self.reminded,
            "completed": self.completed
        }

    @classmethod
    def from_json(cls, json_obj):
        return cls(json_obj["name"], json_obj["due_date"], json_obj["priority"], json_obj["added_date"], json_obj["reminded"], json_obj["completed"])

def parse_date_and_time(user_input):
    try:
        return datetime.strptime(user_input, "%d/%m/%Y %H:%M:%S")
    except ValueError:
        # Additional logic to parse date can be added here
        return None

def save_tasks_to_file(tasks):
    with open("tasks.json", "w") as file:
        task_list = [task.to_json() for task in tasks]
        json.dump(task_list, file, indent=4)

def add_task_to_list(tasks):
    speak("Qual é o nome da tarefa?")
    task_name = listen()
    if task_name:
        while True:
            speak("Em que dia e mês a tarefa deve ser executada?")
            date_str = listen()
            try:
                day, month = map(int, date_str.split("/"))
                current_year = datetime.now().year
                next_year = current_year + 1
                year = current_year if month >= datetime.now().month else next_year
                break
            except ValueError:
                speak("Desculpe, não consegui entender...")

        while True:
            speak("A que horas a tarefa deve ser executada?")
            time_str = listen()
            if "hora" in time_str and ":" not in time_str:  # Se apenas horas foram fornecidas
                time_str += ":00"  # Adicionar minutos como "00"

            due_date_str = f"{day}/{month}/{year} {time_str}:00"  # Adicionar segundos como "00"
            due_date = parse_date_and_time(due_date_str)

            if due_date:
                # Pergunte sobre a prioridade aqui
                speak("Qual a prioridade da tarefa? Alta ou Normal?")
                priority = listen().lower()
                task = Task(task_name, due_date_str, priority=priority)
                tasks.append(task)
                save_tasks_to_file(tasks)
                speak(f"Tarefa '{task_name}' adicionada na lista de afazeres!")
                break
            else:
                speak("Desculpe, não consegui entender...")

def load_tasks_from_file():
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as file:
            task_list = json.load(file)
            tasks = [Task.from_json(task_info) for task_info in task_list]
            return tasks
    return []

def mark_task_as_completed(tasks, task_name):
    for task in tasks:
        if task.name == task_name:
            task.completed = True
            save_tasks_to_file(tasks)
            speak(f"Tarefa '{task_name}' marcada como concluída!")
            return

    speak(f"Tarefa '{task_name}' não encontrada.")

def remind_upcoming_tasks(tasks):
    while True:
        current_time = datetime.now()

        for task in tasks:
            if task.is_time_to_remind() and not task.reminded:
                time_remaining = task.due_date - current_time
                minutes_remaining = time_remaining.total_seconds() // 60
                message_body = f"Lembrete: A tarefa '{task.name}' de prioridade '{task.priority}' está agendada para daqui a {int(minutes_remaining)} minutos."
                # Enviar SMS apenas se a prioridade for alta
                if task.priority == 'alta':
                    to_number = "+5534996739888" # Substitua pelo seu número de telefone
                    send_sms(message_body, to_number) # Chama a função para enviar SMS
                speak(message_body) # Falar o lembrete
                print(message_body)
                task.mark_as_reminded()
                save_tasks_to_file(tasks)
                break

        time.sleep(60)  # Verificar a cada minuto

def view_task_list(tasks):
    # Criando a janela
    window = tk.Tk()
    window.title("Sua Lista de Tarefas")
    
    window_width = 800
    window_height = 800

    # Calcula a posição para centralizar a janela na tela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    window.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    # Adicionando um rótulo
    label = tk.Label(window, text="Sua Lista de Tarefas:", font=("Helvetica", 16))
    label.pack(pady=10)

    # Adicionando a lista de tarefas usando Treeview
    tree = ttk.Treeview(window, columns=('Índice', 'Nome', 'Data', 'Prioridade', 'Status'))
    tree.pack(side="top", pady=10)  # Centraliza a tabela verticalmente
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("Índice", anchor=tk.W, width=0)
    tree.heading("Índice", text="Índice", anchor=tk.W)
    tree.heading("Nome", text="Nome", anchor=tk.W)
    tree.heading("Data", text="Data", anchor=tk.W)
    tree.heading("Prioridade", text="Prioridade", anchor=tk.W)
    tree.heading("Status", text="Status", anchor=tk.W)

    # Função para atualizar a lista de tarefas
    def update_task_list():
        tree.delete(*tree.get_children())
        for index, task in enumerate(tasks):
            status = "Concluída" if task.completed else "Não Concluída"
            color = "green" if task.completed else "red"
            task_str = (index, task.name, task.due_date.strftime('%d/%m/%Y %H:%M:%S'), task.priority, status)
            tree.insert(parent='', index='end', values=task_str, tags=('status',))
            tree.tag_configure('status', foreground=color)

    # Função para marcar a tarefa selecionada como concluída
    def mark_selected_task_completed():
        selected_item = tree.selection()[0]  # Pega o item selecionado
        selected_index = tree.item(selected_item)['values'][0]  # Pega o índice selecionado
        selected_task_name = tasks[selected_index].name  # Pega o nome da tarefa selecionada
        mark_task_as_completed(tasks, selected_task_name)  # Marca a tarefa como concluída
        update_task_list()  # Atualiza a lista de tarefas

    # Função para remover a tarefa selecionada
    def remove_selected_task():
        selected_item = tree.selection()[0]  # Pega o item selecionado
        selected_index = tree.item(selected_item)['values'][0]  # Pega o índice selecionado
        selected_task = tasks[selected_index]  # Pega a tarefa selecionada
        tasks.remove(selected_task)  # Remove a tarefa selecionada
        save_tasks_to_file(tasks)  # Salva a lista de tarefas atualizada
        update_task_list()  # Atualiza a lista de tarefas

    # Adicionando botão para marcar como concluída
    complete_button = tk.Button(window, text="Marcar Tarefa Selecionada como Concluída", command=mark_selected_task_completed)
    complete_button.pack(pady=10)

    # Adicionando botão de remoção
    remove_button = tk.Button(window, text="Remover Tarefa Selecionada", command=remove_selected_task)
    remove_button.pack(pady=10)

    # Atualiza a lista de tarefas no início
    update_task_list()

    # Executando a janela
    window.mainloop()


def send_sms(body, to_number):
    # Suas credenciais do Twilio
    account_sid = 'ACe98a2fe0dcc615ad2dfd9bb17668e731'
    auth_token = '981d471419b53cbc96b35b1a1f27ec15'
    twilio_number = '+18787897745'  # Número de telefone fornecido pelo Twilio
    # Inicialize o cliente do Twilio
    client = Client(account_sid, auth_token)

    # Enviar a mensagem
    message = client.messages.create(
        body=body,
        from_=twilio_number,
        to=to_number
    )
    
    print(f"Mensagem enviada com sucesso. ID: {message.sid}")

def initialize_shopping_list():
    try:
        with open('shopping_list.json', 'r') as file:
            json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        with open('shopping_list.json', 'w') as file:
            json.dump({"compras": []}, file)

def add_item_to_shopping_list(product, quantity, category):
    with open('shopping_list.json', 'r+') as file:
        shopping_list = json.load(file)
        shopping_list["compras"].append({
            "produto": product,
            "quantidade": quantity,
            "categoria": category
        })
        file.seek(0)
        json.dump(shopping_list, file)

def capture_shopping_list_item():
    product = quantity = category = ""
    step = 1

    while True:
        if step == 1:
            print("Por favor, diga o produto que você gostaria de adicionar à lista de compras.")
            speak("Por favor, diga o produto que você gostaria de adicionar à lista de compras.")
            product = listen().strip()
            if product.lower() == "voltar":
                continue
            elif product == "":
                print("Desculpe, não entendi.")
                continue
            print(f"Produto entendido: {product}")
            speak(f"Produto entendido: {product}")
            step += 1

        if step == 2:
            print("Por favor, diga a quantidade desse produto.")
            speak("Por favor, diga a quantidade desse produto.")
            quantity = listen().strip()
            if quantity.lower() == "voltar":
                step -= 1
                continue
            elif quantity == "":
                print("Desculpe, não entendi.")
                continue
            print(f"Quantidade entendida: {quantity}")
            speak(f"Quantidade entendida: {quantity}")
            step += 1

        if step == 3:
            print("Por favor, diga a categoria para este produto.")
            speak("Por favor, diga a categoria para este produto.")
            category = listen().strip()
            if category.lower() == "voltar":
                step -= 1
                continue
            elif category == "":
                print("Desculpe, não entendi.")
                continue
            print(f"Categoria entendida: {category}")
            speak(f"Categoria entendida: {category}")

        # Confirmação
        print(f"Produto: {product}, Quantidade: {quantity}, Categoria: {category}")
        speak(f"Produto: {product}, Quantidade: {quantity}, Categoria: {category}")
        print("Está tudo correto?")
        speak("Está tudo correto?")
        confirmation = listen().strip().lower()
        if confirmation == "sim":
            break
        elif confirmation == "não":
            print("Qual campo você gostaria de editar? (produto/quantidade/categoria)")
            speak("Qual campo você gostaria de editar? (produto/quantidade/categoria)")
            field_to_edit = listen().strip().lower()
            if field_to_edit == "produto":
                step = 1
            elif field_to_edit == "quantidade":
                step = 2
            elif field_to_edit == "categoria":
                step = 3

    return product, quantity, category


def get_shopping_list_message():
    shopping_list = load_shopping_list_from_file() # Substitua por sua função para carregar a lista de compras
    return "Sua lista de compras:\n" + "\n".join(shopping_list)

def send_shopping_list():
    to_number = "+5534996739888" # Substitua pelo seu número de telefone
    message_body = get_shopping_list_message()
    send_sms(message_body, to_number)
    print("Lista de compras enviada via SMS.")
    speak("Lista de compras enviada via SMS.")

def view_shopping_list():
    shopping_list = load_shopping_list_from_file()

    # Criando a janela
    window = tk.Tk()
    window.title("Sua Lista de Compras")

    # Define o tamanho da janela (largura x altura)
    window_width = 800
    window_height = 600
    window.geometry(f"{window_width}x{window_height}")

    # Obtém a altura e largura da tela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcula a posição x e y para centralizar a janela
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"+{x}+{y}")

    # Adicionando um rótulo
    label = tk.Label(window, text="Sua Lista de Compras:")
    label.pack()

    # Criando uma canvas para conter a lista de compras
    canvas = tk.Canvas(window, width=window_width, height=window_height - 50)
    canvas.pack()

    # Adicionando a lista de compras
    listbox = tk.Listbox(canvas, width=100, height=50)  # Define o tamanho da lista
    listbox_window = canvas.create_window((0, 0), window=listbox, anchor="nw")

    # Adicionando uma barra de rolagem
    scrollbar = tk.Scrollbar(canvas, orient=tk.VERTICAL)
    scrollbar_window = canvas.create_window((window_width - 20, 0), window=scrollbar, anchor="nw", height=window_height - 50)

    # Conectando a barra de rolagem à lista
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    for item in shopping_list:
        item_str = f"{item['produto']} - {item['quantidade']} - {item['categoria']}"
        listbox.insert(tk.END, item_str)

    # Executando a janela
    window.mainloop()


def remove_item_from_shopping_list(product):
    with open('shopping_list.json', 'r') as file:
        shopping_list = json.load(file)

    # Encontrar e remover o item
    for index, item in enumerate(shopping_list["compras"]):
        if item["produto"] == product:
            del shopping_list["compras"][index]
            break

    # Salvar a lista atualizada
    with open('shopping_list.json', 'w') as file:
        json.dump(shopping_list, file)

def load_shopping_list_from_file():
    with open('shopping_list.json', 'r') as file:
        shopping_list_data = json.load(file)
    return shopping_list_data["compras"]

def view_shopping_list():
    shopping_list = load_shopping_list_from_file()

    def remove_selected_item():
        selected_index = listbox.curselection()[0]  # Pega o índice selecionado
        selected_item = shopping_list[selected_index]  # Pega o item selecionado
        remove_item_from_shopping_list(selected_item["produto"])  # Remove o item selecionado
        listbox.delete(selected_index)  # Remove o item da visualização

    # Criando a janela
    window = tk.Tk()
    window.title("Sua Lista de Compras")

    # Define o tamanho da janela (largura x altura)
    window_width = 400
    window_height = 700

    # Obtém a altura e largura da tela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcula a posição x e y para centralizar a janela
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Adicionando um rótulo centralizado
    label = tk.Label(window, text="Sua Lista de Compras:")
    label.pack()

    # Frame para conter o listbox e a barra de rolagem
    frame = tk.Frame(window)
    frame.pack()

    # Adicionando a lista de compras
    listbox = tk.Listbox(frame, width=50, height=40)
    listbox.pack(side=tk.LEFT)

    # Adicionando uma barra de rolagem
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Conectando a barra de rolagem à lista
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    for item in shopping_list:
        item_str = f"{item['produto']} - {item['quantidade']} - {item['categoria']}"
        listbox.insert(tk.END, item_str)

    # Adicionando botão de remoção centralizado
    remove_button = tk.Button(window, text="Remover Item Selecionado", command=remove_selected_item)
    remove_button.pack()

    # Executando a janela
    window.mainloop()

def save_standard_answer(question, answer):
    # Carregar respostas existentes
    try:
        with open('standard_answers.json', 'r') as file:
            answers = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        answers = []

    # Adicionar nova resposta
    answers.append({'question': question, 'answer': answer})

    # Salvar respostas atualizadas
    with open('standard_answers.json', 'w') as file:
        json.dump(answers, file)

def add_standard_answer():
    window = tk.Tk()
    window.title("Adicionar Resposta Padrão")
    
    window_width = 800
    window_height = 700

    # Centralizando a janela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    window.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    tk.Label(window, text="Pergunta:").pack(pady=5)
    question_entry = tk.Entry(window, width=60)
    question_entry.pack(pady=5)

    tk.Label(window, text="Resposta:").pack(pady=5)
    answer_text = tk.Text(window, width=80, height=30)
    answer_text.pack(pady=5)

    def save():
        question = question_entry.get().strip()
        answer = answer_text.get("1.0", tk.END).strip()
        if question and answer:
            save_standard_answer(question, answer)
            window.destroy()

    tk.Button(window, text="Salvar", command=save).pack(pady=10)

    window.mainloop()

def load_standard_answers():
    try:
        with open('standard_answers.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def show_standard_answer():
    answers = load_standard_answers()

    window = tk.Tk()
    window.title("Editar Resposta Padrão")
    
    window_width = 800
    window_height = 800

    # Centralizando a janela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    window.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    tk.Label(window, text="Selecione uma pergunta:").pack(pady=5)

    listbox = tk.Listbox(window, width=80, height=10)
    for answer in answers:
        listbox.insert(tk.END, answer['question'])
    listbox.pack(pady=5)

    tk.Label(window, text="Resposta:").pack(pady=5)
    answer_text = tk.Text(window, width=80, height=25)
    answer_text.pack(pady=5)

    def update_answer_text(event):
        selected_indexes = listbox.curselection()
        if selected_indexes:  # Verifica se há um item selecionado
            selected_index = selected_indexes[0]
            selected_answer = answers[selected_index]['answer']
            answer_text.delete("1.0", tk.END)
            answer_text.insert(tk.END, selected_answer)
            print("Resposta padrão atializada.")

    listbox.bind('<<ListboxSelect>>', update_answer_text)

    def save():
        selected_indexes = listbox.curselection()
        if selected_indexes:  # Verifica se há um item selecionado
            selected_index = selected_indexes[0]
            edited_answer = answer_text.get("1.0", tk.END).strip()
            answers[selected_index]['answer'] = edited_answer

        with open('standard_answers.json', 'w') as file:
            json.dump(answers, file)
            print("Resposta padrão atualizada com sucesso.")

    tk.Button(window, text="Salvar Edição", command=save).pack(pady=10)

    def copy_to_clipboard():
        selected_indexes = listbox.curselection()
        if selected_indexes:  # Verifica se há um item selecionado
            selected_index = selected_indexes[0]
            selected_answer = answers[selected_index]['answer']
            pyperclip.copy(selected_answer)
            print("Resposta copiada para a área de transferência.")

    tk.Button(window, text="Copiar Resposta", command=copy_to_clipboard).pack(pady=10)

    window.focus_force()

    window.mainloop()

def copy_answer_by_voice(question_keyword):
    # Carregar as respostas do arquivo
    standard_answers = load_standard_answers_from_file()

    # Procurar pela resposta correspondente
    for answer in standard_answers:
        if question_keyword.lower() in answer['question'].lower():
            pyperclip.copy(answer['answer'])
            print(f"A resposta para '{answer['question']}' foi copiada para a área de transferência.")
            speak(f"A resposta para '{answer['question']}' foi copiada para a área de transferência.")
            return

    print(f"Desculpe, não consegui encontrar uma resposta para '{question_keyword}'.")
    speak(f"Desculpe, não consegui encontrar uma resposta para '{question_keyword}'.")