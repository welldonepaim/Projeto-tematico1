from datetime import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import LEFT, RIGHT, Y
from src.dao import manutencao_dao  # Ajuste para o caminho correto

class AbaPainel:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Painel")

        # Dados fictícios
        self.total_setores = 12
        self.usuarios_ativos = 8
        self.usuarios_inativos = 3
        self.setores_sem_responsavel = 2

        self.ordens_abertas = 7
        self.ordens_encerradas = 15

        # Monta a interface
        self._montar_cards()
        self._montar_graficos()
        self._montar_os_mes()
        self._montar_alertas()

    # ----------------- Cards de resumo -----------------
    def _montar_cards(self):
        frame_cards = tb.Frame(self.frame)
        frame_cards.pack(fill="x", pady=10)

        cards = [
            ("Total de Setores", self.total_setores, "#5dade2"),
            ("Usuários Ativos", self.usuarios_ativos, "#58d68d"),
            ("Usuários Inativos", self.usuarios_inativos, "#ec7063"),
            ("Setores sem Responsável", self.setores_sem_responsavel, "#f4d03f")
        ]

        for title, value, color in cards:
            card = tb.Frame(frame_cards, bootstyle="light", padding=10, relief="raised")
            card.pack(side="left", expand=True, fill="both", padx=5)
            tb.Label(card, text=title, font=("Arial", 10), foreground=color).pack(pady=(0,5))
            tb.Label(card, text=str(value), font=("Arial", 20, "bold")).pack()

    # ----------------- Gráficos -----------------
    def _montar_graficos(self):
        frame_graficos = tb.Frame(self.frame)
        frame_graficos.pack(fill="both", expand=True, pady=10)

        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        # Gráfico 1: Usuários ativos vs inativos (pizza)
        fig1, ax1 = plt.subplots(figsize=(3,3))
        ax1.pie(
            [self.usuarios_ativos, self.usuarios_inativos],
            labels=["Ativos", "Inativos"],
            autopct="%1.1f%%",
            colors=["#58d68d", "#ec7063"]
        )
        ax1.set_title("Usuários")
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_graficos)
        canvas1.get_tk_widget().pack(side=LEFT, expand=True)

        # Gráfico 2: Ordens abertas vs encerradas (barra)
        fig2, ax2 = plt.subplots(figsize=(3,3))
        ax2.bar(["Abertas", "Encerradas"], [self.ordens_abertas, self.ordens_encerradas], color=["#f39c12", "#5dade2"])
        ax2.set_title("Ordens de Serviço")
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_graficos)
        canvas2.get_tk_widget().pack(side=LEFT, expand=True)

    # ----------------- OS do mês -----------------
    def _montar_os_mes(self):
        frame_os = tb.Frame(self.frame)
        frame_os.pack(fill="both", expand=False, pady=10)

        tb.Label(frame_os, text="Ordens de Serviço deste mês", font=("Arial", 12, "bold")).pack(anchor="w")

        # Scrollbar vertical
        scrollbar = tb.Scrollbar(frame_os)
        scrollbar.pack(side=RIGHT, fill=Y)

        colunas = ("ID", "Tipo", "Equipamento", "Responsável", "Data Prevista", "Status")
        self.tree_os = tb.Treeview(frame_os, columns=colunas, show="headings", yscrollcommand=scrollbar.set, height=5)
        for col in colunas:
            self.tree_os.heading(col, text=col)
            self.tree_os.column(col, width=120, anchor="center")
        self.tree_os.pack(fill="both", expand=True)

        scrollbar.config(command=self.tree_os.yview)

        self.tree_os.tag_configure('par', background='#f2f2f2')
        self.tree_os.tag_configure('impar', background='white')

        self.carregar_os_mes()

    def carregar_os_mes(self):
        for item in self.tree_os.get_children():
            self.tree_os.delete(item)

        hoje = datetime.today()
        manutencoes = manutencao_dao.listar_manutencoes()
        # Filtra OS do mês atual
        os_mes = [m for m in manutencoes if m.data_prevista and m.data_prevista.month == hoje.month and m.data_prevista.year == hoje.year]

        for i, m in enumerate(os_mes):
            tag = 'par' if i % 2 == 0 else 'impar'
            eq = m.equipamento.nome if m.equipamento else "N/A"
            resp = m.responsavel.nome if m.responsavel else "N/A"
            data = m.data_prevista.strftime("%d/%m/%Y") if m.data_prevista else ""
            self.tree_os.insert("", "end", values=(m.id, m.tipo, eq, resp, data, m.status), tags=(tag,))

    # ----------------- Alertas -----------------
    def _montar_alertas(self):
        frame_alertas = tb.Frame(self.frame)
        frame_alertas.pack(fill="x", pady=10)

        mensagens = [
            f"⚠️ Existem {self.setores_sem_responsavel} setores sem responsável!",
            f"ℹ️ Total de ordens abertas: {self.ordens_abertas}"
        ]

        for msg in mensagens:
            tb.Label(frame_alertas, text=msg, font=("Arial", 11), bootstyle=INFO).pack(anchor="w", pady=2)

