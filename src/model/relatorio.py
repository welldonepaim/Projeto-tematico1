import os
import re
from datetime import datetime, date
from tkinter import messagebox
from src.dao import manutencao_dao, setor_dao, equipamento_dao, planejamento_dao
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER

# --------------------------
# Funções auxiliares
# --------------------------
def _parse_date_obj(date_str):
    if not date_str:
        return None
    if isinstance(date_str, datetime):
        return date_str.date()
    if isinstance(date_str, date):
        return date_str
    try:
        return datetime.strptime(str(date_str), "%d/%m/%Y").date()
    except Exception:
        try:
            return datetime.strptime(str(date_str), "%Y-%m-%d").date()
        except Exception:
            return None

def _format_date_safe(date_obj):
    """Formato padrão: DD/MM/YYYY"""
    if not date_obj:
        return ""
    if isinstance(date_obj, str):
        date_obj = _parse_date_obj(date_obj)
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime("%d/%m/%Y")
    return str(date_obj)

def _format_date_month_year(date_obj):
    """Formato MÊS/ANO para próxima manutenção"""
    if not date_obj:
        return ""
    if isinstance(date_obj, str):
        date_obj = _parse_date_obj(date_obj)
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime("%m/%Y")
    return str(date_obj)

# --------------------------
# Classe Laudo Util
# --------------------------
class LaudoUtil:

    @staticmethod
    def listar_laudos():
        """Retorna apenas manutenções que possuem laudo anexado."""
        manutencoes = manutencao_dao.listar_manutencoes()
        return [m for m in manutencoes if getattr(m, 'laudo', None)]

    @staticmethod
    def dados_para_tabela():
        """Retorna lista de tuplas para exibição em relatórios ou TreeView."""
        laudos = LaudoUtil.listar_laudos()
        result = []
        for m in laudos:
            equipamento = m.equipamento.nome if m.equipamento else "N/A"
            data = _format_date_safe(m.data) if hasattr(m, 'data') else ""
            responsavel = m.responsavel.nome if m.responsavel else "N/A"
            arquivo = m.laudo if m.laudo else "Sem arquivo"
            result.append((m.id, getattr(m, 'os', ''), equipamento, data, responsavel, arquivo))
        return result

    @staticmethod
    def abrir_laudo(arquivo):
        if not arquivo or arquivo == "Sem arquivo" or not os.path.exists(arquivo):
            return False
        try:
            os.startfile(arquivo)  # Windows
            return True
        except Exception:
            try:
                os.system(f'xdg-open "{arquivo}"')  # Linux/Mac
                return True
            except:
                return False

    @staticmethod
    def validar_arquivo(arquivo):
        return True if arquivo and os.path.exists(arquivo) else False

# --------------------------
# Classe Relatório PDF
# --------------------------
class RelatorioPDFUtil:

    @staticmethod
    def gerar_relatorio_por_setor():
        try:
            arquivos = RelatorioPDFUtil.gerar_por_setor()
            if not arquivos:
                messagebox.showinfo("Relatório", "Nenhum relatório foi gerado.")
            else:
                messagebox.showinfo("Relatório gerado",
                                    f"Relatórios por setor gerados com sucesso na pasta 'relatorios'.")
        except Exception as e:
            messagebox.showerror("Erro ao gerar relatório", str(e))

    @staticmethod
    def gerar_por_setor(output_folder='relatorios', logo_path='image/favicon.png'):
        setores = setor_dao.listar_setores()
        equipamentos = equipamento_dao.listar_equipamentos()
        planejamentos = planejamento_dao.listar_planejamentos()

        # Mapear planejamentos por equipamento (apenas preventivas)
        planos_por_equip = {}
        for p in planejamentos:
            if not p.equipamento or not getattr(p.equipamento, 'id', None):
                continue
            if p.tipo and p.tipo.lower() != 'preventiva':
                continue
            planos_por_equip.setdefault(p.equipamento.id, []).append(p)

        os.makedirs(output_folder, exist_ok=True)
        arquivos_gerados = []

        # Estilos globais
        styles = getSampleStyleSheet()
        small = ParagraphStyle('small', parent=styles['Normal'], fontSize=10, leading=13)
        small_bold = ParagraphStyle('small_bold', parent=styles['Normal'], fontSize=11, leading=14)
        title_style = ParagraphStyle('title', parent=styles['Heading1'],
                                     fontSize=18, textColor=colors.HexColor('#2c3e50'), alignment=TA_CENTER)

        # Gerar PDF por setor
        for setor in setores:
            safe_name = re.sub(r"[^0-9a-zA-ZáéíóúÁÉÍÓÚãõâêôçÇ _-]", "", (setor.nome or "setor")).strip()
            safe_name = safe_name.replace(' ', '_') or f"setor_{setor.id}"
            filename = os.path.join(output_folder, f"{safe_name}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=35)

            elements = []

            # Cabeçalho
            try:
                img = Image(logo_path, width=2*cm, height=2*cm)
                header = Table([[img, Paragraph("<b>ManuSys</b>", title_style)]],
                               colWidths=[2.5*cm, 14*cm], hAlign='LEFT')
            except Exception:
                header = Table([[Paragraph("<b>ManuSys</b>", title_style)]], colWidths=[16.5*cm], hAlign='LEFT')
            elements.append(header)
            elements.append(HRFlowable(color=colors.HexColor('#2980b9'), thickness=1, width='100%'))
            elements.append(Spacer(1, 10))

            # Informações do setor
            eqs = [e for e in equipamentos if str(getattr(e, 'setor', '')) == str(setor.id)]
            info_data = [
                [Paragraph(f"<b>Setor:</b> {setor.nome}", small_bold),
                 Paragraph(f"<b>Responsável:</b> {getattr(setor, 'responsavel', '')}", small_bold)],
                [Paragraph(f"<b>Gerado em:</b> {datetime.today().strftime('%d/%m/%Y %H:%M')}", small_bold),
                 Paragraph(f"<b>Total Equipamentos:</b> {len(eqs)}", small_bold)]
            ]
            info_table = Table(info_data, colWidths=[8*cm, 8*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eaf1fb')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#2980b9')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 12))

            # Tabela de equipamentos
            data_tabela = [[
                Paragraph("<b>ID</b>", small_bold),
                Paragraph("<b>Nome</b>", small_bold),
                Paragraph("<b>Nº Série</b>", small_bold),
                Paragraph("<b>Tipo</b>", small_bold),
                Paragraph("<b>Periodicidade</b>", small_bold),
                Paragraph("<b>Próxima Manutenção</b>", small_bold),
            ]]

            zebra_colors = [colors.whitesmoke, colors.HexColor('#f2f6fa')]
            if not eqs:
                data_tabela.append([Paragraph("-", small)]*6)
            else:
                for eq in eqs:
                    planos = planos_por_equip.get(eq.id, [])
                    periodicidade, next_str = "Sem planejamento", "Sem data prevista"
                    if planos:
                        descricoes, datas_validas = [], []
                        for p in planos:
                            freq = p.frequencia or (f"{p.dias_previstos} dias" if p.dias_previstos else "N/A")
                            prox_data = _parse_date_obj(p.proxima_data())
                            prox_str = _format_date_month_year(prox_data)
                            descricoes.append(f"{freq} -> {prox_str}")
                            if prox_data: datas_validas.append(prox_data)
                        periodicidade = "\n".join(descricoes)
                        next_str = _format_date_month_year(min(datas_validas)) if datas_validas else "Sem data prevista"
                    data_tabela.append([
                        Paragraph(str(eq.id), small),
                        Paragraph(eq.nome or "", small),
                        Paragraph(getattr(eq, "numero_serie", "") or "", small),
                        Paragraph(getattr(eq, "tipo", "") or "", small),
                        Paragraph(periodicidade, small),
                        Paragraph(next_str, small)
                    ])

            col_widths = [1.5*cm, 6*cm, 3*cm, 2.5*cm, 5*cm, 2*cm]
            tabela = Table(data_tabela, colWidths=col_widths, repeatRows=1)
            style = [
                ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#2980b9')),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2980b9')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ]
            for i in range(1, len(data_tabela)):
                style.append(('BACKGROUND', (0,i), (-1,i), zebra_colors[(i-1)%2]))
            tabela.setStyle(TableStyle(style))
            elements.append(tabela)
            elements.append(Spacer(1, 12))

            # Rodapé
            def _footer(canvas, doc):
                canvas.saveState()
                canvas.setStrokeColor(colors.HexColor('#2980b9'))
                canvas.setLineWidth(0.5)
                canvas.line(40, 35, A4[0]-40, 35)
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.HexColor('#2980b9'))
                canvas.drawRightString(A4[0]-40, 20, f"Página {doc.page}")
                canvas.restoreState()

            doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
            arquivos_gerados.append(filename)

        return arquivos_gerados
