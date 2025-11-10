from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os


def generate_event_invoice(
    invoice_number: str,
    event_id: int,
    event_name: str,
    event_date: str,
    slot: str,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    venue_data: dict = None,
    band_data: dict = None,
    decoration_data: dict = None,
    snacks_data: dict = None,
    snacks_count: int = 0,
    ticket_details: list = None,
    total_amount: float = 0,
    paid_amount: float = 0,
    payment_type: str = "Full Payment",
    output_dir: str = "invoices"
):
    """Generate professional event invoice PDF"""
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/invoice_{invoice_number}.pdf"
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#7C3AED'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    company_style = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#7C3AED'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # Header
    title = Paragraph("Thigalzhi® Event Management System", title_style)
    elements.append(title)
    
    subtitle = Paragraph(
        "Professional Concert & Event Management Services<br/>Coimbatore, India | thigalzhieventmanagement@gmail.com | +91 98765 43210",
        company_style
    )
    elements.append(subtitle)
    
    # Invoice Info Section
    invoice_info = [
        [Paragraph("<b>INVOICE</b>", heading_style), ""],
        [f"Invoice No: {invoice_number}", f"Date: {datetime.now().strftime('%d %b %Y')}"],
        [f"Event ID: EVT{event_id:05d}", f"Payment Type: {payment_type}"]
    ]
    
    invoice_table = Table(invoice_info, colWidths=[4.5*inch, 2*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Customer Details
    elements.append(Paragraph("<b>Bill To:</b>", heading_style))
    customer_info = [
        [customer_name, ""],
        [f"Email: {customer_email}", f"Phone: {customer_phone}"],
        [f"Event: {event_name}", ""],
        [f"Date: {event_date} | Slot: {slot}", ""]
    ]
    
    customer_table = Table(customer_info, colWidths=[4.5*inch, 2*inch])
    customer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Items Table
    elements.append(Paragraph("<b>Services & Facilities:</b>", heading_style))
    
    items_data = [['#', 'Description', 'Details', 'Amount (Rs.)']]
    item_num = 1
    
    # Venue
    if venue_data:
        items_data.append([
            str(item_num),
            'Venue',
            f"{venue_data.get('name', 'N/A')}\nCapacity: {venue_data.get('capacity', 'N/A')} | Location: {venue_data.get('location', 'N/A')}",
            f"Rs.{venue_data.get('price', 0):,.2f}"
        ])
        item_num += 1
    
    # Band
    if band_data:
        items_data.append([
            str(item_num),
            'Band',
            f"{band_data.get('name', 'N/A')}\nGenre: {band_data.get('genre', 'N/A')} | Members: {band_data.get('member_count', 'N/A')}",
            f"Rs.{band_data.get('price', 0):,.2f}"
        ])
        item_num += 1
    
    # Decoration
    if decoration_data:
        items_data.append([
            str(item_num),
            'Decoration',
            f"{decoration_data.get('name', 'N/A')}\nType: {decoration_data.get('type', 'N/A')}",
            f"Rs.{decoration_data.get('price', 0):,.2f}"
        ])
        item_num += 1
    
    # Snacks
    if snacks_data:
        items_data.append([
            str(item_num),
            'Snacks',
            f"Items: {', '.join(snacks_data.get('snacks', [])) if snacks_data.get('snacks') else 'Custom Menu'}\nCount: {snacks_count} servings",
            f"Rs.{snacks_data.get('price', 0) * snacks_count:,.2f}"
        ])
        item_num += 1
    
    # Tickets
    if ticket_details:
        for ticket in ticket_details:
            items_data.append([
                str(item_num),
                f'Ticket Setup - {ticket["type"]}',
                f"Price: Rs.{ticket['price']} | Available: {ticket['count']} tickets",
                "Included"
            ])
            item_num += 1
    
    items_table = Table(items_data, colWidths=[0.4*inch, 1.5*inch, 3.2*inch, 1.4*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Payment Summary
    # Payment Summary (No GST)
    balance_due = total_amount - paid_amount
    payment_status = "PAID IN FULL" if balance_due == 0 else "PARTIAL PAYMENT"

    summary_data = [
        ['', '', 'Total Amount:', f"Rs.{total_amount:,.2f}"],
        ['', '', 'Amount Paid:', f"Rs.{paid_amount:,.2f}"],
        ['', '', 'Balance Due:', f"Rs.{balance_due:,.2f}"]
    ]

    summary_table = Table(summary_data, colWidths=[0.4*inch, 1.5*inch, 3.2*inch, 1.4*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (-2, 0), (-2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (-2, 0), (-1, -1), 10),
        ('LINEABOVE', (-2, 0), (-1, 0), 1.5, colors.black),
        ('LINEABOVE', (-2, -1), (-1, -1), 2, colors.HexColor('#7C3AED')),
        ('FONTSIZE', (-2, -1), (-1, -1), 12),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (-2, -1), (-1, -1), colors.HexColor('#7C3AED')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    
    summary_table = Table(summary_data, colWidths=[0.4*inch, 1.5*inch, 3.2*inch, 1.4*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (-2, 0), (-2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (-2, 0), (-1, -1), 10),
        ('LINEABOVE', (-2, 2), (-1, 2), 1.5, colors.black),
        ('LINEABOVE', (-2, -1), (-1, -1), 2, colors.HexColor('#7C3AED')),
        ('FONTSIZE', (-2, -1), (-1, -1), 12),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (-2, -1), (-1, -1), colors.HexColor('#7C3AED')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Payment Status Badge
    status_color = colors.HexColor('#10B981') if balance_due == 0 else colors.HexColor('#F59E0B')
    status_table = Table([[payment_status]], colWidths=[6.5*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), status_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = f"""
    <b>Terms & Conditions:</b><br/>
    • Event booking confirmation subject to payment clearance<br/>
    • Cancellation charges apply as per company policy<br/>
    • For queries, contact us at: thigalzhieventmanagement@gmail.com<br/><br/>
    <b>Thank you for choosing Thigalzhi® Event Management System!</b>
    """
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    return output_path
