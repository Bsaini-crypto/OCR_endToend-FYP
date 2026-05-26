# Testing Guide

This guide shows you how to test the OCR API with sample PDFs.

## Quick Test Options

### Option 1: Python Test Script (Recommended)

1. **Install requests library** (if not already installed):
   ```powershell
   pip install requests
   ```

2. **Run the test script**:
   ```powershell
   # Test with a PDF file
   python test_api.py your-file.pdf
   
   # Or let it auto-detect PDFs in current directory
   python test_api.py
   ```

The script will:
- ✅ Check if API is running
- ✅ Process your PDF
- ✅ Show extracted data
- ✅ Display storage status (local & Airtable)
- ✅ Save full response to `test_response.json`

### Option 2: Using cURL (Command Line)

**Health Check**:
```powershell
curl http://localhost:5002/
```

**Process PDF**:
```powershell
curl -X POST http://localhost:5002/process_pdf -F "file=@your-file.pdf"
```

**Save response to file**:
```powershell
curl -X POST http://localhost:5002/process_pdf -F "file=@your-file.pdf" -o response.json
```

### Option 3: Using PowerShell (Windows)

**Health Check**:
```powershell
Invoke-RestMethod -Uri http://localhost:5002/ -Method Get
```

**Process PDF**:
```powershell
$filePath = "your-file.pdf"
$uri = "http://localhost:5002/process_pdf"
$form = @{
    file = Get-Item -Path $filePath
}
Invoke-RestMethod -Uri $uri -Method Post -Form $form | ConvertTo-Json -Depth 10
```

### Option 4: Using Python Requests (Manual)

```python
import requests

# Health check
response = requests.get("http://localhost:5002/")
print(response.json())

# Process PDF
with open("your-file.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:5002/process_pdf", files=files)
    print(response.json())
```

### Option 5: Using Postman or Insomnia

1. Create a new POST request
2. URL: `http://localhost:5002/process_pdf`
3. Body type: `form-data`
4. Add a key named `file` with type `File`
5. Select your PDF file
6. Send request

## Getting Sample PDFs

### Option 1: Create a Simple Test PDF

You can create a simple PDF using Python:

```python
from reportlab.pdfgen import canvas

c = canvas.Canvas("test_invoice.pdf")
c.drawString(100, 750, "Invoice #12345")
c.drawString(100, 730, "Date: 2024-01-15")
c.drawString(100, 710, "Customer: John Doe")
c.drawString(100, 690, "Amount: $1,234.56")
c.drawString(100, 670, "Items:")
c.drawString(100, 650, "- Product A: $500.00")
c.drawString(100, 630, "- Product B: $734.56")
c.save()
```

Install reportlab: `pip install reportlab`

### Option 2: Download Sample PDFs

- **Invoices**: https://www.pdf-invoice.com/
- **Forms**: https://www.pdfescape.com/
- **Documents**: Any PDF document you have

### Option 3: Use Online PDF Generators

- Create a simple document with text
- Export as PDF
- Use it for testing

## Expected Response Format

```json
{
  "data": {
    "Invoice Number": "12345",
    "Date": "2024-01-15",
    "Customer": "John Doe",
    "Amount": "$1,234.56"
  },
  "status": "success",
  "storage": {
    "local": {
      "saved": true,
      "file_path": "records/record_20240115_120000_123456.json"
    },
    "airtable": {
      "inserted": true,
      "record_id": "recXXXXXXXXXXXXXX"
    }
  }
}
```

## Troubleshooting Tests

### API Not Running
```
Error: Cannot connect to API
```
**Solution**: Start the API first
- Docker: `docker-compose up -d`
- Local: `python flask-ocr.py`

### PDF Not Found
```
Error: PDF file not found
```
**Solution**: Check the file path is correct

### Timeout Error
```
Error: Request timed out
```
**Solution**: 
- PDF might be too large
- API might be processing slowly
- Try a smaller PDF first

### Airtable Errors
If Airtable insertion fails, check:
- API key is correct in `.env`
- Base ID is correct
- Table name matches
- Field names in Airtable match JSON keys

## Testing Checklist

- [ ] API health check works
- [ ] PDF processing works
- [ ] Local storage saves files
- [ ] Airtable insertion works (if configured)
- [ ] Error handling works correctly
- [ ] Response format is correct

## Next Steps

After testing:
1. Check `records/` folder for saved JSON files
2. Check your Airtable table for new records
3. Review `test_response.json` for full API response
4. Adjust Airtable table schema if needed

