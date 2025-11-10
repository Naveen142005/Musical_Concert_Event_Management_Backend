from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os


def generate_booking_ticket(
    booking_id: int,
    event_id: int,
    event_name: str,
    event_date: str,
    slot: str,
    venue_name: str,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    ticket_details: list,
    total_tickets: int,
    total_amount: float,
    output_dir: str = "tickets"
):
    """Generate booking ticket PDF for audience"""
    
    os.makedirs(output_dir, exist_ok=True)
    ticket_number = f"TKT{booking_id:06d}"
    output_path = f"{output_dir}/ticket_{ticket_number}.pdf"
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#7C3AED'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
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
    
    subtitle = Paragraph("EVENT TICKET", subtitle_style)
    elements.append(subtitle)
    
    # Ticket Number Box
    ticket_box = Table([[f"TICKET #{ticket_number}"]], colWidths=[6.5*inch])
    ticket_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(ticket_box)
    elements.append(Spacer(1, 0.3*inch))
    
    # Event Details
    elements.append(Paragraph("<b>Event Details:</b>", heading_style))
    event_info = [
        ["Event Name:", event_name],
        ["Event ID:", f"EVT{event_id:05d}"],
        ["Date:", event_date],
        ["Time Slot:", slot],
        ["Venue:", venue_name],
    ]
    
    event_table = Table(event_info, colWidths=[1.5*inch, 5*inch])
    event_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(event_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Customer Details
    elements.append(Paragraph("<b>Ticket Holder:</b>", heading_style))
    customer_info = [
        ["Name:", customer_name],
        ["Email:", customer_email],
        ["Phone:", customer_phone],
        ["Booking Date:", datetime.now().strftime('%d %b %Y, %I:%M %p')]
    ]
    
    customer_table = Table(customer_info, colWidths=[1.5*inch, 5*inch])
    customer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Ticket Breakdown
    elements.append(Paragraph("<b>Ticket Details:</b>", heading_style))
    
    ticket_data = [['Ticket Type', 'Quantity', 'Price', 'Subtotal (Rs.)']]
    
    for ticket in ticket_details:
        price_per_ticket = ticket['subtotal'] / ticket['quantity']
        ticket_data.append([
            ticket['ticket_type'].capitalize(),
            str(ticket['quantity']),
            f"Rs. {price_per_ticket:,.2f}",
            f"Rs. {ticket['subtotal']:,.2f}"
        ])
    
    ticket_table = Table(ticket_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    ticket_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
    ]))
    elements.append(ticket_table)
    elements.append(Spacer(1, 0.15*inch))
    
    # Total Summary
    summary_data = [
        ['Total Tickets:', str(total_tickets)],
        ['Total Amount:', f"Rs. {total_amount:,.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (-2, 0), (-2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (-2, 0), (-1, -1), 11),
        ('LINEABOVE', (-2, -1), (-1, -1), 2, colors.HexColor('#7C3AED')),
        ('FONTSIZE', (-2, -1), (-1, -1), 13),
        ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (-1, -1), (-1, -1), colors.HexColor('#7C3AED')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Status Badge
    status_table = Table([["BOOKING CONFIRMED"]], colWidths=[6.5*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#10B981')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = """
    <b>Important Instructions:</b><br/>
    • Carry a valid photo ID along with this ticket<br/>
    • Gates open 1 hour before the event<br/>
    • Outside food and beverages not permitted<br/>
    • For support, contact: thigalzhieventmanagement@gmail.com<br/><br/>
    <b>Thank you for booking with Thigalzhi®!</b>
    """
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    return output_path
