import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER

class OrdemServicoReportLab:
    def __init__(self, manutencao, logo_path='image/favicon.png', output_folder='OS_Reports'):
        self.manutencao = manutencao
        self.logo_path = logo_path
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self.small = ParagraphStyle('small', parent=self.styles['Normal'], fontSize=10, leading=13)
        self.small_bold = ParagraphStyle('small_bold', parent=self.styles['Normal'], fontSize=11, leading=14)
        self.title_style = ParagraphStyle('title', parent=self.styles['Heading1'],
                                          fontSize=18, textColor=colors.HexColor('#2c3e50'), alignment=TA_CENTER)

    def gerar_pdf(self):
        filename = os.path.join(self.output_folder, f"OS_{self.manutencao['id']}.pdf")
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=35)
        elements = []

        # Cabeçalho com logo
        try:
            img = Image(self.logo_path, width=2*cm, height=2*cm)
            header = Table([[img, Paragraph("<b>ManuSys - Ordem de Serviço</b>", self.title_style)]],
                           colWidths=[2.5*cm, 14*cm], hAlign='LEFT')
        except:
            header = Table([[Paragraph("<b>ManuSys - Ordem de Serviço</b>", self.title_style)]], colWidths=[16.5*cm])
        elements.append(header)
        elements.append(HRFlowable(color=colors.HexColor('#2980b9'), thickness=1, width='100%'))
        elements.append(Spacer(1, 10))

        # Informações da manutenção
        data_info = [
            ['ID OS:', str(self.manutencao.get('id', ''))],
            ['Equipamento:', self.manutencao.get('equipamento', '')],
            ['Responsável:', self.manutencao.get('responsavel', '')],
            ['Data Prevista:', self.manutencao.get('data_prevista', datetime.today()).strftime("%d/%m/%Y")],
            ['Status:', self.manutencao.get('status', '')],
            ['Prioridade:', self.manutencao.get('prioridade', '')]
        ]
        table_info = Table(data_info, colWidths=[5*cm, 11*cm])
        table_info.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eaf1fb')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#2980b9')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(table_info)
        elements.append(Spacer(1, 12))

        # Observações / Laudo
        elements.append(Paragraph("<b>Observações / Laudo:</b>", self.small_bold))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(self.manutencao.get('observacoes', ''), self.small))
        elements.append(Spacer(1, 15))

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
        return filename

