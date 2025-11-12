import os
import re
from datetime import datetime, date
from tkinter import messagebox
from src.dao import manutencao_dao
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from src.dao import setor_dao, equipamento_dao, planejamento_dao



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
            # tenta formato ISO
            return datetime.strptime(str(date_str), "%Y-%m-%d").date()
        except Exception:
            return None

def _format_date_safe(date_obj):
    if not date_obj:
        return ""
    return date_obj.strftime("%d/%m/%Y")
class LaudoUtil:

    @staticmethod
    def listar_laudos():
        """
        Retorna apenas manutenções que possuem laudo anexado.
        Pode ser usado para preencher tabelas, exportar, etc.
        """
        manutencoes = manutencao_dao.listar_manutencoes()
        return [m for m in manutencoes if getattr(m, 'laudo', None)]


    @staticmethod
    def dados_para_tabela():
        """
        Retorna lista de tuplas formatadas para exibição em TreeView ou relatórios.
        (id, os, equipamento, data, responsável, arquivo)
        """
        laudos = LaudoUtil.listar_laudos()
        result = []

        for m in laudos:
            equipamento = m.equipamento.nome if m.equipamento else "N/A"
            data = m.data.strftime("%d/%m/%Y") if m.data else ""
            responsavel = m.responsavel.nome if m.responsavel else "N/A"
            arquivo = m.laudo if m.laudo else "Sem arquivo"

            result.append((
                m.id,
                getattr(m, 'os', ''),
                equipamento,
                data,
                responsavel,
                arquivo
            ))

        return result


    @staticmethod
    def abrir_laudo(arquivo):
        """Abre o laudo se existir. Retorna True se abriu, False se não."""
        if not arquivo or arquivo == "Sem arquivo":
            return False

        if not os.path.exists(arquivo):
            return False

        try:
            os.startfile(arquivo)  # Windows
            return True
        except Exception:
            try:
                # Linux/Mac
                os.system(f'xdg-open "{arquivo}"')
                return True
            except:
                return False


    @staticmethod
    def validar_arquivo(arquivo):
        """Retorna se o arquivo existe fisicamente."""
        return True if arquivo and os.path.exists(arquivo) else False


class RelatorioPDFUtil:

    @staticmethod
    def gerar_relatorio_por_setor():
        """Compatível com painel: chama gerar_por_setor e mostra mensagem de sucesso/erro."""
        try:
            arquivos = RelatorioPDFUtil.gerar_por_setor()
            if not arquivos:
                messagebox.showinfo("Relatório", "Nenhum relatório foi gerado.")
            else:
                messagebox.showinfo("Relatório gerado", f"Relatórios por setor gerados com sucesso na pasta 'relatorios'.")
        except Exception as e:
            messagebox.showerror("Erro ao gerar relatório", str(e))


    @staticmethod
    def gerar_por_setor(output_folder='relatorios', logo_path='image/favicon.png'):
        """
        Gera um PDF por setor em /relatorios
        Retorna uma lista com caminhos dos PDFs gerados
        """
        setores = setor_dao.listar_setores()
        equipamentos = equipamento_dao.listar_equipamentos()
        planejamentos = planejamento_dao.listar_planejamentos()

        # mapeia id -> planejamentos ligados ao equipamento
        planos_por_equip = {}
        for p in planejamentos:
            if not p.equipamento or not getattr(p.equipamento, 'id', None):
                continue
            if p.tipo and p.tipo.lower() != 'preventiva':
                continue
            planos_por_equip.setdefault(p.equipamento.id, []).append(p)

        os.makedirs(output_folder, exist_ok=True)
        arquivos_gerados = []

        for setor in setores:
            safe_name = re.sub(r"[^0-9a-zA-ZáéíóúÁÉÍÓÚãõâêôçÇ _-]", "", (setor.nome or "setor")).strip()
            safe_name = safe_name.replace(' ', '_') or f"setor_{setor.id}"
            filename = os.path.join(output_folder, f"{safe_name}.pdf")

            doc = SimpleDocTemplate(
                filename, pagesize=A4,
                rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=35
            )

            styles = getSampleStyleSheet()
            styleH = styles['Heading1']
            small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, leading=11)
            small_bold = ParagraphStyle('small_bold', parent=styles['Normal'], fontSize=10, leading=12)
            title_style = ParagraphStyle('title', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#2c3e50'))

            elements = []

            # Cabeçalho elegante com logo pequeno e título
            try:
                img = Image(logo_path, width=1.1*cm, height=1.1*cm)
                header = Table(
                    [[img, Paragraph("<b>ManuSys</b>", title_style)]],
                    colWidths=[1.2*cm, 13*cm], hAlign='LEFT')
            except Exception:
                header = Table([[Paragraph("<b>ManuSys</b>", title_style)]], colWidths=[14*cm], hAlign='LEFT')
            header.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            elements.append(header)
            elements.append(Spacer(1, 6))

            # Bloco de informações do setor
            info_table = Table([
                [Paragraph(f"<b>Setor:</b> {setor.nome}", small_bold),
                 Paragraph(f"<b>Responsável:</b> {setor.responsavel}", small_bold),
                 Paragraph(f"<b>Gerado em:</b> {datetime.today().strftime('%d/%m/%Y %H:%M')}", small_bold)]
            ], colWidths=[6*cm, 4.5*cm, 3.5*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#eaf1fb')),
                ('BOX', (0,0), (-1,0), 0.5, colors.HexColor('#2980b9')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 10))

            # Tabela de equipamentos
            data_tabela = [[
                Paragraph("<b>ID</b>", small_bold),
                Paragraph("<b>Nome</b>", small_bold),
                Paragraph("<b>Nº Série</b>", small_bold),
                Paragraph("<b>Tipo</b>", small_bold),
                Paragraph("<b>Periodicidade</b>", small_bold),
                Paragraph("<b>Próxima Manutenção</b>", small_bold),
            ]]

            eqs = [e for e in equipamentos if str(getattr(e, 'setor', '')) == str(setor.id)]
            if not eqs:
                data_tabela.append([Paragraph("-", small)] * 6)

            zebra_colors = [colors.whitesmoke, colors.HexColor('#f2f6fa')]
            row_idx = 1
            for eq in eqs:
                planos = planos_por_equip.get(eq.id, [])
                if planos:
                    descricoes = []
                    datas_validas = []
                    for p in planos:
                        freq = p.frequencia or (f"{p.dias_previstos} dias" if p.dias_previstos else "N/A")
                        try:
                            prox_data = p.proxima_data()
                        except Exception:
                            prox_data = None
                        prox_str = _format_date_safe(prox_data) if prox_data else "Sem data prevista"
                        descricoes.append(f"{freq} -> {prox_str}")
                        d = _parse_date_obj(prox_data)
                        if d:
                            datas_validas.append(d)
                    periodicidade = "<br/>".join(descricoes)
                    next_str = _format_date_safe(min(datas_validas)) if datas_validas else "Sem data prevista"
                else:
                    periodicidade = "Sem planejamento"
                    next_str = "Sem data prevista"
                data_tabela.append([
                    Paragraph(str(eq.id), small),
                    Paragraph(eq.nome or "", small),
                    Paragraph(getattr(eq, "numero_serie", "") or "", small),
                    Paragraph(getattr(eq, "tipo", "") or "", small),
                    Paragraph(periodicidade, small),
                    Paragraph(next_str, small),
                ])
                row_idx += 1

            col_widths = [1.4*cm, 5.0*cm, 2.8*cm, 2.5*cm, 4.5*cm, 1.8*cm]
            tabela = Table(data_tabela, colWidths=col_widths, repeatRows=1)
            # Estilo da tabela: header colorido, zebra rows, borda azul
            table_style = [
                ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#2980b9')),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2980b9')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ]
            # Zebra rows
            for i in range(1, len(data_tabela)):
                table_style.append(('BACKGROUND', (0,i), (-1,i), zebra_colors[(i-1)%2]))
            tabela.setStyle(TableStyle(table_style))
            elements.append(tabela)
            elements.append(Spacer(1, 8))

            def _footer(canvas, doc_obj):
                canvas.saveState()
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.HexColor('#2980b9'))
                canvas.drawRightString(A4[0] - 40, 20, f"Página {doc_obj.page}")
                canvas.restoreState()

            doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
            arquivos_gerados.append(filename)

        return arquivos_gerados
