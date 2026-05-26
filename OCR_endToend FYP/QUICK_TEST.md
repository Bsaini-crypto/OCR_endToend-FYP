# Quick Test Guide

## Step 1: Create a Sample PDF (Optional)

If you don't have a PDF to test with, create one:

```powershell
# Install reportlab (one-time)
pip install reportlab

# Create sample PDF
python create_sample_pdf.py
```

This creates `sample_invoice.pdf` in the current directory.

## Step 2: Test the API

### Easy Way (Python Script)

```powershell
# Install requests if needed
pip install requests

# Run the test
python test_api.py sample_invoice.pdf
```

### Quick Way (cURL)

```powershell
# Health check
curl http://localhost:5002/

# Process PDF
curl -X POST http://localhost:5002/process_pdf -F "file=@sample_invoice.pdf"
```

### PowerShell Way

```powershell
# Health check
Invoke-RestMethod -Uri http://localhost:5002/

# Process PDF
$uri = "http://localhost:5002/process_pdf"
$form = @{ file = Get-Item -Path "sample_invoice.pdf" }
Invoke-RestMethod -Uri $uri -Method Post -Form $form
```

## Step 3: Check Results

1. **Check the response** - Should show extracted JSON data
2. **Check `records/` folder** - Should have a new JSON file
3. **Check Airtable** - Should have a new record (if configured)

## That's It! 🎉

For more detailed testing options, see `TESTING.md`

