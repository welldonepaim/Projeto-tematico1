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
    def __init__(self, notebook):
        self.frame = tb.Frame(notebook, padding=12)
        notebook.add(self.frame, text="Painel")

        # header
        header = tb.Frame(self.frame)
        header.pack(fill="x", pady=(0, 8))
        tb.Label(header, text="Painel de Controle", font=("Segoe UI", 18, "bold")).pack(side=LEFT)
        tb.Button(header, text="Atualizar", bootstyle=INFO, command=self.refresh).pack(side=RIGHT)
        tb.Button(header, text="Relatório por Setor (PDF)", bootstyle=PRIMARY, command=self.gerar_relatorio_pdf).pack(side=RIGHT, padx=6)

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

    def gerar_relatorio_pdf(self):
        """Gera um PDF por setor (arquivo: <nome_setor>.pdf) com a lista de equipamentos e próximos planejamentos.

        Melhora a apresentação com um cabeçalho e uma tabela simples.
        """
        if not REPORTLAB_AVAILABLE:
            messagebox.showwarning("Dependência ausente", "A biblioteca 'reportlab' não está instalada. Instale com: pip install reportlab")
            return

        try:
            import re
            setores = setor_dao.listar_setores()
            equipamentos = equipamento_dao.listar_equipamentos()
            planejamentos = planejamento_dao.listar_planejamentos()

            # map equipamento id -> lista de planejamentos preventivos
            planos_por_equip = {}
            for p in planejamentos:
                if not p.equipamento or not getattr(p.equipamento, 'id', None):
                    continue
                if p.tipo and p.tipo.lower() != 'preventiva':
                    continue
                planos_por_equip.setdefault(p.equipamento.id, []).append(p)

            # criar pasta de saída para relatórios
            rel_folder = os.path.join(os.getcwd(), 'relatorios')
            os.makedirs(rel_folder, exist_ok=True)

            for setor in setores:
                # sanitize filename
                safe_name = re.sub(r"[^0-9a-zA-ZáéíóúÁÉÍÓÚãõâêôçÇ _-]", "", (setor.nome or "setor")).strip()
                safe_name = safe_name.replace(' ', '_') or f"setor_{setor.id}"
                filename = os.path.join(rel_folder, f"{safe_name}.pdf")

                # usar platypus para melhor layout e quebrar células longas
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import cm

                doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
                styles = getSampleStyleSheet()
                styleH = styles['Heading1']
                styleN = styles['BodyText']
                small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, leading=11)
                small_bold = ParagraphStyle('small_bold', parent=styles['Normal'], fontSize=10, leading=12, spaceAfter=6)

                elements = []

                # cabeçalho com logo e nome do app
                logo_path = 'image/favicon.png'
                try:
                    img = Image(logo_path, width=2*cm, height=2*cm)
                except Exception:
                    img = None

                header_table_data = []
                left_cells = []
                if img:
                    left_cells.append(img)
                else:
                    left_cells.append(Paragraph('', styleN))
                left_cells.append(Paragraph(f"<b>{'ManuSys'}</b>", styleN))
                header_table_data.append(left_cells)
                header_table = Table([[img, Paragraph(f"<b>{'ManuSys'}</b>")]], colWidths=[2*cm, 12*cm]) if img else Table([[Paragraph(f"<b>{'ManuSys'}</b>")]], colWidths=[14*cm])
                header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                elements.append(header_table)
                elements.append(Spacer(1, 8))

                elements.append(Paragraph(f"Relatório - Setor: <b>{setor.nome}</b>", styleH))
                elements.append(Paragraph(f"Responsável: {setor.responsavel or 'N/A'}", small))
                elements.append(Paragraph(f"Gerado em: {datetime.today().strftime('%d/%m/%Y %H:%M')}", small))
                elements.append(Spacer(1, 12))

                # montar tabela de equipamentos
                data_table = [[
                    Paragraph('<b>ID</b>', small_bold),
                    Paragraph('<b>Nome</b>', small_bold),
                    Paragraph('<b>Nº Série</b>', small_bold),
                    Paragraph('<b>Tipo</b>', small_bold),
                    Paragraph('<b>Periodicidade</b>', small_bold),
                    Paragraph('<b>Próxima Manutenção</b>', small_bold),
                ]]

                eqs = [e for e in equipamentos if str(getattr(e, 'setor', '')) == str(setor.id)]
                if not eqs:
                    data_table.append([
                        Paragraph('-', small),
                        Paragraph('(Nenhum equipamento cadastrado neste setor)', small),
                        Paragraph('-', small),
                        Paragraph('-', small),
                        Paragraph('-', small),
                        Paragraph('-', small),
                    ])
                for eq in eqs:
                    planos = planos_por_equip.get(eq.id, [])
                    if planos:
                        parts = []
                        next_dates = []
                        for p in planos:
                            freq = p.frequencia or (str(p.dias_previstos) + ' dias' if p.dias_previstos else 'N/A')
                            try:
                                prox = p.proxima_data()
                            except Exception:
                                prox = None
                            prox_str = _format_date_safe(prox) if prox else 'Sem data prevista'
                            parts.append(f"{freq} -> {prox_str}")
                            dobj = _parse_date_obj(prox)
                            if dobj:
                                next_dates.append(dobj)
                        periodicidade_text = '<br/>'.join(parts)
                        next_str = _format_date_safe(min(next_dates)) if next_dates else 'Sem data prevista'
                    else:
                        periodicidade_text = 'Sem planejamento'
                        next_str = 'Sem data prevista'

                    data_table.append([
                        Paragraph(str(eq.id), small),
                        Paragraph(str(eq.nome or ''), small),
                        Paragraph(str(getattr(eq, 'numero_serie', '') or ''), small),
                        Paragraph(str(getattr(eq, 'tipo', '') or ''), small),
                        Paragraph(periodicidade_text, small),
                        Paragraph(next_str, small),
                    ])

                # criar table com larguras de coluna (ajustadas ao A4 e margens)
                col_widths = [1.4*cm, 5.0*cm, 2.8*cm, 2.5*cm, 4.5*cm, 1.8*cm]
                tbl = Table(data_table, colWidths=col_widths, repeatRows=1)
                tbl.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('LEFTPADDING', (0,0), (-1,-1), 4),
                    ('RIGHTPADDING', (0,0), (-1,-1), 4),
                    ('ALIGN', (0,0), (0,-1), 'CENTER'),
                    ('ALIGN', (5,0), (5,-1), 'CENTER'),
                ]))

                elements.append(tbl)
                # adicionar rodapé com número de página
                def _footer(canvas_obj, doc_obj):
                    canvas_obj.saveState()
                    footer_text = f"Página {doc_obj.page}"
                    canvas_obj.setFont('Helvetica', 8)
                    canvas_obj.drawRightString(A4[0] - 40, 20, footer_text)
                    canvas_obj.restoreState()

                doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)

            messagebox.showinfo("Relatório gerado", f"Relatórios por setor gerados com sucesso em: {rel_folder}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório: {e}")

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


