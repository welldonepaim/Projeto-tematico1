from datetime import datetime, timedelta
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, Y, INFO, PRIMARY, SUCCESS, DANGER, WARNING
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.dao import manutencao_dao, equipamento_dao, planejamento_dao


class AbaPainel:
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=12)
        notebook.add(self.frame, text="Painel")

        # header
        header = tb.Frame(self.frame)
        header.pack(fill="x", pady=(0, 8))
        tb.Label(header, text="Painel de Controle", font=("Segoe UI", 18, "bold")).pack(side=LEFT)
        tb.Button(header, text="Atualizar", bootstyle=INFO, command=self.refresh).pack(side=RIGHT)

        # KPI cards
        self.kpi_frame = tb.Frame(self.frame)
        self.kpi_frame.pack(fill="x", pady=6)

        # area de conteúdo (gráficos + tabela)
        self.content_frame = tb.Frame(self.frame)
        self.content_frame.pack(fill="both", expand=True)

        # Monta interface inicial
        self._montar_kpis()
        self._montar_graficos()
        self._montar_os_mes()

        # Atualiza periodicamente (opcional)
        self.frame.after(120000, self.refresh)

    def refresh(self):
        try:
            # atualiza apenas o conteúdo dinâmico
            for widget in list(self.kpi_frame.winfo_children()):
                widget.destroy()
            for widget in list(self.content_frame.winfo_children()):
                widget.destroy()

            self._montar_kpis()
            self._montar_graficos()
            self._montar_os_mes()
        except Exception as e:
            print("Erro ao atualizar painel:", e)

    def _kpi_card(self, parent, title, value, subtitle="", color=PRIMARY):
        card = tb.Frame(parent, padding=10, bootstyle="light")
        card.pack(side=LEFT, expand=True, fill="x", padx=6)
        tb.Label(card, text=title, font=("Segoe UI", 10), foreground="#6c757d").pack(anchor="w")
        tb.Label(card, text=str(value), font=("Segoe UI", 20, "bold"), foreground="#222222").pack(anchor="w")
        if subtitle:
            tb.Label(card, text=subtitle, font=("Segoe UI", 9), foreground="#6c757d").pack(anchor="w")
        return card

    def _montar_kpis(self):
        # coleta dados
        equipamentos = equipamento_dao.listar_equipamentos()
        manutencoes = manutencao_dao.listar_manutencoes()
        planejamentos = planejamento_dao.listar_planejamentos()

        total_equipamentos = len(equipamentos)
        equipamentos_disponiveis = len([e for e in equipamentos if getattr(e, 'status', '') == 'Disponível'])
        ordens_abertas = len([m for m in manutencoes if getattr(m, 'status', '').lower() in ('pendente', 'em análise', 'em manutencao', 'em manutção', 'em manutencao')])
        hoje = datetime.today().date()
        ordens_atrasadas = len([m for m in manutencoes if m.data_prevista and m.data_prevista < hoje and getattr(m, 'status', '').lower() not in ('concluida', 'revisada')])
        # show count of planejamentos (placeholder: all for now)
        proximos_planejamentos = len(planejamentos)

        # create cards
        self._kpi_card(self.kpi_frame, "Equipamentos", total_equipamentos, f"{equipamentos_disponiveis} disponíveis", color=PRIMARY)
        self._kpi_card(self.kpi_frame, "Ordens Abertas", ordens_abertas, "Em andamento", color=WARNING)
        self._kpi_card(self.kpi_frame, "Ordens Atrasadas", ordens_atrasadas, "Requer atenção", color=DANGER)
        self._kpi_card(self.kpi_frame, "Planejamentos", len(planejamentos), "Agendados", color=SUCCESS)

    def _montar_graficos(self):
        frame_graficos = tb.Frame(self.content_frame)
        frame_graficos.pack(fill="both", expand=True, pady=10)

        # Grafico 1: Distribuição equipamentos (pie)
        equipamentos = equipamento_dao.listar_equipamentos()
        total_equipamentos = len(equipamentos)
        equipamentos_disponiveis = len([e for e in equipamentos if getattr(e, 'status', '') == 'Disponível'])
        equipamentos_manut = total_equipamentos - equipamentos_disponiveis
        fig1, ax1 = plt.subplots(figsize=(3,4))
        ax1.pie([equipamentos_disponiveis, equipamentos_manut], labels=["Disponíveis", "Em manutenção"], autopct="%1.0f%%", colors=["#2ecc71", "#e74c3c"])
        ax1.set_title("Equipamentos")
        FigureCanvasTkAgg(fig1, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True)

        # Grafico 2: Ordens por status (bar)
        manutencoes = manutencao_dao.listar_manutencoes()
        status_counts = Counter([ (m.status or "").capitalize() for m in manutencoes ])
        fig2, ax2 = plt.subplots(figsize=(4,4))
        ax2.bar(status_counts.keys(), status_counts.values(), color=["#f39c12", "#3498db", "#2ecc71", "#95a5a6"]) 
        ax2.set_title("Ordens por Status")
        ax2.tick_params(axis='x', rotation=25)
        FigureCanvasTkAgg(fig2, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True)

        # Grafico 3: Prioridade
        prioridades = [m.prioridade if m.prioridade else "Sem Prioridade" for m in manutencoes]
        contagem = Counter(prioridades)
        fig3, ax3 = plt.subplots(figsize=(4,4))
        ax3.bar(contagem.keys(), contagem.values(), color=["#c0392b", "#e67e22", "#f1c40f", "#1ba755", "#7f8c8d"]) 
        ax3.set_title("Ordens por Prioridade")
        ax3.tick_params(axis='x', rotation=15)
        FigureCanvasTkAgg(fig3, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True)


    def _montar_os_mes(self):
        frame_os = tb.Frame(self.content_frame)
        frame_os.pack(fill="both", expand=False, pady=10)

        tb.Label(frame_os, text="Ordens de Serviço deste mês", font=("Segoe UI", 12, "bold")).pack(anchor="w")

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
        self.tree_os.tag_configure('atrasada', background='#f8d7da', foreground='#c0392b', font=('Segoe UI', 10, 'bold'))

        self.carregar_os_mes()

    def carregar_os_mes(self):
        for item in self.tree_os.get_children():
            self.tree_os.delete(item)

        hoje = datetime.today().date()
        manutencoes = manutencao_dao.listar_manutencoes()

        os_mes = [m for m in manutencoes if m.data_prevista and m.data_prevista.month == hoje.month and m.data_prevista.year == hoje.year and (m.tipo or "").lower()=="preventiva"]

        for i, m in enumerate(os_mes):
            eq = m.equipamento.nome if m.equipamento else "N/A"
            resp = m.responsavel.nome if m.responsavel else "N/A"
            data = m.data_prevista.strftime("%d/%m/%Y") if m.data_prevista else ""
            prioridade = m.prioridade if m.prioridade else "Sem Prioridade"

            if m.data_prevista < hoje and (m.status or "").lower() not in ('concluida', 'revisada'):
                tag = 'atrasada'
            else:
                tag = 'par' if i % 2 == 0 else 'impar'

            self.tree_os.insert("", "end", values=(m.id, m.tipo, eq, resp, data, prioridade, m.status), tags=(tag,))


