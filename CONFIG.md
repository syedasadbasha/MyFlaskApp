# Email and WhatsApp Configuration File

# ==================== EMAIL CONFIGURATION ====================
# Gmail SMTP Configuration

# 1. Get your Gmail email address
EMAIL_SENDER = "your_email@gmail.com"

# 2. Generate Gmail App Password (NOT your regular password):
#    - Go to: https://myaccount.google.com/apppasswords
#    - Make sure 2-Factor Authentication is enabled
#    - Generate an "App password" for Mail
#    - Use this password below (NOT your Gmail password)
EMAIL_PASSWORD = "your_gmail_app_password"

# Alternative: Use environment variable
# Set in your system: FLASK_EMAIL_PASSWORD="your_password"


# ==================== WHATSAPP CONFIGURATION (TWILIO) ====================
# To enable WhatsApp messaging, you need Twilio account

# 1. Create account at: https://www.twilio.com
# 2. Go to Twilio Console: https://console.twilio.com
# 3. Find your Account SID and Auth Token
# 4. Set up WhatsApp Sandbox

WHATSAPP_ACCOUNT_SID = "your_twilio_account_sid"
WHATSAPP_AUTH_TOKEN = "your_twilio_auth_token"

# Twilio WhatsApp Sandbox Number (default)
# This is provided by Twilio (e.g., +14155552671)
WHATSAPP_PHONE_NUMBER = "+14155552671"

# Alternative: Use environment variables
# Set in your system:
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_WHATSAPP_NUMBER


# ==================== SETUP INSTRUCTIONS ====================

# EMAIL SETUP (Gmail):
# 1. Enable 2-Factor Authentication on Gmail account
# 2. Visit: https://myaccount.google.com/apppasswords
# 3. Create new App Password for "Mail" and "Windows"
# 4. Copy the 16-character password
# 5. Update EMAIL_PASSWORD above

# WHATSAPP SETUP (Twilio):
# 1. Sign up at: https://www.twilio.com
# 2. Go to: https://console.twilio.com
# 3. Find Account SID and Auth Token (under Account Settings)
# 4. Go to: https://console.twilio.com/develop/sms/try-it-out/whatsapp-sandbox-learn
# 5. Set up WhatsApp Sandbox (join the test conversation)
# 6. Update the configuration values below

# For Production WhatsApp (paid):
# - You need Twilio Business Account verification
# - Phone number must be verified for production

# ==================== TESTING ====================

# Test Email: Send a test email from Python
# python -c "from app import send_email; send_email('your_email@gmail.com', 'Test', 'Hello!')"

# Test WhatsApp: Send a test message
# python -c "from app import send_whatsapp; send_whatsapp('+919876543210', 'Test message')"
