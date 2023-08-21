import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.utf8")


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
        camadas,
        tempo_exposicao,
    ):
        self.volume = (
            volume / 1000
        )  # input volume in ml converted to liters to calculate resin cost
        self.print_time = print_time_hours
        self.resin_price_per_liter = resin_price_per_liter
        self.failure_rate = failure_rate
        self.profit_margin = profit_margin
        self.administrative_costs = administrative_costs
        self.machine_hourly_rate = machine_hourly_rate
        self.camadas = camadas
        self.tempo_exposicao = tempo_exposicao
        self.depreciacao_lcd = self.calcular_depreciacao_lcd_simplificado()

    # function to calculate the energy cost of my 3D printer given x hours of work
    def energy_cost(self):
        potencia = 140  # 3D printer power in watts
        tempo = self.print_time  # print time in hours
        tarifa = 0.99  # kwh price in my city

        # Energy consumption of my machine giving x hours of work
        energia = potencia * tempo / 1000

        # calculate the cost of energy in Brazilian Real
        custo_energia = energia * tarifa

        # debug
        # print(f"O valor da impressão é R$ {valor:.2f}")
        return custo_energia

    # function to calculate the cost of the resin used in the print
    def calculate_print_resin_cost(self):
        custo_resina = (
            self.resin_price_per_liter * self.volume
        )  # price of resin bottle(1 liter) * volume of resin used
        # print(f"Custo de material: {custo_material}")
        return custo_resina

    # function to give me an margin of error in the print cost
    def calculate_failure_cost(self):
        custo_falha = (
            self.calculate_print_resin_cost() * (self.failure_rate / 100)
        ) + self.energy_cost()  # formula: (cost of resin used on the print * failure rate in %) + energy cost
        # print(f"Custo de falha: {cuto_falha}")
        return custo_falha

    # function to calculate the depreciation of the LCD screen
    def calcular_depreciacao_lcd_simplificado(self):
        # Parâmetros fixos
        valor_lcd = 1070  # lcd price in brazilian real
        vida_util_lcd_horas = 2000  # lcd lifetime in hours
        # Calculando o tempo para camadas regulares
        tempo_total_segundos = (
            self.camadas * self.tempo_exposicao
        )  # calculates the time the lcd stays on during the print is total layers * exposure time
        # converting to hours
        tempo_total_horas = tempo_total_segundos / 3600
        # calculating the percentage of depreciation
        depreciacao_percentual = tempo_total_horas / vida_util_lcd_horas
        valor_depreciacao = (
            valor_lcd * depreciacao_percentual
        )  # lcd price * depreciation percentage
        depreciacao_convertido = locale.currency(valor_depreciacao, grouping=True)
        print(f"Depreciação LCD: {depreciacao_convertido}")
        return valor_depreciacao

    # function to calculate the total cost of the print
    def total_print_cost(self):
        material_cost = self.calculate_print_resin_cost()
        failure_cost = self.calculate_failure_cost()
        energy_cost = self.energy_cost()
        machine_cost = self.machine_hourly_rate * self.print_time
        total_print_cost = (
            material_cost
            + failure_cost
            + energy_cost
            + machine_cost
            + self.administrative_costs
            + self.depreciacao_lcd
        )
        # print (f"Custo de hora maquina: {machine_cost}")
        # print(f"Custo total de produção: {total_producao}")
        # print(f"depreciação LCD: {self.depreciacao_lcd}")
        return total_print_cost

    # function to calculate the sale price of the print
    def calculate_sale_price(self):
        return self.total_print_cost() * (
            self.profit_margin / 100
        )  # formula: total print cost * profit margin in %


# class to calculate the cost of painting and finishing
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

    def total_working_hours(self):  # Calculate total working hours
        return self.finishing_hours + self.painting_hours

    def total_materials_cost(self):  # Calculate total materials cost
        return self.finishing_materials_cost + self.painting_materials_cost

    def total_service_cost(self):  # Calculate total service cost
        return self.total_working_hours() * self.hourly_rate

    def total_paint_and_finish_price(
        self,
    ):  # Calculate total price of painting and finishing
        return self.total_service_cost() + self.total_materials_cost()


client_id_counter = 0


def generate_client_id():  # function to generate a unique id for each client
    global client_id_counter
    client_id_counter += 1
    return client_id_counter


# class to create a client
class Cliente:
    def __init__(
        self,
        nome,
        telefone,
        email,
        social,
        rua,
        numero,
        bairro,
        cep,
        cidade,
        estado,
        cpf,
        client_id=None,
    ):
        self.client_id = client_id if client_id else generate_client_id()
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.social = social
        self.rua = rua
        self.numero = numero
        self.bairro = bairro
        self.cep = cep
        self.cidade = cidade
        self.estado = estado
        self.cpf = cpf

    @classmethod
    def from_dict(cls, data):
        # print ("dados cliente:", data)
        return cls(
            data["nome"],
            data["telefone"],
            data["email"],
            data["social"],
            data["rua"],
            data["numero"],
            data["bairro"],
            data["cep"],
            data["cidade"],
            data["estado"],
            data["cpf"],
            data["client_id"],
        )

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "nome": self.nome,
            "telefone": self.telefone,
            "email": self.email,
            "social": self.social,
            "rua": self.rua,
            "numero": self.numero,
            "bairro": self.bairro,
            "cep": self.cep,
            "cidade": self.cidade,
            "estado": self.estado,
            "cpf": self.cpf,
        }


# class to create a budget (this is the most complex part of the application)
class Orcamento:
    next_id = 1

    def __init__(
        self,
        selected_cliente,
        descricao,
        volume,
        print_time_hours,
        resin_price_per_liter,
        failure_rate,
        profit_margin,
        administrative_costs,
        machine_hourly_rate,
        camadas,
        tempo_exposicao,
        salary_goal,
        days_per_week,
        hours_per_day,
        finishing_hours,
        painting_hours,
        finishing_materials_cost,
        painting_materials_cost,
        print_price,
        painting_and_finishing_price,
        resin_cost_calculator,
        painting_and_finishing_calculator,
        lucro_liquido,
        status="Pendente",
        id=None,
    ):
        if id is not None:
            self.id = id
        else:
            self.id = Orcamento.next_id
        Orcamento.next_id += 1
        self.cliente = selected_cliente
        self.descricao_projeto = descricao
        self.volume = volume
        self.print_time_hours = print_time_hours
        self.resin_price_per_liter = resin_price_per_liter
        self.failure_rate = failure_rate
        self.profit_margin = profit_margin
        self.administrative_costs = administrative_costs
        self.machine_hourly_rate = machine_hourly_rate
        self.camadas = camadas
        self.tempo_exposicao = tempo_exposicao
        self.salary_goal = salary_goal
        self.days_per_week = days_per_week
        self.hours_per_day = hours_per_day
        self.finishing_hours = finishing_hours
        self.painting_hours = painting_hours
        self.finishing_materials_cost = finishing_materials_cost
        self.painting_materials_cost = painting_materials_cost
        self.print_price = print_price
        self.painting_and_finishing_price = painting_and_finishing_price
        self.valor_venda = self.calcular_valor_total()  # sale price
        self.lucro_liquido = lucro_liquido  # net profit
        self.status = status  # pending, approved, rejected

    def to_dict(self):
        return {
            "id": self.id,
            "cliente": self.cliente.to_dict(),
            "descricao_projeto": self.descricao_projeto,
            "volume": self.volume,
            "print_time_hours": self.print_time_hours,
            "resin_price_per_liter": self.resin_price_per_liter,
            "failure_rate": self.failure_rate,
            "profit_margin": self.profit_margin,
            "administrative_costs": self.administrative_costs,
            "machine_hourly_rate": self.machine_hourly_rate,
            "camadas": self.camadas,
            "tempo_exposicao": self.tempo_exposicao,
            "salary_goal": self.salary_goal,
            "days_per_week": self.days_per_week,
            "hours_per_day": self.hours_per_day,
            "finishing_hours": self.finishing_hours,
            "painting_hours": self.painting_hours,
            "finishing_materials_cost": self.finishing_materials_cost,
            "painting_materials_cost": self.painting_materials_cost,
            "print_price": self.print_price,
            "painting_and_finishing_price": self.painting_and_finishing_price,
            "valor_venda": self.valor_venda,
            "lucro_liquido": self.lucro_liquido,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        cliente = Cliente.from_dict(data["cliente"])
        return cls(
            cliente,
            data["descricao_projeto"],
            data["volume"],
            data["print_time_hours"],
            data["resin_price_per_liter"],
            data["failure_rate"],
            data["profit_margin"],
            data["administrative_costs"],
            data["machine_hourly_rate"],
            data["camadas"],
            data["tempo_exposicao"],
            data["salary_goal"],
            data["days_per_week"],
            data["hours_per_day"],
            data["finishing_hours"],
            data["painting_hours"],
            data["finishing_materials_cost"],
            data["painting_materials_cost"],
            data["print_price"],
            data["painting_and_finishing_price"],
            data["valor_venda"],
            data["lucro_liquido"],
            data["status"],
            id=data["id"],
        )

    @classmethod
    # function to set the next unique id to be used
    def set_next_id(cls, orcamentos):
        max_id = max((orcamento.id for orcamento in orcamentos), default=0)
        cls.next_id = max_id + 1

    # function to calculate sale price of de piece (print + painting and finishing)
    def calcular_valor_total(
        self,
    ):
        valor_venda = self.print_price + self.painting_and_finishing_price
        return valor_venda


# class to create a sale, this is going to be used to create a sale history and generate reports
# reports i need: sales by month, sales by client, monthly revenue, monthly profit, monthly expenses, monthly net profit
# this class needs to be improved
class Venda:
    def __init__(self, orcamento, data_venda, data_despacho=None, codigo_rastreio=None):
        self.orcamento = orcamento
        # sale date
        self.data_venda = (
            datetime.strptime(data_venda, "%d-%m-%Y")
            if isinstance(data_venda, str)
            else data_venda
        )
        # shipping date
        self.data_despacho = (
            datetime.strptime(data_despacho, "%d-%m-%Y")
            if isinstance(data_despacho, str)
            else data_despacho
        )
        # tracking code
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


# from here on is the part that needs most improvements


# class to manage the application
# i can use tips to improve this class
# i can use tips to menage the reports
class Gerenciador:
    def __init__(self):
        self.clientes = []
        self.orcamentos = []
        self.vendas = []
        self.reports = []

    # function to add a client to the list
    def adicionar_cliente(self, cliente):
        self.clientes.append(cliente)

    # function to remove a client from the list
    def remover_cliente(self, cliente):
        self.clientes.remove(cliente)

    # function to create a budget
    def criar_orcamento(self, orcamento):
        self.orcamentos.append(orcamento)

    # function to register a sale
    def registrar_venda(self, venda):
        self.vendas.append(venda)

    # function to edit a client
    def editar_cliente(
        self, client_id, nome, telefone, email, social
    ):  # Additional parameters can be added as needed
        # print("Editing client with ID:", client_id)  # Print the client ID
        for cliente in self.clientes:
            if str(cliente.client_id) == str(
                client_id
            ):  # Supondo que o ID esteja armazenado no atributo 'id'
                cliente.nome = nome
                cliente.telefone = telefone
                cliente.email = email
                cliente.social = social
                break

        save_data(self)  # Save the updated data to file


# function to refresh the treeview with the clients list
def refresh_client_list(gerenciador, tree_clients):
    tree_clients.delete(*tree_clients.get_children())
    for c in gerenciador.clientes:
        tree_clients.insert(
            "",
            tk.END,
            values=(c.client_id, c.nome, c.telefone, c.email, c.social),
        )


# function to refresh the treeview with the budget list
def refresh_ocamento_list(gerenciador, tree_orcamentos):
    tree_orcamentos.delete(*tree_orcamentos.get_children())
    for o in gerenciador.orcamentos:
        venda = o.print_price + o.painting_and_finishing_price
        valor_formatado = locale.currency(venda, grouping=True)
        tree_orcamentos.insert(
            "",
            tk.END,
            values=(
                o.id,
                o.cliente.nome,
                o.descricao_projeto,
                valor_formatado,
                o.status,
            ),
        )


# function to delete a client selected in the treeview
def remove_client(tree_clients, gerenciador):
    # Get the selected item in the tree
    selected_items = tree_clients.selection()
    if not selected_items:
        print("Nenhum cliente selecionado")
        return

    item = selected_items[0]
    values = tree_clients.item(item, "values")
    cliente_id = int(values[0])
    print("Selected values:", values)
    # Create a new Cliente object with the selected values
    cliente_to_remove = next(
        (c for c in gerenciador.clientes if c.client_id == cliente_id), None
    )

    if cliente_to_remove:
        confirmation_message = (
            f"Tem certeza que deseja remover o cliente {cliente_to_remove.nome}?"
        )
        if messagebox.askyesno("Remover Cliente", confirmation_message):
            gerenciador.clientes.remove(cliente_to_remove)
            save_data(gerenciador)
            refresh_client_list(gerenciador, tree_clients)
            print(cliente_to_remove.nome, "removido com sucesso!")


# function to add a client
def add_client(
    nome,
    telefone,
    email,
    social,
    rua,
    numero,
    bairro,
    cep,
    cidade,
    estado,
    cpf,
    gerenciador,
    tree_clients,
):
    if not nome or not telefone:  # Basic validation
        return "Todos os campos são obrigatórios!"

    # Create a new Cliente object with the provided data, ID will be generated automatically
    novo_cliente = Cliente(
        nome,
        telefone,
        email,
        social,
        rua,
        numero,
        bairro,
        cep,
        cidade,
        estado,
        cpf,
    )

    # Add the new client to the list of clients in the gerenciador
    gerenciador.adicionar_cliente(novo_cliente)

    # Optionally, you can save the updated data to a file
    save_data(gerenciador)
    refresh_client_list(gerenciador, tree_clients)

    # Return a success message
    return "Cliente adicionado com sucesso!"


# function to edit a client selected in the treeview
def edit_client(tab, tree_clients, gerenciador):
    selected_item = tree_clients.selection()[0]  # Get the selected client
    client_data = tree_clients.item(selected_item, "values")
    client_id = client_data[0]  # Get the selected client's ID

    # print("Selected client ID:", client_id)  # Print for debugging
    # function to save the edits, uses the previous data as a placeholder
    def save_edits():
        nonlocal client_id, gerenciador, tree_clients  # Capture these variables
        # Access client_id directly in this function
        client_id = entry_id.get()
        nome = entry_name.get()
        telefone = entry_phone.get()
        email = entry_email.get()
        social = entry_social.get()
        print(
            "Saving edits:", client_id, nome, telefone, email, social
        )  # Print for debugging
        # Call the "editar_cliente" method to update the client details
        gerenciador.editar_cliente(client_id, nome, telefone, email, social)
        # Save the updated data to file
        save_data(gerenciador)

        # Refresh the client list (if needed)
        refresh_client_list(gerenciador, tree_clients)

        # Close the edit window
        edit_window.destroy()

    # Create a new window for editing
    edit_window = tk.Toplevel(tab)
    edit_window.title("Editar Cliente")

    # Field to display client's ID (read-only)
    lbl_id = ttk.Label(edit_window, text="ID:")
    lbl_id.grid(row=0, column=0)
    entry_id = ttk.Entry(edit_window)  # ID is not editable
    entry_id.config(state=tk.NORMAL)
    entry_id.insert(0, client_id)  # Pre-fill with selected client's ID
    entry_id.config(state="readonly")
    entry_id.grid(row=0, column=1)

    # Field to edit client's name
    lbl_name = ttk.Label(edit_window, text="Nome:")
    lbl_name.grid(row=1, column=0)
    entry_name = ttk.Entry(edit_window)
    entry_name.insert(0, client_data[1])  # Pre-fill with selected client's name
    entry_name.grid(row=1, column=1)

    # Field to edit client's phone
    lbl_phone = ttk.Label(edit_window, text="Telefone:")
    lbl_phone.grid(row=2, column=0)
    entry_phone = ttk.Entry(edit_window)
    entry_phone.insert(0, client_data[2])  # Pre-fill with selected client's phone
    entry_phone.grid(row=2, column=1)

    # Field to edit client's email
    lbl_email = ttk.Label(edit_window, text="Email:")
    lbl_email.grid(row=3, column=0)
    entry_email = ttk.Entry(edit_window)
    entry_email.insert(0, client_data[3])  # Pre-fill with selected client's email
    entry_email.grid(row=3, column=1)

    # Field to edit client's social
    lbl_social = ttk.Label(edit_window, text="Social:")
    lbl_social.grid(row=4, column=0)
    entry_social = ttk.Entry(edit_window)
    entry_social.insert(0, client_data[4])  # Pre-fill with selected client's social
    entry_social.grid(row=4, column=1)

    # Button to save edits (will call a function named "save_edits" which we will define later)
    button_save_edits = ttk.Button(edit_window, text="Salvar", command=save_edits)
    button_save_edits.grid(row=5, column=1)


# function to generate a monthly sales report
def calcular_balanco(mes, ano, gerenciador):
    pass


# function to save the data to a file
def save_data(gerenciador):
    # Saves clients to a JSON file
    # print("Saving clients:", [cliente.to_dict() for cliente in gerenciador.clientes])  # Print for debugging
    with open("clientes.json", "w", encoding="utf-8") as file:
        json.dump(
            [cliente.to_dict() for cliente in gerenciador.clientes], file, indent=4
        )

    # Saves budgets to a JSON file
    with open("orcamentos.json", "w", encoding="utf-8") as file:
        json.dump(
            [orcamento.to_dict() for orcamento in gerenciador.orcamentos],
            file,
            indent=4,
        )

    # Saves sales to a JSON file
    with open("vendas.json", "w", encoding="utf-8") as file:
        json.dump([venda.to_dict() for venda in gerenciador.vendas], file, indent=4)


# function to load data from files
def load_data():
    global client_id_counter
    try:
        with open("clientes.json", "r", encoding="utf-8") as file:
            clientes_data = json.load(file)
            # print("Clientes data:", clientes_data) # Adicione esta linha
        with open("orcamentos.json", "r", encoding="utf-8") as file:
            orcamentos_data = json.load(file)
        with open("vendas.json", "r", encoding="utf-8") as file:
            vendas_data = json.load(file)

        clientes = [Cliente.from_dict(cliente) for cliente in clientes_data]
        last_client_id = max([cliente.client_id for cliente in clientes], default=0)
        client_id_counter = last_client_id + 1
        orcamentos = [Orcamento.from_dict(orcamento) for orcamento in orcamentos_data]
        Orcamento.set_next_id(orcamentos)  # Atualize o próximo ID
        vendas = [Venda.from_dict(venda) for venda in vendas_data]

    except FileNotFoundError:
        # Se os arquivos não existirem, crie listas vazias
        clientes, orcamentos, vendas = [], [], []

    gerenciador = Gerenciador()
    gerenciador.clientes = clientes
    gerenciador.orcamentos = orcamentos
    gerenciador.vendas = vendas
    return gerenciador


# loads the last budget	data to use as placeholder
def load_last_budget():
    try:
        with open("ultimo_orcamento.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None  # Return None if the file does not exist


# start of the GUI part
def main_window():
    gerenciador = load_data()
    window = tk.Tk()
    window.title("Gerenciador de Orçamentos")

    # window size
    window.geometry("800x800")

    window.update_idletasks()

    # get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width // 2) - (window.winfo_width() // 2)
    y = (screen_height // 2) - (window.winfo_height() // 2)

    # set the position of the window to the center of the screen
    window.geometry(f"+{x}+{y}")

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
