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
from src.model.relatorio import RelatorioPDFUtil

# tentativa de importar reportlab para gerar PDF; se não disponível, avisamos ao usuário
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

def _format_date_safe(val):
    if not val:
        return ""
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
    if not val:
        return None
    if isinstance(val, date):
        return val
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
        try:
            if not REPORTLAB_AVAILABLE:
                messagebox.showwarning("Instale reportlab")
                return
            if 'RelatorioPDFUtil' in globals():
                RelatorioPDFUtil.gerar_relatorio_por_setor()
            else:
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

        # KPI cards
        self.kpi_frame = tb.Frame(self.frame)
        self.kpi_frame.pack(fill="x", pady=6)

        # separador
        tb.Frame(self.frame, height=2, style="secondary.TFrame").pack(fill="x", pady=(0, 8))

        # FRAME ROLÁVEL PARA CONTEÚDO
        self.scroll_container = tb.Frame(self.frame)
        self.scroll_container.pack(fill="both", expand=True)

        self.canvas = tb.Canvas(self.scroll_container)
        self.v_scroll = tb.Scrollbar(self.scroll_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.canvas.pack(side=LEFT, fill="both", expand=True)
        self.v_scroll.pack(side=RIGHT, fill=Y)

        self.inner_frame = tb.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        # montar KPIs (fixos), gráficos e OS dentro do inner_frame (rolável)
        self._montar_kpis()
        self._montar_graficos(outer_frame=self.inner_frame)
        self._montar_os_mes(outer_frame=self.inner_frame)

    def refresh(self):
        try:
            for widget in list(self.kpi_frame.winfo_children()):
                widget.destroy()
            for widget in list(self.inner_frame.winfo_children()):
                widget.destroy()
            self._montar_kpis()
            self._montar_graficos(outer_frame=self.inner_frame)
            self._montar_os_mes(outer_frame=self.inner_frame)
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
        equipamentos = equipamento_dao.listar_equipamentos()
        manutencoes = manutencao_dao.listar_manutencoes()
        planejamentos = planejamento_dao.listar_planejamentos()

        total_equipamentos = len(equipamentos)
        equipamentos_disponiveis = len([e for e in equipamentos if getattr(e, 'status', '') == 'Disponível'])
        ordens_abertas = len([m for m in manutencoes if getattr(m, 'status', '').lower() in ('pendente', 'em análise', 'em manutencão', 'programada')])
        hoje = datetime.today().date()
        ordens_atrasadas = sum(
            1 for m in manutencoes
            if m.data_prevista and getattr(m, 'planejamento', None) and m.data_prevista < hoje and getattr(m, 'status', '').lower() not in ('concluida', 'revisada')
        )

        self._kpi_card(self.kpi_frame, "Equipamentos", total_equipamentos, f"{equipamentos_disponiveis} disponíveis", color=PRIMARY)
        self._kpi_card(self.kpi_frame, "Ordens Abertas", ordens_abertas, "Em andamento", color=WARNING)
        self._kpi_card(self.kpi_frame, "Ordens Atrasadas", ordens_atrasadas, "Requer atenção", color=DANGER)
        self._kpi_card(self.kpi_frame, "Planejamentos", len(planejamentos), "Agendados", color=SUCCESS)

    def _montar_graficos(self, outer_frame):
        frame_graficos = tb.Frame(outer_frame)
        frame_graficos.pack(fill="both", expand=True, pady=10)

        # Gráfico 1: Distribuição equipamentos
        equipamentos = equipamento_dao.listar_equipamentos()
        total_equipamentos = len(equipamentos)
        fig1, ax1 = plt.subplots(figsize=(3.5, 3.5))
        if total_equipamentos == 0:
            ax1.set_title("Equipamentos", fontsize=13)
            ax1.text(0.5, 0.5, 'Sem dados de equipamentos', ha='center', va='center', fontsize=11)
            ax1.axis('off')
        else:
            disp = len([e for e in equipamentos if getattr(e, 'status', '') == 'Disponível'])
            manut = total_equipamentos - disp
            wedges, texts, autotexts = ax1.pie([disp, manut], labels=["Disponíveis", "Em manutenção"], autopct="%1.0f%%",
                                              colors=["#2ecc71", "#e74c3c"], wedgeprops={'edgecolor': '#34495e'})
            for autotext in autotexts: autotext.set_color('white'); autotext.set_fontsize(12)
            for text in texts: text.set_fontsize(11)
            ax1.set_title("Equipamentos", fontsize=13)
        fig1.tight_layout(pad=1.5)
        FigureCanvasTkAgg(fig1, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True, padx=8)

        # Gráfico 2: Ordens por status
        manutencoes = manutencao_dao.listar_manutencoes()
        status_counts = Counter([(m.status or "").capitalize() for m in manutencoes])
        fig2, ax2 = plt.subplots(figsize=(4.5, 3.5))
        bars = ax2.bar(status_counts.keys(), status_counts.values(), color=["#f39c12", "#3498db", "#2ecc71", "#95a5a6"])
        ax2.set_title("Ordens por Status", fontsize=13)
        ax2.tick_params(axis='x', rotation=25, labelsize=11)
        ax2.tick_params(axis='y', labelsize=11)
        for bar in bars: bar.set_edgecolor('#34495e')
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
        for bar in bars2: bar.set_edgecolor('#34495e')
        fig3.tight_layout(pad=1.5)
        FigureCanvasTkAgg(fig3, master=frame_graficos).get_tk_widget().pack(side=LEFT, expand=True, padx=8)

    def _montar_os_mes(self, outer_frame):
        frame_os = tb.Frame(outer_frame)
        frame_os.pack(fill="both", expand=False, pady=10)

        tb.Label(frame_os, text="Ordens de Serviço deste mês", font=("Segoe UI", 12, "bold"), background="#3498db", foreground="#fff").pack(anchor="w", fill="x", pady=(0,2))

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
        todos_planejamentos = planejamento_dao.listar_planejamentos()
        todas_manutencoes = manutencao_dao.listar_manutencoes()
        os_por_planejamento = {m.planejamento.id: m for m in todas_manutencoes if getattr(m, 'planejamento', None)}

        planejamentos_mes = []
        for p in todos_planejamentos:
            data_inicial_obj = _parse_date_obj(p.data_inicial)
            data_para_comparar = data_inicial_obj
            if (p.tipo or "").lower() == "preventiva" and p.last_gerada:
                last_gerada_obj = _parse_date_obj(p.last_gerada)
                if last_gerada_obj and p.dias_previstos:
                    data_para_comparar = last_gerada_obj + timedelta(days=p.dias_previstos)
            if not data_para_comparar:
                continue
            if data_para_comparar.month == hoje.month and data_para_comparar.year == hoje.year:
                planejamentos_mes.append(p)

        for i, p in enumerate(planejamentos_mes):
            manutencao_associada = os_por_planejamento.get(p.id)
            if manutencao_associada:
                status = manutencao_associada.status
                item_id = manutencao_associada.id
                data_prevista = _parse_date_obj(manutencao_associada.data_prevista)
            else:
                status = "Planejada"
                item_id = p.id
                data_prevista = data_para_comparar
            atrasada = False
            if data_prevista and data_prevista < hoje:
                if status.lower() not in ("concluída", "revisada", "em planejamento"):
                    atrasada = True
            tag = 'atrasada' if atrasada else ('par' if i % 2 == 0 else 'impar')
            eq_nome = p.equipamento.nome if p.equipamento else "N/A"
            resp_nome = p.responsavel.nome if p.responsavel else "N/A"
            self.tree_os.insert("", "end",
                                values=(item_id, p.tipo or "", eq_nome, resp_nome,
                                        _format_date_safe(data_prevista),
                                        p.criticidade or "Sem Prioridade",
                                        status),
                                tags=(tag,))
