from flask import Flask, render_template, request
from reportlab.pdfgen import canvas  # NEW: Import the PDF tool

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # 1. Get the data from the form
    name = request.form['name']
    item = request.form['item']
    price = request.form['price']
    
    # 2. Create the PDF file
    file_name = "invoice.pdf"
    c = canvas.Canvas(file_name)
    
    # 3. Draw text onto the PDF (the numbers are X, Y coordinates on the page)
    c.drawString(100, 750, f"Customer: {name}")
    c.drawString(100, 730, f"Item: {item}")
    c.drawString(100, 710, f"Price: Rs. {price}")
    
    # 4. Save the PDF
    c.save()
    
    return f"Success! {file_name} has been generated for {name}."

if __name__ == '__main__':
    app.run(debug=True)