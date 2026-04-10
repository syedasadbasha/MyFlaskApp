from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
try:
    from reportlab.enum.text import TA_CENTER, TA_LEFT, TA_RIGHT
except ImportError:
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///invoices.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.secret_key = 'your_secret_key_change_me'

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Models
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    gst_number = db.Column(db.String(20))
    logo_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.Text)
    items = db.Column(db.Text)  # JSON format
    subtotal = db.Column(db.Float)
    gst_rate = db.Column(db.Float, default=18.0)
    gst_amount = db.Column(db.Float)
    total = db.Column(db.Float)
    status = db.Column(db.String(20), default='draft')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    description = db.Column(db.String(200))
    quantity = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    amount = db.Column(db.Float)

# Helper Functions
def generate_invoice_number():
    """Generate unique invoice number"""
    last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
    if last_invoice:
        number = int(last_invoice.invoice_number.split('-')[1]) + 1
    else:
        number = 1001
    return f"INV-{number}"

def calculate_gst(amount, gst_rate):
    """Calculate GST amount"""
    return round(amount * gst_rate / 100, 2)

def send_email(recipient_email, subject, body, pdf_file=None):
    """Send email with optional PDF attachment"""
    try:
        sender_email = "your_email@gmail.com"  # Change this
        sender_password = "your_app_password"  # Change this (use app password for Gmail)
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "html"))
        
        if pdf_file and os.path.exists(pdf_file):
            with open(pdf_file, 'rb') as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= {pdf_file}")
                message.attach(part)
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {str(e)}")
        return False

def generate_pdf_invoice(invoice_id):
    """Generate PDF invoice"""
    invoice = Invoice.query.get(invoice_id)
    company = Company.query.get(invoice.company_id)
    items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
    
    filename = f"invoice_{invoice.invoice_number}.pdf"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=10,
        alignment=TA_CENTER
    )
    
    # Header with Logo
    if company and company.logo_path and os.path.exists(company.logo_path):
        try:
            img = Image(company.logo_path, width=1.5*inch, height=1*inch)
            story.append(img)
        except:
            pass
    
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice Details
    details_data = [
        ["Invoice No:", invoice.invoice_number, "Date:", datetime.now().strftime("%d %b %Y")],
        ["Status:", invoice.status.upper(), "Due Date:", invoice.due_date.strftime("%d %b %Y") if invoice.due_date else "N/A"],
    ]
    
    if company:
        details_data.append(["Company:", company.name, "GST:", company.gst_number or "N/A"])
    
    details_table = Table(details_data, colWidths=[1.2*inch, 1.8*inch, 1*inch, 1.8*inch])
    details_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Customer Details
    story.append(Paragraph("<b>Bill To:</b>", styles['Heading3']))
    customer_info = f"{invoice.customer_name}<br/>"
    if invoice.customer_address:
        customer_info += f"{invoice.customer_address}<br/>"
    if invoice.customer_phone:
        customer_info += f"Phone: {invoice.customer_phone}<br/>"
    if invoice.customer_email:
        customer_info += f"Email: {invoice.customer_email}"
    story.append(Paragraph(customer_info, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Items Table
    items_data = [["Description", "Qty", "Unit Price (₹)", "Amount (₹)"]]
    for item in items:
        items_data.append([
            item.description,
            f"{item.quantity}",
            f"{item.unit_price:.2f}",
            f"{item.amount:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Totals
    totals_data = [
        ["Subtotal:", f"₹{invoice.subtotal:.2f}"],
        ["GST ({:.0f}%):", f"₹{invoice.gst_amount:.2f}"],
        ["TOTAL:", f"₹{invoice.total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[3.5*inch, 1.9*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(totals_table)
    
    if invoice.notes:
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>Notes:</b>", styles['Heading3']))
        story.append(Paragraph(invoice.notes, styles['Normal']))
    
    doc.build(story)
    return filepath

# Routes
@app.route('/')
def index():
    companies = Company.query.all()
    invoices = Invoice.query.all()
    return render_template('index.html', companies=companies, invoices=invoices)

@app.route('/api/gst-calculate', methods=['POST'])
def gst_calculate():
    """Calculate GST"""
    data = request.json
    amount = float(data.get('amount', 0))
    gst_rate = float(data.get('gst_rate', 18))
    gst = calculate_gst(amount, gst_rate)
    total = amount + gst
    return jsonify({'gst': round(gst, 2), 'total': round(total, 2)})

@app.route('/company/add', methods=['POST'])
def add_company():
    """Add company details"""
    try:
        name = request.form.get('company_name')
        email = request.form.get('company_email')
        phone = request.form.get('company_phone')
        address = request.form.get('company_address')
        gst_number = request.form.get('gst_number')
        
        logo_path = None
        if 'company_logo' in request.files:
            file = request.files['company_logo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(logo_path)
        
        company = Company(
            name=name,
            email=email,
            phone=phone,
            address=address,
            gst_number=gst_number,
            logo_path=logo_path
        )
        db.session.add(company)
        db.session.commit()
        
        flash('Company details saved!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/invoice/create', methods=['POST'])
def create_invoice():
    """Create new invoice"""
    try:
        company_id = request.form.get('company_id')
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        customer_address = request.form.get('customer_address')
        gst_rate = float(request.form.get('gst_rate', 18))
        notes = request.form.get('notes')
        
        invoice_number = generate_invoice_number()
        
        invoice = Invoice(
            invoice_number=invoice_number,
            company_id=company_id if company_id else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_address=customer_address,
            gst_rate=gst_rate,
            notes=notes,
            due_date=datetime.now() + timedelta(days=30)
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        # Add items
        items_data = request.form.getlist('item_description[]')
        quantities = request.form.getlist('item_quantity[]')
        prices = request.form.getlist('item_price[]')
        
        subtotal = 0
        for desc, qty, price in zip(items_data, quantities, prices):
            if desc and qty and price:
                amount = float(qty) * float(price)
                subtotal += amount
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=desc,
                    quantity=float(qty),
                    unit_price=float(price),
                    amount=amount
                )
                db.session.add(item)
        
        gst_amount = calculate_gst(subtotal, gst_rate)
        total = subtotal + gst_amount
        
        invoice.subtotal = subtotal
        invoice.gst_amount = gst_amount
        invoice.total = total
        invoice.status = 'saved'
        
        db.session.commit()
        
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('invoice_detail', invoice_id=invoice.id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/invoice/<int:invoice_id>')
def invoice_detail(invoice_id):
    """View invoice details"""
    invoice = Invoice.query.get_or_404(invoice_id)
    items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
    company = Company.query.get(invoice.company_id) if invoice.company_id else None
    return render_template('invoice_detail.html', invoice=invoice, items=items, company=company)

@app.route('/invoice/<int:invoice_id>/pdf')
def download_pdf(invoice_id):
    """Download invoice as PDF"""
    try:
        pdf_path = generate_pdf_invoice(invoice_id)
        return send_file(pdf_path, as_attachment=True, download_name=f'invoice_{invoice_id}.pdf')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/invoice/<int:invoice_id>/send-email', methods=['POST'])
def send_invoice_email(invoice_id):
    """Send invoice via email"""
    try:
        data = request.json
        recipient_email = data.get('email')
        
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({'success': False, 'message': 'Invoice not found'})
        
        pdf_path = generate_pdf_invoice(invoice_id)
        
        email_body = f"""
        <h2>Invoice {invoice.invoice_number}</h2>
        <p>Dear {invoice.customer_name},</p>
        <p>Please find attached your invoice.</p>
        <p><b>Invoice Details:</b></p>
        <ul>
            <li>Subtotal: ₹{invoice.subtotal:.2f}</li>
            <li>GST ({invoice.gst_rate}%): ₹{invoice.gst_amount:.2f}</li>
            <li>Total: ₹{invoice.total:.2f}</li>
        </ul>
        <p>Thank you!</p>
        """
        
        success = send_email(recipient_email, f"Invoice {invoice.invoice_number}", email_body, pdf_path)
        
        if success:
            invoice.status = 'sent'
            db.session.commit()
            return jsonify({'success': True, 'message': 'Invoice sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send email'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/invoice/<int:invoice_id>/delete', methods=['DELETE'])
def delete_invoice(invoice_id):
    """Delete invoice"""
    try:
        invoice = Invoice.query.get(invoice_id)
        if invoice:
            InvoiceItem.query.filter_by(invoice_id=invoice_id).delete()
            db.session.delete(invoice)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)