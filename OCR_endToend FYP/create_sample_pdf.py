"""
Create a sample PDF for testing the OCR API.
This script generates a simple invoice-like PDF document.
"""
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
except ImportError:
    print("Error: reportlab is not installed.")
    print("Install it with: pip install reportlab")
    exit(1)

def create_sample_invoice():
    """Create a sample invoice PDF for testing."""
    filename = "sample_invoice.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height - 100, "INVOICE")
    
    # Invoice Details
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    invoice_data = [
        ("Invoice Number:", "INV-2024-001234"),
        ("Date:", "January 15, 2024"),
        ("Due Date:", "February 15, 2024"),
        ("", ""),
        ("Bill To:", ""),
        ("Customer Name:", "John Doe"),
        ("Company:", "Acme Corporation"),
        ("Address:", "123 Main Street"),
        ("City, State ZIP:", "New York, NY 10001"),
        ("Email:", "john.doe@acme.com"),
        ("", ""),
        ("Items:", ""),
        ("", ""),
        ("1. Product A - Premium Package", "$500.00"),
        ("   Quantity: 2 units", ""),
        ("", ""),
        ("2. Product B - Standard Package", "$734.56"),
        ("   Quantity: 1 unit", ""),
        ("", ""),
        ("3. Service Fee - Consultation", "$250.00"),
        ("   Duration: 5 hours", ""),
        ("", ""),
        ("Subtotal:", "$1,484.56"),
        ("Tax (8.5%):", "$126.19"),
        ("Shipping:", "$50.00"),
        ("", ""),
        ("TOTAL:", "$1,660.75"),
        ("", ""),
        ("Payment Terms:", "Net 30"),
        ("Payment Method:", "Bank Transfer"),
        ("", ""),
        ("Notes:", "Thank you for your business!"),
    ]
    
    for label, value in invoice_data:
        if label:
            c.drawString(100, y_position, f"{label} {value}")
        y_position -= 20
        if y_position < 100:
            c.showPage()
            y_position = height - 100
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(100, 50, "This is a sample invoice for testing OCR API.")
    
    c.save()
    print(f"✅ Sample PDF created: {filename}")
    print(f"   You can now test it with: python test_api.py {filename}")
    return filename

if __name__ == "__main__":
    create_sample_invoice()

