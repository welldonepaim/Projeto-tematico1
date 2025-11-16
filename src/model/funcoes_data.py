import os
import re
from datetime import datetime
from tkinter import messagebox
from src.dao import manutencao_dao
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from src.dao import setor_dao, equipamento_dao, planejamento_dao
from src.utils.funcoes_data import _format_date_safe, _parse_date_obj  

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

            safe_name = re.sub(r"[^0-9a-zA-ZáéíóúÁÉÍÓÚãõâêôçÇ _-]",
                               "", (setor.nome or "setor")).strip()
            safe_name = safe_name.replace(' ', '_') or f"setor_{setor.id}"
            filename = os.path.join(output_folder, f"{safe_name}.pdf")

            doc = SimpleDocTemplate(
                filename, pagesize=A4,
                rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40
            )

            styles = getSampleStyleSheet()
            styleH = styles['Heading1']
            small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, leading=11)
            small_bold = ParagraphStyle('small_bold', parent=styles['Normal'], fontSize=10, leading=12)

            elements = []

            # cabeçalho
            try:
                img = Image(logo_path, width=2*cm, height=2*cm)
                header = Table([[img, Paragraph("<b>ManuSys</b>", styles['BodyText'])]],
                               colWidths=[2*cm, 12*cm])
            except Exception:
                header = Table([[Paragraph("<b>ManuSys</b>", styles['BodyText'])]],
                               colWidths=[14*cm])

            header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            elements.append(header)
            elements.append(Spacer(1, 8))

            elements.append(Paragraph(f"Relatório - Setor: <b>{setor.nome}</b>", styleH))
            elements.append(Paragraph(f"Responsável: {setor.responsavel}", small))
            elements.append(Paragraph(f"Gerado em: {datetime.today().strftime('%d/%m/%Y %H:%M')}", small))
            elements.append(Spacer(1, 12))

            # tabela
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

            col_widths = [1.4*cm, 5.0*cm, 2.8*cm, 2.5*cm, 4.5*cm, 1.8*cm]

            tabela = Table(data_tabela, colWidths=col_widths, repeatRows=1)
            tabela.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))

            elements.append(tabela)

            def _footer(canvas, doc_obj):
                canvas.saveState()
                canvas.setFont('Helvetica', 8)
                canvas.drawRightString(A4[0] - 40, 20, f"Página {doc_obj.page}")
                canvas.restoreState()

            doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)

            arquivos_gerados.append(filename)

        return arquivos_gerados
