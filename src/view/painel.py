from datetime import datetime, timedelta, date
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, Y, INFO, PRIMARY, SUCCESS, DANGER, WARNING
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.dao import manutencao_dao, equipamento_dao, planejamento_dao
from src.dao import setor_dao
import os
from tkinter import messagebox
from src.utils.relatorio import RelatorioPDFUtil

# tentativa de importar reportlab para gerar PDF; se não disponível, avisamos ao usuário
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def _format_date_safe(val):
    """Formata um valor que pode ser date/datetime ou string 'YYYY-MM-DD' (ou com 'T') para 'DD/MM/YYYY'."""
    if not val:
        return ""
    # já é date/datetime
    if hasattr(val, 'strftime'):
        try:
            return val.strftime('%d/%m/%Y')
        except Exception:
            return str(val)
    s = str(val)
    if 'T' in s:
        s = s.split('T')[0]
    try:
        return datetime.strptime(s, '%Y-%m-%d').strftime('%d/%m/%Y')
    except Exception:
        return s


def _parse_date_obj(val):
    """Tenta converter val (date/datetime/str) para um objeto datetime.date. Retorna None se não for possível."""
    if not val:
        return None
    if isinstance(val, date):
        return val
    # val may be datetime
    if hasattr(val, 'date') and not hasattr(val, 'strftime'):
        try:
            return val.date()
        except Exception:
            pass
    s = str(val)
    if 'T' in s:
        s = s.split('T')[0]
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except Exception:
        return None


class AbaPainel:
    def gerar_relatorio_pdf(self):
        """Gera relatório PDF por setor usando utilitário ou exibe mensagem de erro se falhar."""
        try:
            if not REPORTLAB_AVAILABLE:
                messagebox.showwarning("Dependência ausente", "A biblioteca 'reportlab' não está instalada. Instale com: pip install reportlab")
                return
            # Utilitário customizado (se existir)
            if 'RelatorioPDFUtil' in globals():
                RelatorioPDFUtil.gerar_relatorio_por_setor()
            else:
                # Fallback: apenas mensagem
                messagebox.showinfo("Relatório", "Função de geração de relatório não implementada.")
                return
            
        except Exception as e:
            messagebox.showerror("Erro ao gerar relatório", str(e))
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=12)
        notebook.add(self.frame, text="Painel")

        # header com logo e faixa colorida
        header = tb.Frame(self.frame)
        header.pack(fill="x", pady=(0, 8))
        logo_path = os.path.join(os.getcwd(), 'image', 'favicon.png')
        self.logo_img = None
        try:
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img = img.resize((32, 32), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                tb.Label(header, image=self.logo_img).pack(side=LEFT, padx=(0, 8), pady=2)
        except Exception:
            self.logo_img = None
        tb.Label(header, text="Painel de Controle", font=("Segoe UI", 18, "bold"), foreground="#222222").pack(side=LEFT, fill="y", padx=(0,10), pady=2)
        tb.Button(header, text="Relatório por Setor (PDF)", bootstyle=PRIMARY, command=self.gerar_relatorio_pdf).pack(side=RIGHT, padx=6, pady=2)
        # faixa colorida removida para fundo limpo


        # KPI cards
        self.kpi_frame = tb.Frame(self.frame)
        self.kpi_frame.pack(fill="x", pady=6)

        # separador
        tb.Frame(self.frame, height=2, style="secondary.TFrame").pack(fill="x", pady=(0, 8))

        # area de conteúdo (gráficos + tabela)
        self.content_frame = tb.Frame(self.frame)
        self.content_frame.pack(fill="both", expand=True)

        # Monta interface inicial
        self._montar_kpis()
        self._montar_graficos()
        self._montar_os_mes()

       

    def refresh(self):
        try:
            # destrói widgets antigos
            for widget in list(self.kpi_frame.winfo_children()):
                widget.destroy()
            for widget in list(self.content_frame.winfo_children()):
                widget.destroy()

            # recria o conteúdo
            self._montar_kpis()
            self._montar_graficos()
            self._montar_os_mes()
        except Exception as e:
            print("Erro ao atualizar painel:", e)


    def _kpi_card(self, parent, title, value, subtitle="", color=PRIMARY):
        card = tb.Frame(parent, padding=10)
        card.pack(side=LEFT, expand=True, fill="x", padx=6)
        tb.Label(card, text=title, font=("Segoe UI", 10), foreground="#6c757d").pack(anchor="w")
        tb.Label(card, text=str(value), font=("Segoe UI", 22, "bold"), foreground="#222222").pack(anchor="w", pady=(0,2))
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

        # Gráfico 1: Distribuição equipamentos (pie)
        equipamentos = equipamento_dao.listar_equipamentos()
        total_equipamentos = len(equipamentos)
        if total_equipamentos == 0:
            fig1, ax1 = plt.subplots(figsize=(3.5, 3.5))
            ax1.set_title("Equipamentos", fontsize=13)
            ax1.text(0.5, 0.5, 'Sem dados de equipamentos',
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform=ax1.transAxes, fontsize=11)
            ax1.axis('off')
            fig1.tight_layout(pad=1.5)
            FigureCanvasTkAgg(fig1, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True, padx=8)
        else:
            equipamentos_disponiveis = len([e for e in equipamentos if getattr(e, 'status', '') == 'Disponível'])
            equipamentos_manut = total_equipamentos - equipamentos_disponiveis
            fig1, ax1 = plt.subplots(figsize=(3.5, 3.5))
            wedges, texts, autotexts = ax1.pie(
                [equipamentos_disponiveis, equipamentos_manut],
                labels=["Disponíveis", "Em manutenção"],
                autopct="%1.0f%%",
                colors=["#2ecc71", "#e74c3c"],
                wedgeprops={'edgecolor': '#34495e'},
                textprops={'fontsize': 11}
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(12)
            for text in texts:
                text.set_fontsize(11)
            ax1.set_title("Equipamentos", fontsize=13)
            fig1.tight_layout(pad=1.5)
            FigureCanvasTkAgg(fig1, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True, padx=8)

        # Gráfico 2: Ordens por status (bar)
        manutencoes = manutencao_dao.listar_manutencoes()
        status_counts = Counter([(m.status or "").capitalize() for m in manutencoes])
        fig2, ax2 = plt.subplots(figsize=(4.5, 3.5))
        bars = ax2.bar(status_counts.keys(), status_counts.values(), color=["#f39c12", "#3498db", "#2ecc71", "#95a5a6"])
        ax2.set_title("Ordens por Status", fontsize=13)
        ax2.tick_params(axis='x', rotation=25, labelsize=11)
        ax2.tick_params(axis='y', labelsize=11)
        for bar in bars:
            bar.set_edgecolor('#34495e')
        for label in ax2.get_xticklabels():
            label.set_fontsize(11)
        fig2.tight_layout(pad=1.5)
        FigureCanvasTkAgg(fig2, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True, padx=8)

        # Gráfico 3: Prioridade
        prioridades = [m.prioridade if m.prioridade else "Sem Prioridade" for m in manutencoes]
        contagem = Counter(prioridades)
        fig3, ax3 = plt.subplots(figsize=(4.5, 3.5))
        bars2 = ax3.bar(contagem.keys(), contagem.values(), color=["#c0392b", "#e67e22", "#f1c40f", "#1ba755", "#7f8c8d"])
        ax3.set_title("Ordens por Prioridade", fontsize=13)
        ax3.tick_params(axis='x', rotation=15, labelsize=11)
        ax3.tick_params(axis='y', labelsize=11)
        for bar in bars2:
            bar.set_edgecolor('#34495e')
        for label in ax3.get_xticklabels():
            label.set_fontsize(11)
        fig3.tight_layout(pad=1.5)
        FigureCanvasTkAgg(fig3, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True, padx=8)


    def _montar_os_mes(self):
        frame_os = tb.Frame(self.content_frame)
        frame_os.pack(fill="both", expand=False, pady=10)

        # Cabeçalho dinâmico com mês atual
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        hoje = datetime.today().date()
        mes_nome = meses[hoje.month - 1]
        tb.Label(frame_os, text=f"Ordens de Serviço de {mes_nome}", font=("Segoe UI", 12, "bold"), background="#3498db", foreground="#fff").pack(anchor="w", fill="x", pady=(0,2))

        scrollbar = tb.Scrollbar(frame_os)
        scrollbar.pack(side=RIGHT, fill=Y)

        colunas = ("ID", "Tipo", "Equipamento", "Responsável", "Data Prevista", "Prioridade", "Status")
        self.tree_os = tb.Treeview(frame_os, columns=colunas, show="headings", yscrollcommand=scrollbar.set, height=7)

        for col in colunas:
            self.tree_os.heading(col, text=col)
            self.tree_os.column(col, width=130, anchor="center")
        self.tree_os.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree_os.yview)

        # Linhas zebradas e cabeçalho destacado
        self.tree_os.tag_configure('par', background='#f2f2f2', foreground='black')
        self.tree_os.tag_configure('impar', background='white', foreground='black')
        self.tree_os.tag_configure('atrasada', background='#f8d7da', foreground='#c0392b', font=('Segoe UI', 10, 'bold'))

        self.carregar_os_mes()


    def carregar_os_mes(self):
        # limpa a tabela
        for item in self.tree_os.get_children():
            self.tree_os.delete(item)

        hoje = datetime.today().date()
        manutencoes = manutencao_dao.listar_manutencoes()

        # Mostrar apenas manutenções associadas a planejamento
        # 1. Que serão abertas neste mês (data_prevista no mês atual)
        # 2. Ou que foram abertas em meses anteriores e não encerradas
        os_mes = []
        for m in manutencoes:
            if not getattr(m, 'planejamento', None):
                continue  # só mostra OS de planejamento
            if m.data_prevista:
                # OS deste mês
                if m.data_prevista.month == hoje.month and m.data_prevista.year == hoje.year:
                    os_mes.append((m, False))  # False = não é atrasada
                # OS de meses anteriores ainda abertas
                elif m.data_prevista < hoje and (m.data_prevista.month != hoje.month or m.data_prevista.year != hoje.year):
                    if getattr(m, 'status', '').lower() not in ('concluida', 'revisada'):
                        os_mes.append((m, True))  # True = atrasada

        # insere no treeview
        for i, (m, atrasada) in enumerate(os_mes):
            tag = 'atrasada' if atrasada else ('par' if i % 2 == 0 else 'impar')
            self.tree_os.insert(
                "",
                "end",
                values=(
                    m.id,
                    m.tipo or "",
                    m.equipamento.nome if hasattr(m, 'equipamento') and m.equipamento else "",
                    m.responsavel.nome if hasattr(m, 'responsavel') and m.responsavel else "",
                    _format_date_safe(m.data_prevista),
                    m.prioridade or "",
                    m.status or ""
                ),
                tags=(tag,)
            )

