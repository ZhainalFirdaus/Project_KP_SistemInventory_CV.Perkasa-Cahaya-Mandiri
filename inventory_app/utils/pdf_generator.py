from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO
from datetime import datetime

def generate_surat_jalan_pdf(event_name, location, admin_name, unit_list):
    """
    Generates a professional Surat Jalan PDF.
    unit_list: list of dicts {'sn': ..., 'name': ..., 'category': ...}
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    # 1. Header
    elements.append(Paragraph("CV. PERKASA CAHAYA MANDIRI", title_style))
    elements.append(Paragraph("SURAT JALAN / DELIVERY ORDER", styles['Heading2']))
    elements.append(Spacer(1, 0.5*cm))
    
    # 2. Info Section
    info_data = [
        ["Event:", event_name, "Tanggal:", datetime.utcnow().strftime('%d %B %Y')],
        ["Lokasi:", location, "Admin:", admin_name]
    ]
    info_table = Table(info_data, colWidths=[3*cm, 7*cm, 3*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 1*cm))
    
    # 3. Item Table
    table_data = [["No", "Nama Alat", "Kategori", "Serial Number / SN"]]
    for i, unit in enumerate(unit_list, 1):
        table_data.append([str(i), unit['name'], unit['category'], unit['sn']])
    
    item_table = Table(table_data, colWidths=[1*cm, 7*cm, 4*cm, 5*cm])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3b82f6")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (1,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('ALIGN', (1,1), (1,-1), 'LEFT'), # Align item name to left
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 2*cm))
    
    # 4. Signature Section
    sig_data = [
        ["Disiapkan Oleh,", "", "Diterima Oleh,"],
        ["", "", ""],
        ["", "", ""],
        ["( ____________________ )", "", "( ____________________ )"],
        [admin_name, "", "Kru / Client"]
    ]
    sig_table = Table(sig_data, colWidths=[6*cm, 5*cm, 6*cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
