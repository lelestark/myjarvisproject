import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk

class ResinCostCalculator:
    def __init__(self, volume, print_time_hours, resin_price_per_liter, kwh_price, machine_consumption, failure_rate, profit_margin, administrative_costs, machine_hourly_rate):
        self.volume = volume
        self.print_time_minutes = print_time_hours * 60
        self.resin_price_per_liter = resin_price_per_liter
        self.kwh_price = kwh_price
        self.machine_consumption = machine_consumption
        self.failure_rate = failure_rate
        self.profit_margin = profit_margin
        self.administrative_costs = administrative_costs
        self.machine_hourly_rate = machine_hourly_rate
    
    def energy_cost(self):
        return (self.print_time_minutes / 60) * self.kwh_price * self.machine_consumption / 1000

    def calculate_material_cost(self):
        return self.volume * self.resin_price_per_liter

    def calculate_failure_cost(self):
        return (self.calculate_material_cost() + self.energy_cost()) * self.failure_rate / 100

    def total_production_cost(self):
        material_cost = self.calculate_material_cost()
        failure_cost = self.calculate_failure_cost()
        energy_cost = self.energy_cost()
        machine_cost = self.machine_hourly_rate * (self.print_time_minutes / 60)
        return material_cost + failure_cost + energy_cost + machine_cost + self.administrative_costs
    
    def calculate_sale_price(self):
        return self.total_production_cost() * (1 + self.profit_margin / 100)

class PaintingAndFinishingCalculator:
    def __init__(self, salary_goal, days_per_week, hours_per_day, finishing_hours, painting_hours, finishing_materials_cost, painting_materials_cost):
        self.hourly_rate = salary_goal / (days_per_week * hours_per_day * 4) # Calcula a taxa horária com base no salário desejado
        self.finishing_hours = finishing_hours
        self.painting_hours = painting_hours
        self.finishing_materials_cost = finishing_materials_cost
        self.painting_materials_cost = painting_materials_cost

    def total_hours(self):
        return self.finishing_hours + self.painting_hours

    def total_materials_cost(self):
        return self.finishing_materials_cost + self.painting_materials_cost

    def total_service_cost(self):
        return self.total_hours() * self.hourly_rate

    def total_cost(self):
        return self.total_service_cost() + self.total_materials_cost()

class Cliente:
    def __init__(self, nome, telefone, email, social):
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.social = social

    def to_dict(self):
        return {
            "nome": self.nome,
            "telefone": self.telefone,
            "email": self.email,
            "social": self.social
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nome"], data["telefone"], data["email"], data["social"])

class Orcamento:
    next_id = 1
    
    def __init__(self, cliente, descricao_projeto, resin_cost, painting_and_finishing_cost, status="Pendente"):
        self.id = Orcamento.next_id
        Orcamento.next_id += 1
        self.cliente = cliente
        self.descricao_projeto = descricao_projeto
        self.resin_cost = resin_cost
        self.painting_and_finishing_cost = painting_and_finishing_cost
        self.valor_venda = self.calcular_valor_total()
        self.lucro = self.valor_venda - (resin_cost + painting_and_finishing_cost)
        self.status = status

    def to_dict(self):
        return {
            "cliente": self.cliente.to_dict(),
            "descricao_projeto": self.descricao_projeto,
            "resin_cost": self.resin_cost,
            "painting_and_finishing_cost": self.painting_and_finishing_cost,
            "valor_venda": self.valor_venda,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        cliente = Cliente.from_dict(data["cliente"])
        return cls(cliente, data["descricao_projeto"], data["resin_cost"], data["painting_and_finishing_cost"], data["status"])

    def calcular_valor_total(self):
        return self.resin_cost + self.painting_and_finishing_cost

class Venda:
    def __init__(self, orcamento, data_venda, data_despacho=None, codigo_rastreio=None):
        self.orcamento = orcamento
        self.data_venda = datetime.strptime(data_venda, "%d-%m-%Y") if isinstance(data_venda, str) else data_venda
        self.data_despacho = datetime.strptime(data_despacho, "%d-%m-%Y") if isinstance(data_despacho, str) else data_despacho
        self.codigo_rastreio = codigo_rastreio

    def to_dict(self):
        return {
            "orcamento": self.orcamento.to_dict(),
            "data_venda": self.data_venda.strftime("%Y-%m-%d"),
            "data_despacho": self.data_despacho.strftime("%Y-%m-%d") if self.data_despacho else None,
            "codigo_rastreio": self.codigo_rastreio
        }

    @classmethod
    def from_dict(cls, data):
        orcamento = Orcamento.from_dict(data["orcamento"])
        return cls(orcamento, data["data_venda"], data["data_despacho"], data["codigo_rastreio"])

class Gerenciador:
    def __init__(self):
        self.clientes = []
        self.orcamentos = []
        self.vendas = []

    def adicionar_cliente(self, cliente):
        self.clientes.append(cliente)

    def criar_orcamento(self, orcamento):
        self.orcamentos.append(orcamento)

    def registrar_venda(self, venda):
        self.vendas.append(venda)

    def balanco_mensal(self, mes, ano):
        total_vendas = sum(venda.orcamento.valor for venda in self.vendas if venda.data_venda.month == mes and venda.data_venda.year == ano)
        return total_vendas

def save_data(gerenciador, filename="data.json"):
    data = {
        "clientes": [cliente.to_dict() for cliente in gerenciador.clientes],
        "orcamentos": [orcamento.to_dict() for orcamento in gerenciador.orcamentos],
        "vendas": [venda.to_dict() for venda in gerenciador.vendas]
    }
    with open(filename, "w") as file:
        json.dump(data, file)

def load_data(filename="data.json"):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            clientes = [Cliente.from_dict(cliente) for cliente in data["clientes"]]
            orcamentos = [Orcamento.from_dict(orcamento) for orcamento in data["orcamentos"]]
            vendas = [Venda.from_dict(venda) for venda in data["vendas"]]
    except FileNotFoundError:
        # Se o arquivo não existir, cria um template básico
        data = {
            "clientes": [],
            "orcamentos": [],
            "vendas": []
        }
        with open(filename, "w") as file:
            json.dump(data, file)
        clientes, orcamentos, vendas = [], [], []

    gerenciador = Gerenciador()
    gerenciador.clientes = clientes
    gerenciador.orcamentos = orcamentos
    gerenciador.vendas = vendas
    return gerenciador

def main_window():
    gerenciador = load_data()
    window = tk.Tk()
    window.title("Gerenciador de Orçamentos")
    
    # Configurando o notebook para abas
    tab_control = ttk.Notebook(window)
    
    # Criando as abas principais
    tab_clientes = ttk.Frame(tab_control)
    tab_orcamentos = ttk.Frame(tab_control)
    tab_vendas = ttk.Frame(tab_control)
    tab_relatorios = ttk.Frame(tab_control)
    
    tab_control.add(tab_clientes, text="Clientes")
    tab_control.add(tab_orcamentos, text="Orçamentos")
    tab_control.add(tab_vendas, text="Vendas")
    tab_control.add(tab_relatorios, text="Relatórios")
    
    tab_control.pack(expand=1, fill="both")
    
    # Chamar as funções para configurar cada aba
    setup_tab_clientes(tab_clientes)
    setup_tab_orcamentos(tab_orcamentos)
    setup_tab_vendas(tab_vendas)
    setup_tab_relatorios(tab_relatorios)
    
    window.mainloop()

# Funções de configuração para cada aba
def setup_tab_clientes(tab, gerenciador):
    # Campos para adicionar cliente
    frame_add_client = ttk.Frame(tab)
    frame_add_client.pack(side=tk.TOP, fill=tk.X)

    lbl_name = ttk.Label(frame_add_client, text="Nome:")
    lbl_name.grid(row=0, column=0)
    entry_name = ttk.Entry(frame_add_client)
    entry_name.grid(row=0, column=1)

    lbl_telefone = ttk.Label(frame_add_client, text="Telefone:")
    lbl_telefone.grid(row=1, column=0)
    entry_telefone = ttk.Entry(frame_add_client)
    entry_telefone.grid(row=1, column=1)

    lbl_email = ttk.Label(frame_add_client, text="Email:")
    lbl_email.grid(row=2, column=0)
    entry_email = ttk.Entry(frame_add_client)
    entry_email.grid(row=2, column=1)

    lbl_social = ttk.Label(frame_add_client, text="Social:")
    lbl_social.grid(row=3, column=0)
    entry_social = ttk.Entry(frame_add_client)
    entry_social.grid(row=3, column=1)

    # Botão para adicionar cliente
    button_add_client = ttk.Button(
        frame_add_client, 
        text="Adicionar Cliente", 
        command=lambda: add_client(
            entry_name.get(), entry_telefone.get(), entry_email.get(), entry_social.get(), gerenciador, tree_clients
        )
    )
    button_add_client.grid(row=4, columnspan=2)

    # Lista para visualizar clientes
    tree_clients = ttk.Treeview(tab, columns=("Nome", "Telefone", "Email", "Social"))
    tree_clients.column("#0", width=0, stretch=tk.NO)
    tree_clients.column("Nome", anchor=tk.W, width=150)
    tree_clients.column("Telefone", anchor=tk.W, width=100)
    tree_clients.column("Email", anchor=tk.W, width=150)
    tree_clients.column("Social", anchor=tk.W, width=100)

    tree_clients.heading("#0", text="", anchor=tk.W)
    tree_clients.heading("Nome", text="Nome", anchor=tk.W)
    tree_clients.heading("Telefone", text="Telefone", anchor=tk.W)
    tree_clients.heading("Email", text="Email", anchor=tk.W)
    tree_clients.heading("Social", text="Social", anchor=tk.W)

    tree_clients.pack()

    # Carregar clientes existentes
    for cliente in gerenciador.clientes:
        tree_clients.insert("", tk.END, values=(cliente.nome, cliente.telefone, cliente.email, cliente.social))

def add_client(name, telefone, email, social, gerenciador, tree_clients):
    if not name or not telefone or not email: # Validação básica
        return "Todos os campos são obrigatórios!"
    # Criando uma instância da classe Cliente com os dados fornecidos
    novo_cliente = Cliente(nome, telefone, email, social)

    # Adicionando o novo cliente à lista de clientes no gerenciador
    gerenciador.adicionar_cliente(novo_cliente)

    # Opcionalmente, você pode salvar os dados atualizados em um arquivo
    save_data(gerenciador)
    
    # Retornar uma mensagem de sucesso
    return "Cliente adicionado com sucesso!"

def setup_tab_orcamentos(tab):
    # Criar frames para organizar a aba
    frame_create_orcamento = ttk.Frame(tab)
    frame_create_orcamento.pack(side=tk.TOP, fill=tk.X)
    
    frame_view_orcamento = ttk.Frame(tab)
    frame_view_orcamento.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
    # Campo para selecionar o cliente
    lbl_cliente = ttk.Label(frame_create_orcamento, text="Cliente:")
    lbl_cliente.grid(row=0, column=0)
    entry_cliente = ttk.Combobox(frame_create_orcamento)
    entry_cliente['values'] = [cliente.nome for cliente in gerenciador.clientes]  # Preenchendo com os nomes dos clientes
    entry_cliente.grid(row=0, column=1)

    # Campo para a descrição do projeto
    lbl_descricao = ttk.Label(frame_create_orcamento, text="Descrição do Projeto:")
    lbl_descricao.grid(row=1, column=0)
    entry_descricao = ttk.Entry(frame_create_orcamento)
    entry_descricao.grid(row=1, column=1)

    # Campo para o volume
    lbl_volume = ttk.Label(frame_create_orcamento, text="Volume (L):")
    lbl_volume.grid(row=2, column=0)
    entry_volume = ttk.Entry(frame_create_orcamento)
    entry_volume.grid(row=2, column=1)

    # Campo para o tempo de impressão
    lbl_print_time = ttk.Label(frame_create_orcamento, text="Tempo de Impressão (h):")
    lbl_print_time.grid(row=3, column=0)
    entry_print_time = ttk.Entry(frame_create_orcamento)
    entry_print_time.grid(row=3, column=1)

    # Seção para cálculo de custo da resina
    frame_resin_cost = ttk.LabelFrame(frame_create_orcamento, text="Custo da Resina")
    frame_resin_cost.grid(row=1, columnspan=2, sticky="ew")

    entry_volume = add_field(frame_resin_cost, "Volume (ml):", 0)
    entry_print_time = add_field(frame_resin_cost, "Tempo de Impressão (h):", 1)
    entry_resin_price = add_field(frame_resin_cost, "Preço da Resina por Litro:", 2)
    entry_kwh_price = add_field(frame_resin_cost, "Preço do kWh:", 3)
    entry_machine_consumption = add_field(frame_resin_cost, "Consumo da Máquina (W):", 4)
    entry_failure_rate = add_field(frame_resin_cost, "Taxa de Falha (%):", 5)
    entry_profit_margin = add_field(frame_resin_cost, "Margem de Lucro (%):", 6)
    entry_administrative_costs = add_field(frame_resin_cost, "Custos Administrativos:", 7)
    entry_machine_hourly_rate = add_field(frame_resin_cost, "Taxa Horária da Máquina:", 8)

    # Seção para cálculo de custo de pintura e acabamento
    frame_painting_finishing = ttk.LabelFrame(frame_create_orcamento, text="Custo de Pintura e Acabamento")
    frame_painting_finishing.grid(row=2, columnspan=2, sticky="ew")

    entry_salary_goal = add_field(frame_painting_finishing, "Meta Salarial:", 0)
    entry_days_per_week = add_field(frame_painting_finishing, "Dias por Semana:", 1)
    entry_hours_per_day = add_field(frame_painting_finishing, "Horas por Dia:", 2)
    entry_finishing_hours = add_field(frame_painting_finishing, "Horas de Acabamento:", 3)
    entry_painting_hours = add_field(frame_painting_finishing, "Horas de Pintura:", 4)
    entry_finishing_materials_cost = add_field(frame_painting_finishing, "Custo de Materiais para Acabamento:", 5)
    entry_painting_materials_cost = add_field(frame_painting_finishing, "Custo de Materiais para Pintura:", 6)

    # Botão para criar o orçamento
    button_create_orcamento = ttk.Button(
        frame_create_orcamento,
        text="Criar Orçamento",
        command=lambda: create_orcamento(
            entry_cliente.get(), entry_descricao.get(), entry_volume.get(), entry_print_time.get(),
            entry_resin_price.get(), entry_kwh_price.get(), entry_machine_consumption.get(),
            entry_failure_rate.get(), entry_profit_margin.get(), entry_administrative_costs.get(),
            entry_machine_hourly_rate.get(), entry_salary_goal.get(), entry_days_per_week.get(),
            entry_hours_per_day.get(), entry_finishing_hours.get(), entry_painting_hours.get(),
            entry_finishing_materials_cost.get(), entry_painting_materials_cost.get()
        )
    )

    button_create_orcamento.grid(row=3, columnspan=2)

    def add_field(frame, label_text, row):
        lbl = ttk.Label(frame, text=label_text)
        lbl.grid(row=row, column=0)
        entry = ttk.Entry(frame)
        entry.grid(row=row, column=1)
        return entry

    # Lista para visualizar orçamentos
    tree_orcamentos = ttk.Treeview(frame_view_orcamento, columns=("ID", "Cliente", "Descrição", "Valor", "Status"))
    tree_orcamentos.column("#0", width=0, stretch=tk.NO)
    tree_orcamentos.column("ID", anchor=tk.W, width=50)
    tree_orcamentos.column("Cliente", anchor=tk.W, width=150)
    tree_orcamentos.column("Descrição", anchor=tk.W, width=300)
    tree_orcamentos.column("Valor", anchor=tk.W, width=100)
    tree_orcamentos.column("Status", anchor=tk.W, width=100)

    tree_orcamentos.heading("#0", text="", anchor=tk.W)
    tree_orcamentos.heading("ID", text="ID", anchor=tk.W)
    tree_orcamentos.heading("Cliente", text="Cliente", anchor=tk.W)
    tree_orcamentos.heading("Descrição", text="Descrição", anchor=tk.W)
    tree_orcamentos.heading("Valor", text="Valor", anchor=tk.W)
    tree_orcamentos.heading("Status", text="Status", anchor=tk.W)

    tree_orcamentos.pack()

    # Botões para editar, excluir e aprovar
    frame_buttons = ttk.Frame(frame_view_orcamento)
    frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)

    button_edit = ttk.Button(frame_buttons, text="Editar", command=lambda: edit_orcamento(tree_orcamentos))
    button_edit.pack(side=tk.LEFT)

    button_delete = ttk.Button(frame_buttons, text="Excluir", command=lambda: delete_orcamento(tree_orcamentos))
    button_delete.pack(side=tk.LEFT)

    button_approve = ttk.Button(frame_buttons, text="Aprovar", command=lambda: approve_orcamento(tree_orcamentos))
    button_approve.pack(side=tk.LEFT)

def create_orcamento(
    cliente, descricao, volume, print_time_hours,
    resin_price_per_liter, kwh_price, machine_consumption, failure_rate,
    profit_margin, administrative_costs, machine_hourly_rate,
    salary_goal, days_per_week, hours_per_day, finishing_hours, painting_hours,
    finishing_materials_cost, painting_materials_cost, gerenciador, tree_orcamentos
):
    # Convertendo valores de entrada para tipos numéricos
    volume = float(volume)
    print_time_hours = float(print_time_hours)
    resin_price_per_liter = float(resin_price_per_liter)
    kwh_price = float(kwh_price)
    machine_consumption = float(machine_consumption)
    failure_rate = float(failure_rate)
    profit_margin = float(profit_margin)
    administrative_costs = float(administrative_costs)
    machine_hourly_rate = float(machine_hourly_rate)
    salary_goal = float(salary_goal)
    days_per_week = int(days_per_week)
    hours_per_day = int(hours_per_day)
    finishing_hours = float(finishing_hours)
    painting_hours = float(painting_hours)
    finishing_materials_cost = float(finishing_materials_cost)
    painting_materials_cost = float(painting_materials_cost)

    # Cálculo do custo da resina
    resin_calculator = ResinCostCalculator(
        volume, print_time_hours, resin_price_per_liter,
        kwh_price, machine_consumption, failure_rate,
        profit_margin, administrative_costs, machine_hourly_rate
    )
    resin_cost = resin_calculator.calculate_sale_price()

    # Cálculo do custo de pintura e acabamento
    painting_calculator = PaintingAndFinishingCalculator(
        salary_goal, days_per_week, hours_per_day,
        finishing_hours, painting_hours, finishing_materials_cost,
        painting_materials_cost
    )
    painting_and_finishing_cost = painting_calculator.total_cost()

    # Criando uma instância do orçamento
    selected_cliente = next(c for c in gerenciador.clientes if c.nome == cliente)
    orcamento = Orcamento(selected_cliente, descricao, resin_cost, painting_and_finishing_cost)

    # Adicionando o orçamento ao gerenciador
    gerenciador.criar_orcamento(orcamento)

    # Adicionando o orçamento à árvore de visualização
    tree_orcamentos.insert("", tk.END, values=(orcamento.id, cliente, descricao, f"{resin_cost + painting_and_finishing_cost:.2f}", "Pendente"))

    # Opcionalmente, você pode salvar os dados atualizados em um arquivo
    save_data(gerenciador)
    
    return "Orçamento criado com sucesso!"

def edit_orcamento(tree_orcamentos, gerenciador):
    selected_item = tree_orcamentos.selection()[0]
    orcamento_id = tree_orcamentos.item(selected_item, 'values')[0]

    # Encontrar o orçamento correspondente no gerenciador
    orcamento_to_edit = next(o for o in gerenciador.orcamentos if o.id == int(orcamento_id))

    # Criar uma nova janela para edição
    edit_window = tk.Toplevel()
    edit_window.title("Editar Orçamento")

    # Campos para editar os detalhes do orçamento
    # Você pode adicionar campos semelhantes aos da função de criação de orçamento
    lbl_cliente = ttk.Label(edit_window, text="Cliente:")
    lbl_cliente.grid(row=0, column=0)
    entry_cliente = ttk.Combobox(edit_window, values=[c.nome for c in gerenciador.clientes])
    entry_cliente.grid(row=0, column=1)
    entry_cliente.set(orcamento_to_edit.cliente.nome)

    lbl_descricao = ttk.Label(edit_window, text="Descrição do Projeto:")
    lbl_descricao.grid(row=1, column=0)
    entry_descricao = ttk.Entry(edit_window)
    entry_descricao.grid(row=1, column=1)
    entry_descricao.insert(0, orcamento_to_edit.descricao_projeto)

    lbl_volume = ttk.Label(edit_window, text="Volume (litros):")
    lbl_volume.grid(row=2, column=0)
    entry_volume = ttk.Entry(edit_window)
    entry_volume.grid(row=2, column=1)
    entry_volume.insert(0, orcamento_to_edit.volume)

    lbl_print_time = ttk.Label(edit_window, text="Tempo de Impressão (horas):")
    lbl_print_time.grid(row=3, column=0)
    entry_print_time = ttk.Entry(edit_window)
    entry_print_time.grid(row=3, column=1)
    entry_print_time.insert(0, orcamento_to_edit.print_time_hours)

    def save_edits():
        # Coletar os valores editados
        edited_cliente = entry_cliente.get()
        edited_descricao = entry_descricao.get()
        edited_volume = float(entry_volume.get())
        edited_print_time = float(entry_print_time.get())

        # Atualizar o orçamento selecionado com os novos valores
        orcamento_to_edit.cliente = next(c for c in gerenciador.clientes if c.nome == edited_cliente)
        orcamento_to_edit.descricao_projeto = edited_descricao
        orcamento_to_edit.volume = edited_volume
        orcamento_to_edit.print_time_hours = edited_print_time

        # Você pode continuar atualizando outros campos aqui...

        # Atualizar a visualização na árvore de orçamentos
        tree_orcamentos.item(selected_item, values=(orcamento_to_edit.id, edited_cliente, edited_descricao, orcamento_to_edit.valor_venda, orcamento_to_edit.status))

        # Salvar os dados atualizados, se necessário
        save_data(gerenciador)

        # Fechar a janela de edição
        edit_window.destroy()


def delete_orcamento(tree_orcamentos, gerenciador):
    selected_item = tree_orcamentos.selection()[0]  # Obter o item selecionado
    selected_orcamento_id = tree_orcamentos.item(selected_item, "values")[0]  # Obter o ID do orçamento selecionado
    
    # Encontrar o objeto do orçamento correspondente na lista de orçamentos
    orcamento_to_delete = next(o for o in gerenciador.orcamentos if o.id == int(selected_orcamento_id))
    
    # Remover o objeto do orçamento da lista de orçamentos
    gerenciador.orcamentos.remove(orcamento_to_delete)
    
    # Remover o item selecionado da árvore de orçamentos
    tree_orcamentos.delete(selected_item)

    # Opcionalmente, você pode salvar os dados atualizados em um arquivo
    save_data(gerenciador)

    # Você pode retornar uma mensagem de sucesso ou realizar outras ações conforme necessário
    return "Orçamento excluído com sucesso!"

def approve_orcamento(tree_orcamentos, gerenciador):
    selected_item = tree_orcamentos.selection()[0]  # Obter o item selecionado
    selected_orcamento_id = tree_orcamentos.item(selected_item, "values")[0]  # Obter o ID do orçamento selecionado
    
    # Encontrar o objeto do orçamento correspondente na lista de orçamentos
    orcamento_to_approve = next(o for o in gerenciador.orcamentos if o.id == int(selected_orcamento_id))
    
    # Alterar o status do objeto do orçamento para "Aprovado"
    orcamento_to_approve.status = "Aprovado"
    
    # Atualizar a árvore de orçamentos para refletir a mudança de status
    tree_orcamentos.item(selected_item, values=(orcamento_to_approve.id, orcamento_to_approve.cliente.nome, orcamento_to_approve.descricao_projeto, orcamento_to_approve.valor_venda, "Aprovado"))

    # Opcionalmente, você pode salvar os dados atualizados em um arquivo
    save_data(gerenciador)

    # Você pode retornar uma mensagem de sucesso ou realizar outras ações conforme necessário
    return "Orçamento aprovado com sucesso!"

def setup_tab_vendas(tab):
    # Criar frames para organizar a aba
    frame_create_venda = ttk.Frame(tab)
    frame_create_venda.pack(side=tk.TOP, fill=tk.X)
    
    frame_view_venda = ttk.Frame(tab)
    frame_view_venda.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
    # Campos para registrar uma venda
    lbl_orcamento = ttk.Label(frame_create_venda, text="Orçamento:")
    lbl_orcamento.grid(row=0, column=0)
    entry_orcamento = ttk.Combobox(frame_create_venda)  # Utilize uma Combobox para selecionar o orçamento
    entry_orcamento.grid(row=0, column=1)

    lbl_data_venda = ttk.Label(frame_create_venda, text="Data da Venda:")
    lbl_data_venda.grid(row=1, column=0)
    entry_data_venda = ttk.Entry(frame_create_venda)
    entry_data_venda.grid(row=1, column=1)

    # Adicione campos semelhantes para data de despacho e código de rastreio
    # ...

    button_create_venda = ttk.Button(frame_create_venda, text="Registrar Venda", command=lambda: create_venda(entry_orcamento.get(), entry_data_venda.get(), ...))
    button_create_venda.grid(row=2, columnspan=2)

    # Lista para visualizar vendas
    tree_vendas = ttk.Treeview(frame_view_venda, columns=("ID", "Orçamento", "Data Venda", "Data Despacho", "Rastreio"))
    tree_vendas.column("#0", width=0, stretch=tk.NO)
    tree_vendas.column("ID", anchor=tk.W, width=50)
    tree_vendas.column("Orçamento", anchor=tk.W, width=150)
    tree_vendas.column("Data Venda", anchor=tk.W, width=100)
    tree_vendas.column("Data Despacho", anchor=tk.W, width=100)
    tree_vendas.column("Rastreio", anchor=tk.W, width=100)

    tree_vendas.heading("#0", text="", anchor=tk.W)
    tree_vendas.heading("ID", text="ID", anchor=tk.W)
    tree_vendas.heading("Orçamento", text="Orçamento", anchor=tk.W)
    tree_vendas.heading("Data Venda", text="Data Venda", anchor=tk.W)
    tree_vendas.heading("Data Despacho", text="Data Despacho", anchor=tk.W)
    tree_vendas.heading("Rastreio", text="Rastreio", anchor=tk.W)

    tree_vendas.pack()

def create_venda(orcamento_id, data_venda, data_despacho, codigo_rastreio, gerenciador, tree_vendas):
    # Encontrar o objeto do orçamento correspondente na lista de orçamentos
    orcamento_selecionado = next(o for o in gerenciador.orcamentos if o.id == int(orcamento_id))

    # Verificar se o orçamento está aprovado antes de criar a venda
    if orcamento_selecionado.status != "Aprovado":
        return "Orçamento não aprovado! A venda não pode ser criada."

    # Criar uma instância da classe Venda com os dados fornecidos
    nova_venda = Venda(orcamento_selecionado, data_venda, data_despacho, codigo_rastreio)

    # Adicionar a nova venda à lista de vendas no gerenciador
    gerenciador.registrar_venda(nova_venda)

    # Opcionalmente, você pode salvar os dados atualizados em um arquivo
    save_data(gerenciador)

    # Adicionar a nova venda à árvore de vendas para visualização
    tree_vendas.insert("", tk.END, values=(nova_venda.orcamento.id, nova_venda.data_venda.strftime("%Y-%m-%d"), nova_venda.data_despacho.strftime("%Y-%m-%d") if nova_venda.data_despacho else None, nova_venda.codigo_rastreio))

    # Retornar uma mensagem de sucesso
    return "Venda criada com sucesso!"

def setup_tab_relatorios(tab, gerenciador):
    # Criar frames para organizar a aba
    frame_balanco_mensal = ttk.Frame(tab)
    frame_balanco_mensal.pack(side=tk.TOP, fill=tk.X)
    
    frame_roi = ttk.Frame(tab)
    frame_roi.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # Campos para balanço mensal
    lbl_mes = ttk.Label(frame_balanco_mensal, text="Mês:")
    lbl_mes.grid(row=0, column=0)
    entry_mes = ttk.Spinbox(frame_balanco_mensal, from_=1, to=12)
    entry_mes.grid(row=0, column=1)

    lbl_ano = ttk.Label(frame_balanco_mensal, text="Ano:")
    lbl_ano.grid(row=1, column=0)
    entry_ano = ttk.Entry(frame_balanco_mensal)
    entry_ano.grid(row=1, column=1)

    button_calcular_balanco = ttk.Button(frame_balanco_mensal, text="Calcular Balanço", command=lambda: calcular_balanco(entry_mes.get(), entry_ano.get(), gerenciador))
    button_calcular_balanco.grid(row=2, columnspan=2)

    # Seção para mostrar informações sobre retorno do investimento
    lbl_roi = ttk.Label(frame_roi, text="Retorno do Investimento:")
    lbl_roi.pack(side=tk.TOP)

    lbl_roi_info = ttk.Label(frame_roi, text="Informações sobre ROI aqui") # Você pode atualizar este texto com as informações calculadas
    lbl_roi_info.pack(side=tk.TOP)

def calcular_balanco(mes, ano, gerenciador):
    # Inicializar a soma total das vendas
    total_vendas = 0

    # Loop através das vendas no gerenciador
    for venda in gerenciador.vendas:
        # Verificar se a venda corresponde ao mês e ano especificados
        if venda.data_venda.month == int(mes) and venda.data_venda.year == int(ano):
            # Adicionar o valor da venda ao total
            total_vendas += venda.orcamento.valor_venda

    # Retornar o total das vendas para o mês e ano especificados
    return total_vendas

def calcular_roi(gerenciador):
    # Somando o lucro dos orçamentos aprovados que resultaram em vendas
    total_lucro = sum(venda.orcamento.lucro for venda in gerenciador.vendas if venda.orcamento.status == "Aprovado")
    
    # Somando o custo total dos orçamentos aprovados
    total_custo = 3100

    # Calculando o ROI
    roi = total_lucro - total_custo if total_custo != 0 else 0

    # Retornando o ROI em formato de moeda Real brasileiro
    return f"R$ {roi:,.2f}"

if __name__ == "__main__":
    main_window()
