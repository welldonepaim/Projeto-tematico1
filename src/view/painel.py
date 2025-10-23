from datetime import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, Y, INFO
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.dao import manutencao_dao

class AbaPainel:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Painel")

        # Inicializa valores
        self.total_setores = 12
        self.usuarios_ativos = 8
        self.usuarios_inativos = 3
        self.setores_sem_responsavel = 2

        self.ordens_abertas = 0
        self.ordens_encerradas = 0

        # Monta interface inicial
        self._montar_graficos()
        self._montar_os_mes()

        # Atualiza automaticamente a cada 10 segundos em teste para verificação de mudanças
        self._atualizar_periodicamente()

    def _atualizar_periodicamente(self):
        try:
            manutencoes = manutencao_dao.listar_manutencoes()

            self.ordens_abertas = sum(1 for m in manutencoes if m.status in ('pendente', 'em analise', 'em manutencao'))
            self.ordens_encerradas = sum(1 for m in manutencoes if m.status in ('concluida', 'revisada'))

            for widget in self.frame.winfo_children():
                widget.destroy()

            self._montar_graficos()
            self._montar_os_mes()

        except Exception as e:
            print("Erro ao atualizar painel:", e)

        self.frame.after(10000, self._atualizar_periodicamente)

    def _montar_graficos(self):
        frame_graficos = tb.Frame(self.frame)
        frame_graficos.pack(fill="both", expand=True, pady=10)

        # Gráfico 1: Usuários Dados ficticios
        fig1, ax1 = plt.subplots(figsize=(3,3))
        ax1.pie([self.usuarios_ativos, self.usuarios_inativos],
                labels=["Ativos", "Inativos"],
                autopct="%1.1f%%",
                colors=["#58d68d", "#ec7063"])
        ax1.set_title("Usuários")
        FigureCanvasTkAgg(fig1, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True)

        # Gráfico 2: Ordens
        fig2, ax2 = plt.subplots(figsize=(3,3))
        ax2.bar(["Abertas", "Encerradas"], [self.ordens_abertas, self.ordens_encerradas],
                color=["#f39c12", "#5dade2"])
        ax2.set_title("Ordens de Serviço")
        FigureCanvasTkAgg(fig2, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True)

        # Gráfico 3: Prioridade
        manutencoes = manutencao_dao.listar_manutencoes()
        prioridades = [m.prioridade if m.prioridade else "Sem Prioridade" for m in manutencoes]
        contagem = Counter(prioridades)
        fig3, ax3 = plt.subplots(figsize=(4,3))
        ax3.bar(contagem.keys(), contagem.values(), color=["#c0392b", "#e67e22", "#f1c40f", "#27ae60", "#95a5a6"])
        ax3.set_title("Ordens por Prioridade")
        ax3.set_ylabel("Quantidade")
        FigureCanvasTkAgg(fig3, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True)

    def _montar_os_mes(self):
        frame_os = tb.Frame(self.frame)
        frame_os.pack(fill="both", expand=False, pady=10)

        tb.Label(frame_os, text="Ordens de Serviço deste mês", font=("Arial", 12, "bold")).pack(anchor="w")

        scrollbar = tb.Scrollbar(frame_os)
        scrollbar.pack(side=RIGHT, fill=Y)

        colunas = ("ID", "Tipo", "Equipamento", "Responsável", "Data Prevista", "Prioridade", "Status")
        self.tree_os = tb.Treeview(frame_os, columns=colunas, show="headings", yscrollcommand=scrollbar.set, height=7)

        for col in colunas:
            self.tree_os.heading(col, text=col)
            self.tree_os.column(col, width=130, anchor="center")
        self.tree_os.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree_os.yview)

        self.tree_os.tag_configure('par', background='#f2f2f2', foreground='black')
        self.tree_os.tag_configure('impar', background='white', foreground='black')
        self.tree_os.tag_configure('atrasada', background='#f8d7da', foreground='#c0392b', font=('Arial', 10, 'bold'))

        self.carregar_os_mes()

    def carregar_os_mes(self):
        for item in self.tree_os.get_children():
            self.tree_os.delete(item)

        hoje = datetime.today().date()
        manutencoes = manutencao_dao.listar_manutencoes()

        os_mes = [m for m in manutencoes if m.data_prevista and m.data_prevista.month == hoje.month and m.data_prevista.year == hoje.year and m.tipo.lower()=="preventiva"]

        for i, m in enumerate(os_mes):
            eq = m.equipamento.nome if m.equipamento else "N/A"
            resp = m.responsavel.nome if m.responsavel else "N/A"
            data = m.data_prevista.strftime("%d/%m/%Y") if m.data_prevista else ""
            prioridade = m.prioridade if m.prioridade else "Sem Prioridade"

            if m.data_prevista < hoje and m.status not in ('concluida', 'revisada'):
                tag = 'atrasada'
            else:
                tag = 'par' if i % 2 == 0 else 'impar'

            self.tree_os.insert("", "end", values=(m.id, m.tipo, eq, resp, data, prioridade, m.status), tags=(tag,))

    
