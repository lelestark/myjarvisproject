import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

class ResinCostCalculator:
    def __init__(
        self,
        volume,
        print_time_hours,
        resin_price_per_liter,
        failure_rate,
        profit_margin,
        administrative_costs,
        machine_hourly_rate,
    ):
        self.volume = volume / 1000
        self.print_time = print_time_hours
        self.resin_price_per_liter = resin_price_per_liter
        self.failure_rate = failure_rate
        self.profit_margin = profit_margin
        self.administrative_costs = administrative_costs
        self.machine_hourly_rate = machine_hourly_rate

    def energy_cost(self):
        # Definir as variáveis
        potencia = 140 # potência da impressora 3D em watts
        tempo = 43 # tempo de impressão em horas
        tarifa = 0.99 # tarifa de energia em reais por kWh

        # Calcular a energia consumida em kWh
        energia = potencia * tempo / 1000

        # Calcular o valor da impressão em reais
        valor = energia * tarifa

        # Mostrar o resultado na tela
        print(f"O valor da impressão é R$ {valor:.2f}")
        return valor

    def calculate_material_cost(self):
        custo_material = self.resin_price_per_liter * self.volume
        print(f"Custo de material: {custo_material}")
        return custo_material

    def calculate_failure_cost(self):
        cuto_falha = (
            (self.calculate_material_cost() 
            * (self.failure_rate
            / 100)) + self.energy_cost()
        )
        print(f"Custo de falha: {cuto_falha}")
        return cuto_falha

    def total_production_cost(self):
        material_cost = self.calculate_material_cost()
        failure_cost = self.calculate_failure_cost()
        energy_cost = self.energy_cost()
        machine_cost = self.machine_hourly_rate * self.print_time
        total_producao = (
            material_cost
            + failure_cost
            + energy_cost
            + machine_cost
            + self.administrative_costs
        )
        print (f"Custo de hora maquina: {machine_cost}")
        print(f"Custo total de produção: {total_producao}")
        return total_producao

    def calculate_sale_price(self):
        debug = self.total_production_cost() * (1 + self.profit_margin / 100)
        print(f"Preço de venda: {debug}")
        return self.total_production_cost() * (1 + self.profit_margin / 100)


class PaintingAndFinishingCalculator:
    def __init__(
        self,
        salary_goal,
        days_per_week,
        hours_per_day,
        finishing_hours,
        painting_hours,
        finishing_materials_cost,
        painting_materials_cost,
    ):
        self.hourly_rate = salary_goal / (
            days_per_week * hours_per_day * 4
        )  # Calculate hourly rate based on desired salary
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
            "social": self.social,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["nome"], data["telefone"], data["email"], data["social"])


class Orcamento:
    next_id = 1

    def __init__(
        self,
        cliente,
        descricao_projeto,
        resin_cost,
        painting_and_finishing_cost,
        status="Pendente",
    ):
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
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        cliente = Cliente.from_dict(data["cliente"])
        return cls(
            cliente,
            data["descricao_projeto"],
            data["resin_cost"],
            data["painting_and_finishing_cost"],
            data["status"],
        )

    def calcular_valor_total(self):
        return self.resin_cost + self.painting_and_finishing_cost


class Venda:
    def __init__(self, orcamento, data_venda, data_despacho=None, codigo_rastreio=None):
        self.orcamento = orcamento
        self.data_venda = (
            datetime.strptime(data_venda, "%d-%m-%Y")
            if isinstance(data_venda, str)
            else data_venda
        )
        self.data_despacho = (
            datetime.strptime(data_despacho, "%d-%m-%Y")
            if isinstance(data_despacho, str)
            else data_despacho
        )
        self.codigo_rastreio = codigo_rastreio

    def to_dict(self):
        return {
            "orcamento": self.orcamento.to_dict(),
            "data_venda": self.data_venda.strftime("%Y-%m-%d"),
            "data_despacho": self.data_despacho.strftime("%Y-%m-%d")
            if self.data_despacho
            else None,
            "codigo_rastreio": self.codigo_rastreio,
        }

    @classmethod
    def from_dict(cls, data):
        orcamento = Orcamento.from_dict(data["orcamento"])
        return cls(
            orcamento,
            data["data_venda"],
            data["data_despacho"],
            data["codigo_rastreio"],
        )


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


def calcular_balanco(mes, ano, gerenciador):
    total_vendas = sum(
        venda.orcamento.valor_venda
        for venda in gerenciador.vendas
        if venda.data_venda.month == int(mes) and venda.data_venda.year == int(ano)
    )
    return total_vendas


def save_data(gerenciador):
    # Salvando clientes
    with open('clientes.json', 'w', encoding='utf-8') as file:
        json.dump([cliente.to_dict() for cliente in gerenciador.clientes], file, indent=4)

    # Salvando orçamentos
    with open('orcamentos.json', 'w', encoding='utf-8') as file:
        json.dump([orcamento.to_dict() for orcamento in gerenciador.orcamentos], file, indent=4)

    # Salvando vendas
    with open('vendas.json', 'w', encoding='utf-8') as file:
        json.dump([venda.to_dict() for venda in gerenciador.vendas], file, indent=4)


def load_data_from_file(filename):
    with open(filename, "r", encoding='utf-8') as file:
        return json.load(file)

def load_data():
    try:
        with open("clientes.json", "r", encoding='utf-8') as file:
            clientes_data = json.load(file)
        with open("orcamentos.json", "r", encoding='utf-8') as file:
            orcamentos_data = json.load(file)
        with open("vendas.json", "r", encoding='utf-8') as file:
            vendas_data = json.load(file)

        clientes = [Cliente.from_dict(cliente) for cliente in clientes_data]
        orcamentos = [Orcamento.from_dict(orcamento) for orcamento in orcamentos_data]
        vendas = [Venda.from_dict(venda) for venda in vendas_data]

    except FileNotFoundError:
        # Se os arquivos não existirem, crie listas vazias
        clientes, orcamentos, vendas = [], [], []

    gerenciador = Gerenciador()
    gerenciador.clientes = clientes
    gerenciador.orcamentos = orcamentos
    gerenciador.vendas = vendas
    return gerenciador

def load_last_budget():
    try:
        with open('ultimo_orcamento.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return None  # Return None if the file does not exist

def main_window():
    gerenciador = load_data()
    window = tk.Tk()
    window.title("Gerenciador de Orçamentos")

    # Configuring the notebook for tabs
    tab_control = ttk.Notebook(window)

    # Creating the main tabs
    tab_clientes = ttk.Frame(tab_control)
    tab_orcamentos = ttk.Frame(tab_control)
    tab_vendas = ttk.Frame(tab_control)
    tab_relatorios = ttk.Frame(tab_control)

    tab_control.add(tab_clientes, text="Clientes")
    tab_control.add(tab_orcamentos, text="Orçamentos")
    tab_control.add(tab_vendas, text="Vendas")
    tab_control.add(tab_relatorios, text="Relatórios")

    tab_control.pack(expand=1, fill="both")

    # Call the functions to configure each tab
    setup_tab_clientes(tab_clientes, gerenciador)
    setup_tab_orcamentos(tab_orcamentos, gerenciador)
    setup_tab_vendas(tab_vendas, gerenciador)
    setup_tab_relatorios(tab_relatorios, gerenciador)

    window.mainloop()


# Configuration functions for each tab
def setup_tab_clientes(tab, gerenciador):
    # Fields to add a client
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

    # Button to add a client
    button_add_client = ttk.Button(
        frame_add_client,
        text="Adicionar Cliente",
        command=lambda: add_client(
            entry_name.get(),
            entry_telefone.get(),
            entry_email.get(),
            entry_social.get(),
            gerenciador,
            tree_clients,
        ),
    )
    button_add_client.grid(row=4, columnspan=2)

    # List to view clients
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

    # Load existing clients
    for cliente in gerenciador.clientes:
        tree_clients.insert(
            "",
            tk.END,
            values=(cliente.nome, cliente.telefone, cliente.email, cliente.social),
        )


def add_client(name, telefone, email, social, gerenciador, tree_clients):
    if not name or not telefone or not email:  # Basic validation
        return "Todos os campos são obrigatórios!"
    # Create an instance of the Cliente class with the provided data
    novo_cliente = Cliente(name, telefone, email, social)

    # Add the new client to the list of clients in the gerenciador
    gerenciador.adicionar_cliente(novo_cliente)

    # Optionally, you can save the updated data to a file
    save_data(gerenciador)

    # Return a success message
    return "Cliente adicionado com sucesso!"


def setup_tab_orcamentos(tab, gerenciador):
    ultimo_orcamento = load_last_budget()
    def add_field(parent, label_text, row, default_value=None):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky="e")

        entry = tk.Entry(parent)
        entry.grid(row=row, column=1, sticky="ew")

        if default_value is not None:
            entry.insert(0, default_value)

        return entry

    # Create frames to organize the tab
    frame_create_orcamento = ttk.Frame(tab)
    frame_create_orcamento.pack(side=tk.TOP, fill=tk.X)

    frame_view_orcamento = ttk.Frame(tab)
    frame_view_orcamento.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # Field to select the client
    lbl_cliente = ttk.Label(frame_create_orcamento, text="Cliente:")
    lbl_cliente.grid(row=0, column=0)
    entry_cliente = ttk.Combobox(frame_create_orcamento)
    entry_cliente["values"] = [
        cliente.nome for cliente in gerenciador.clientes
    ]  # Fill with client names
    entry_cliente.grid(row=0, column=1)

    # Section for resin cost calculation
    frame_resin_cost = ttk.LabelFrame(frame_create_orcamento, text="Custo da Resina")
    frame_resin_cost.grid(row=1, columnspan=2, sticky="ew")

    if ultimo_orcamento:
        entry_descricao = add_field(frame_resin_cost, "Descrição do Projeto:", 2, ultimo_orcamento['descricao_projeto'])
        entry_volume = add_field(frame_resin_cost, "Volume (ml):", 3, ultimo_orcamento['volume'])
        entry_print_time = add_field(frame_resin_cost, "Tempo de Impressão (h):", 4, ultimo_orcamento['print_time_hours'])
        entry_resin_price = add_field(frame_resin_cost, "Preço da Resina por Litro:", 5, ultimo_orcamento['resin_price_per_liter'])
        entry_failure_rate = add_field(frame_resin_cost, "Taxa de Falha (%):", 6, ultimo_orcamento['failure_rate'])
        entry_profit_margin = add_field(frame_resin_cost, "Margem de Lucro (%):", 7, ultimo_orcamento['profit_margin'])
        entry_administrative_costs = add_field(frame_resin_cost, "Custos Administrativos:", 8, ultimo_orcamento['administrative_costs'])
        entry_machine_hourly_rate = add_field(frame_resin_cost, "Taxa Horária Máquina:", 9, ultimo_orcamento['machine_hourly_rate'])
    else:
        entry_descricao = add_field(frame_resin_cost, "Descrição do Projeto:", 2)
        entry_volume = add_field(frame_resin_cost, "Volume (ml):", 3)
        entry_print_time = add_field(frame_resin_cost, "Tempo de Impressão (h):", 4)
        entry_resin_price = add_field(frame_resin_cost, "Preço da Resina por Litro:", 5)
        entry_failure_rate = add_field(frame_resin_cost, "Taxa de Falha (%):", 6)
        entry_profit_margin = add_field(frame_resin_cost, "Margem de Lucro (%):", 7)
        entry_administrative_costs = add_field(frame_resin_cost, "Custos Administrativos:", 8)
        entry_machine_hourly_rate = add_field(frame_resin_cost, "Taxa Horária da Máquina:", 9)

    # Section for painting and finishing cost calculation
    frame_painting_finishing = ttk.LabelFrame(
        frame_create_orcamento, text="Custo de Pintura e Acabamento"
    )
    frame_painting_finishing.grid(row=2, columnspan=2, sticky="ew")

    if ultimo_orcamento:
        entry_salary_goal = add_field(frame_painting_finishing, "Meta Salarial:", 0, ultimo_orcamento['salary_goal'])
        entry_days_per_week = add_field(frame_painting_finishing, "Dias por Semana:", 1, ultimo_orcamento['days_per_week'])
        entry_hours_per_day = add_field(frame_painting_finishing, "Horas por Dia:", 2, ultimo_orcamento['hours_per_day'])
        entry_finishing_hours = add_field(frame_painting_finishing, "Horas de Acabamento:", 3, ultimo_orcamento['finishing_hours'])
        entry_painting_hours = add_field(frame_painting_finishing, "Horas de Pintura:", 4, ultimo_orcamento['painting_hours'])
        entry_finishing_materials_cost = add_field(frame_painting_finishing, "Custo de Materiais para Acabamento:", 5, ultimo_orcamento['finishing_materials_cost'])
        entry_painting_materials_cost = add_field(frame_painting_finishing, "Custo de Materiais para Pintura:", 6, ultimo_orcamento['painting_materials_cost'])
    else:
        entry_salary_goal = add_field(frame_painting_finishing, "Meta Salarial:", 0)
        entry_days_per_week = add_field(frame_painting_finishing, "Dias por Semana:", 1)
        entry_hours_per_day = add_field(frame_painting_finishing, "Horas por Dia:", 2)
        entry_finishing_hours = add_field(frame_painting_finishing, "Horas de Acabamento:", 3)
        entry_painting_hours = add_field(frame_painting_finishing, "Horas de Pintura:", 4)
        entry_finishing_materials_cost = add_field(frame_painting_finishing, "Custo de Materiais para Acabamento:", 5)
        entry_painting_materials_cost = add_field(frame_painting_finishing, "Custo de Materiais para Pintura:", 6)

    # Button to create the orcamento
    button_create_orcamento = ttk.Button(
        frame_create_orcamento,
        text="Criar Orçamento",
        command=lambda: create_orcamento(
            entry_cliente.get(),
            entry_descricao.get(),
            entry_volume.get(),
            entry_print_time.get(),
            entry_resin_price.get(),
            entry_failure_rate.get(),
            entry_profit_margin.get(),
            entry_administrative_costs.get(),
            entry_machine_hourly_rate.get(),
            entry_salary_goal.get(),
            entry_days_per_week.get(),
            entry_hours_per_day.get(),
            entry_finishing_hours.get(),
            entry_painting_hours.get(),
            entry_finishing_materials_cost.get(),
            entry_painting_materials_cost.get(),
            gerenciador,
            tree_orcamentos,
        ),
    )

    button_create_orcamento.grid(row=4, columnspan=2)

    # List to view orcamentos
    tree_orcamentos = ttk.Treeview(
        frame_view_orcamento, columns=("ID", "Cliente", "Descrição", "Valor", "Status")
    )
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

    for orcamento in gerenciador.orcamentos:
        valor_formatado = locale.currency(orcamento.valor_venda, grouping=True)
        tree_orcamentos.insert(
            "",
            tk.END,
            values=(
                orcamento.id,
                orcamento.cliente.nome,
                orcamento.descricao_projeto,
                valor_formatado,
                orcamento.status,
            ),
        )

        tree_orcamentos.pack()

    # Buttons to edit, delete, and approve
    frame_buttons = ttk.Frame(frame_view_orcamento)
    frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)

    button_edit = ttk.Button(
        frame_buttons,
        text="Editar",
        command=lambda: edit_orcamento(tree_orcamentos, gerenciador),
    )
    button_edit.pack(side=tk.LEFT)

    button_delete = ttk.Button(
        frame_buttons,
        text="Excluir",
        command=lambda: delete_orcamento(tree_orcamentos, gerenciador),
    )
    button_delete.pack(side=tk.LEFT)

    button_approve = ttk.Button(
        frame_buttons,
        text="Aprovar",
        command=lambda: approve_orcamento(tree_orcamentos, gerenciador),
    )
    button_approve.pack(side=tk.LEFT)


def create_orcamento(
    cliente,
    descricao,
    volume,
    print_time_hours,
    resin_price_per_liter,
    failure_rate,
    profit_margin,
    administrative_costs,
    machine_hourly_rate,
    salary_goal,
    days_per_week,
    hours_per_day,
    finishing_hours,
    painting_hours,
    finishing_materials_cost,
    painting_materials_cost,
    gerenciador,
    tree_orcamentos,
):
    # Convert input values to numeric types
    volume = int(volume)
    print_time_hours = int(print_time_hours)
    resin_price_per_liter = int(resin_price_per_liter)
    failure_rate = int(failure_rate)
    profit_margin = int(profit_margin)
    administrative_costs = int(administrative_costs)
    machine_hourly_rate = int(machine_hourly_rate)
    salary_goal = int(salary_goal)
    days_per_week = int(days_per_week)
    hours_per_day = int(hours_per_day)
    finishing_hours = int(finishing_hours)
    painting_hours = int(painting_hours)
    finishing_materials_cost = int(finishing_materials_cost)
    painting_materials_cost = int(painting_materials_cost)

    # Calculate resin cost
    resin_calculator = ResinCostCalculator(
        volume,
        print_time_hours,
        resin_price_per_liter,
        failure_rate,
        profit_margin,
        administrative_costs,
        machine_hourly_rate,
    )
    resin_cost = resin_calculator.calculate_sale_price()

    # Calculate painting and finishing cost
    painting_calculator = PaintingAndFinishingCalculator(
        salary_goal,
        days_per_week,
        hours_per_day,
        finishing_hours,
        painting_hours,
        finishing_materials_cost,
        painting_materials_cost,
    )
    painting_and_finishing_cost = painting_calculator.total_cost()

    # Create an instance of Orcamento
    selected_cliente = next(c for c in gerenciador.clientes if c.nome == cliente)
    orcamento = Orcamento(
        selected_cliente, descricao, resin_cost, painting_and_finishing_cost
    )

    # Add the orcamento to the gerenciador
    gerenciador.criar_orcamento(orcamento)

    # Add the orcamento to the tree view
    tree_orcamentos.insert(
        "",
        tk.END,
        values=(
            orcamento.id,
            cliente,
            descricao,
            f"{resin_cost + painting_and_finishing_cost:.2f}",
            "Pendente",
        ),
    )

    # Optionally, you can save the updated data to a file
    save_data(gerenciador)

    # Creating a dictionary with the budget data
    ultimo_orcamento = {
        'cliente': cliente,
        'descricao_projeto': descricao,
        'volume': volume,
        'print_time_hours': print_time_hours,
        'resin_price_per_liter': resin_price_per_liter,
        'failure_rate': failure_rate,
        'profit_margin': profit_margin,
        'administrative_costs': administrative_costs,
        'machine_hourly_rate': machine_hourly_rate,
        'salary_goal': salary_goal,
        'days_per_week': days_per_week,
        'hours_per_day': hours_per_day,
        'finishing_hours': finishing_hours,
        'painting_hours': painting_hours,
        'finishing_materials_cost': finishing_materials_cost,
        'painting_materials_cost': painting_materials_cost,
    }

    # Saving the dictionary to a JSON file
    with open('ultimo_orcamento.json', 'w', encoding='utf-8') as file:
        json.dump(ultimo_orcamento, file)
    print ("Orçamento criado com sucesso!")

def edit_orcamento(tree_orcamentos, gerenciador):
    selected_item = tree_orcamentos.selection()[0]
    orcamento_id = tree_orcamentos.item(selected_item, "values")[0]

    # Find the corresponding orcamento object in the list of orcamentos
    orcamento_to_edit = next(
        o for o in gerenciador.orcamentos if o.id == int(orcamento_id)
    )

    # Create a new window for editing
    edit_window = tk.Toplevel()
    edit_window.title("Editar Orçamento")

    # Fields to edit the orcamento details
    # You can add similar fields as in the create_orcamento function
    lbl_cliente = ttk.Label(edit_window, text="Cliente:")
    lbl_cliente.grid(row=0, column=0)
    entry_cliente = ttk.Combobox(
    edit_window, values=[c.nome for c in gerenciador.clientes]
    )
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
        # Collect the edited values
        edited_cliente = entry_cliente.get()
        edited_descricao = entry_descricao.get()
        edited_volume = float(entry_volume.get())
        edited_print_time = float(entry_print_time.get())

        # Update the selected orcamento with the new values
        orcamento_to_edit.cliente = next(
            c for c in gerenciador.clientes if c.nome == edited_cliente
        )
        orcamento_to_edit.descricao_projeto = edited_descricao
        orcamento_to_edit.volume = edited_volume
        orcamento_to_edit.print_time_hours = edited_print_time

        # You can continue updating other fields here...

        # Update the view in the tree of orcamentos
        tree_orcamentos.item(
            selected_item,
            values=(
                orcamento_to_edit.id,
                edited_cliente,
                edited_descricao,
                orcamento_to_edit.valor_venda,
                orcamento_to_edit.status,
            ),
        )

        # Save the updated data, if necessary
        save_data(gerenciador)

        # Close the edit window
        edit_window.destroy()


def delete_orcamento(tree_orcamentos, gerenciador):
    selected_item = tree_orcamentos.selection()[0]  # Get the selected item
    selected_orcamento_id = tree_orcamentos.item(selected_item, "values")[
        0
    ]  # Get the ID of the selected orcamento

    # Find the corresponding orcamento object in the list of orcamentos
    orcamento_to_delete = next(
        o for o in gerenciador.orcamentos if o.id == int(selected_orcamento_id)
    )

    # Remove the orcamento object from the list of orcamentos
    gerenciador.orcamentos.remove(orcamento_to_delete)

    # Remove the selected item from the tree of orcamentos
    tree_orcamentos.delete(selected_item)

    # Optionally, you can save the updated data to a file
    save_data(gerenciador)

    # You can return a success message or perform other actions as needed
    return "Orçamento excluído com sucesso!"


def approve_orcamento(tree_orcamentos, gerenciador):
    selected_item = tree_orcamentos.selection()[0]  # Get the selected item
    selected_orcamento_id = tree_orcamentos.item(selected_item, "values")[
        0
    ]  # Get the ID of the selected orcamento

    # Find the corresponding orcamento object in the list of orcamentos
    orcamento_to_approve = next(
        o for o in gerenciador.orcamentos if o.id == int(selected_orcamento_id)
    )

    # Change the status of the orcamento object to "Aprovado"
    orcamento_to_approve.status = "Aprovado"

    # Update the orcamentos tree to reflect the status change
    tree_orcamentos.item(
        selected_item,
        values=(
            orcamento_to_approve.id,
            orcamento_to_approve.cliente.nome,
            orcamento_to_approve.descricao_projeto,
            orcamento_to_approve.valor_venda,
            "Aprovado",
        ),
    )

    # Optionally, you can save the updated data to a file
    save_data(gerenciador)

    # You can return a success message or perform other actions as needed
    return "Orçamento aprovado com sucesso!"


def setup_tab_vendas(tab, gerenciador):
    # Create frames to organize the tab
    frame_create_venda = ttk.Frame(tab)
    frame_create_venda.pack(side=tk.TOP, fill=tk.X)

    frame_view_venda = ttk.Frame(tab)
    frame_view_venda.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # Fields to register a venda
    lbl_orcamento = ttk.Label(frame_create_venda, text="Orçamento:")
    lbl_orcamento.grid(row=0, column=0)
    entry_orcamento = ttk.Combobox(
        frame_create_venda
    )  # Use a Combobox to select the orcamento
    entry_orcamento.grid(row=0, column=1)

    lbl_data_venda = ttk.Label(frame_create_venda, text="Data da Venda:")
    lbl_data_venda.grid(row=1, column=0)
    entry_data_venda = ttk.Entry(frame_create_venda)
    entry_data_venda.grid(row=1, column=1)

    lbl_data_despacho = ttk.Label(frame_create_venda, text="Data de Despacho:")
    lbl_data_despacho.grid(row=2, column=0)
    entry_data_despacho = ttk.Entry(frame_create_venda)
    entry_data_despacho.grid(row=2, column=1)

    lbl_codigo_rastreio = ttk.Label(frame_create_venda, text="Código de Rastreio:")
    lbl_codigo_rastreio.grid(row=3, column=0)
    entry_codigo_rastreio = ttk.Entry(frame_create_venda)
    entry_codigo_rastreio.grid(row=3, column=1)

    button_create_venda = ttk.Button(
        frame_create_venda,
        text="Registrar Venda",
        command=lambda: create_venda(
            entry_orcamento.get(),
            entry_data_venda.get(),
            entry_data_despacho.get(),
            entry_codigo_rastreio.get(),
            gerenciador,
            tree_vendas,
        ),
    )
    button_create_venda.grid(row=4, columnspan=2)

    # List to view vendas
    tree_vendas = ttk.Treeview(
        frame_view_venda,
        columns=("ID", "Orçamento", "Data Venda", "Data Despacho", "Rastreio"),
    )
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


def create_venda(
    orcamento_id, data_venda, data_despacho, codigo_rastreio, gerenciador, tree_vendas
):
    # Find the corresponding orcamento object in the list of orcamentos
    selected_orcamento = next(
        o for o in gerenciador.orcamentos if o.id == int(orcamento_id)
    )

    # Check if the orcamento is approved before creating the venda
    if selected_orcamento.status != "Aprovado":
        return "Orçamento não aprovado! A venda não pode ser criada."

    # Create an instance of the Venda class with the provided data
    nova_venda = Venda(selected_orcamento, data_venda, data_despacho, codigo_rastreio)

    # Add the new venda to the list of vendas in the gerenciador
    gerenciador.registrar_venda(nova_venda)

    # Optionally, you can save the updated data to a file
    save_data(gerenciador)

    # Add the new venda to the tree view for visualization
    tree_vendas.insert(
        "",
        tk.END,
        values=(
            nova_venda.orcamento.id,
            nova_venda.data_venda.strftime("%Y-%m-%d"),
            nova_venda.data_despacho.strftime("%Y-%m-%d")
            if nova_venda.data_despacho
            else None,
            nova_venda.codigo_rastreio,
        ),
    )

    # Return a success message
    return "Venda criada com sucesso!"

def setup_tab_relatorios(tab, gerenciador):
    # Create frames to organize the tab
    frame_balanco_mensal = ttk.Frame(tab)
    frame_balanco_mensal.pack(side=tk.TOP, fill=tk.X)

    frame_roi = ttk.Frame(tab)
    frame_roi.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # Fields for monthly balance
    lbl_mes = ttk.Label(frame_balanco_mensal, text="Mês:")
    lbl_mes.grid(row=0, column=0)
    entry_mes = ttk.Spinbox(frame_balanco_mensal, from_=1, to=12)
    entry_mes.grid(row=0, column=1)

    lbl_ano = ttk.Label(frame_balanco_mensal, text="Ano:")
    lbl_ano.grid(row=1, column=0)
    entry_ano = ttk.Entry(frame_balanco_mensal)
    entry_ano.grid(row=1, column=1)

    button_calcular_balanco = ttk.Button(
        frame_balanco_mensal,
        text="Calcular Balanço",
        command=lambda: calcular_balanco(entry_mes.get(), entry_ano.get(), gerenciador),
    )
    button_calcular_balanco.grid(row=2, columnspan=2)

    # Section to show return on investment information
    lbl_roi = ttk.Label(frame_roi, text="Retorno do Investimento:")
    lbl_roi.pack(side=tk.TOP)

    lbl_roi_info = ttk.Label(
        frame_roi, text="Informações sobre ROI aqui"
    )  # You can update this text with the calculated information
    lbl_roi_info.pack(side=tk.TOP)


if __name__ == "__main__":
    main_window()
