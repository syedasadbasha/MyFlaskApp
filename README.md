# GST Invoice Manager

A professional invoice management system for India with automatic GST calculation, PDF generation, and email capabilities.

## ✨ Features

✅ **GST Calculation (India Specific)**
- Support for 5%, 12%, 18%, and 28% GST rates
- Real-time calculation and display
- Itemized invoice breakdown

✅ **Invoice Management**
- Auto-generate unique invoice numbers (INV-XXXX format)
- Create, view, and manage invoices
- Save invoices to SQLite database
- Track invoice status (Draft, Saved, Sent)

✅ **Company Setup**
- Store company details (name, email, phone, address, GST number)
- Upload company logo
- Multiple company support

✅ **Invoice Items**
- Add multiple items per invoice
- Automatic amount calculation (Qty × Price)
- Real-time total updates

✅ **PDF Generation**
- Professional invoice PDFs with company logo
- Included GST breakdown
- Print-ready format

✅ **Email Functionality**
- Send invoices directly via email
- PDF attachment included
- Customize recipient (default to customer email)

## 📋 Requirements

- Python 3.8+
- Flask 3.0+
- SQLAlchemy 3.1+
- ReportLab 4.0+

## 🚀 Installation

### 1. Clone/Extract the Project
```bash
cd MyFlaskApp
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Email (Optional)

To enable email functionality, edit `app.py` and update these lines (around line 95):

```python
sender_email = "your_email@gmail.com"  # Your Gmail address
sender_password = "your_app_password"  # Gmail App Password
```

To get Gmail App Password:
1. Enable 2-Factor Authentication on your Google Account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for Mail
4. Use this password in the code above

## 🏃 Running the Application

```bash
python app.py
```

The app will be available at: **http://127.0.0.1:5000**

## 📖 How to Use

### 1. **Company Setup** (First Time)
   - Go to "🏢 Company" tab
   - Enter company name, GST number, contact details
   - Upload company logo (optional)
   - Click "💾 Save Company Details"

### 2. **Create Invoice**
   - Go to "➕ Create Invoice" tab
   - Select company (if available)
   - Enter customer details
   - Choose GST rate (default 18%)
   - Add invoice items (description, qty, price)
   - System automatically calculates amounts and GST
   - Click "✅ Create Invoice"

### 3. **View Invoices**
   - Go to "📊 All Invoices" tab
   - See all created invoices with amounts and status
   - View full details by clicking "View"

### 4. **Download as PDF**
   - Click "📥 PDF" button next to invoice
   - PDF downloads with company logo, all details, and GST breakdown

### 5. **Send Email** (if email configured)
   - Click "📧 Email" button
   - Invoice PDF is sent to customer email
   - Invoice status changes to "Sent"

## 📊 GST Rates

| Rate | Category | Example |
|------|----------|---------|
| 5% | Essential Items | Food, medicines basic goods |
| 12% | Standard | Packaged goods, services |
| 18% | Regular | Most goods and services |
| 28% | Luxury | High-end items, premium services |

## 📁 File Structure

```
MyFlaskApp/
├── app.py                 # Main application
├── templates/
│   ├── index.html        # Main dashboard
│   └── invoice_detail.html  # Invoice view page
├── uploads/              # Company logos & PDFs
├── invoices.db           # SQLite database
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## 💾 Database

The app uses **SQLite** database with three main tables:

- **Company**: Stores company information
- **Invoice**: Stores invoice details
- **InvoiceItem**: Stores individual line items

Database file: `invoices.db` (auto-created on first run)

## 🔒 Security Notes

⚠️ **Important for Production:**
1. Change `app.secret_key` in `app.py`
2. Use strong email password (App Password)
3. Set `debug=False` in production
4. Use environment variables for sensitive data
5. Implement user authentication

## 🐛 Troubleshooting

### Email Not Sending?
- Verify Gmail credentials are correct
- Check if 2FA is enabled and app password is generated
- Check firewall settings (port 465)

### Database Issues?
- Delete `invoices.db` to reset database
- Ensure `uploads/` folder exists and is writable

### PDF Generation Errors?
- Verify ReportLab is installed: `pip install reportlab==4.0.9`
- Check uploads folder has write permissions

## 🎯 Future Enhancements

- [ ] User authentication & multi-user support
- [ ] Invoice templates customization
- [ ] Recurring invoices
- [ ] Payment tracking
- [ ] SMS notifications
- [ ] Multi-currency support
- [ ] Invoice reminders

## 📝 License

This project is free to use and modify for personal and commercial purposes.

## 👨‍💻 Support

For issues or suggestions, please check the code comments or create a new issue.

---

**Version:** 1.0.0  
**Last Updated:** April 2026  
**Made with ❤️ for Indian businesses**
