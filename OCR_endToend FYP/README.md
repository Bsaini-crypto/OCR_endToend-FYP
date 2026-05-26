# PDF OCR and Data Extraction with CRM Integration

An end-to-end OCR solution that extracts data from PDF files using OCR and AI, then saves records locally and inserts them into Airtable CRM.

## Features

- 📄 **PDF Processing**: Extract text from PDF files using OCR (Tesseract) or direct text extraction
- 🤖 **AI-Powered Extraction**: Uses GPT-4 to intelligently structure extracted data into JSON
- 💾 **Local Storage**: Automatically saves each processed record to a local folder
- 🔗 **CRM Integration**: Inserts records into Airtable for easy management
- 🐳 **Docker Support**: Fully containerized for easy deployment
- 🌐 **REST API**: Flask-based API for easy integration

## Project Structure

```
OCR/
├── flask-ocr.py          # Flask API endpoint (main API)
├── ocr.py                # Streamlit UI version
├── storage.py            # Local file storage module
├── airtable_client.py    # Airtable CRM integration
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.9+ (for local development)
- Airtable account with API access
- OpenAI API key

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Airtable CRM Configuration
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
AIRTABLE_TABLE_NAME=Records

# Local Storage Configuration (optional)
STORAGE_DIR=records
```

### 2. Airtable Setup

1. **Get your Airtable API Key**:
   - Go to https://airtable.com/create/tokens
   - Create a new personal access token
   - Copy the token to `AIRTABLE_API_KEY` in your `.env` file

2. **Get your Base ID**:
   - Open your Airtable base
   - Look at the URL: `https://airtable.com/{BASE_ID}/...`
   - Copy the Base ID to `AIRTABLE_BASE_ID` in your `.env` file

3. **Create a Table**:
   - Create a table in your Airtable base (or use an existing one)
   - The table name should match `AIRTABLE_TABLE_NAME` (default: "Records")
   - **Important**: The table fields should match the JSON keys that will be extracted from your PDFs
   - You can start with a simple table and add fields as needed

### 3. Docker Deployment (Recommended)

1. **Build the Docker image**:
   ```bash
   docker build -t ocr-api .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name ocr-api \
     -p 5002:5002 \
     --env-file .env \
     -v $(pwd)/records:/app/records \
     ocr-api
   ```

   Or use Docker Compose (create `docker-compose.yml`):
   ```yaml
   version: '3.8'
   services:
     ocr-api:
       build: .
       ports:
         - "5002:5002"
       env_file:
         - .env
       volumes:
         - ./records:/app/records
       command: python flask-ocr.py
   ```

   Then run:
   ```bash
   docker-compose up -d
   ```

### 4. Local Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install system dependencies** (for OCR):
   - **Windows**: Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
   - **Linux**: `sudo apt-get install tesseract-ocr poppler-utils`
   - **macOS**: `brew install tesseract poppler`

3. **Run the Flask API**:
   ```bash
   python flask-ocr.py
   ```

   The API will be available at `http://localhost:5002`

## API Usage

### Endpoint: `/process_pdf`

**Method**: `POST`

**Content-Type**: `multipart/form-data`

**Request**:
- `file`: PDF file to process

**Response**:
```json
{
  "data": {
    // Extracted JSON data from PDF
  },
  "status": "success",
  "storage": {
    "local": {
      "saved": true,
      "file_path": "records/record_20240101_120000_123456.docx"
    },
    "airtable": {
      "inserted": true,
      "record_id": "recXXXXXXXXXXXXXX"
    }
  }
}
```

### Example using cURL:

```bash
curl -X POST http://localhost:5002/process_pdf \
  -F "file=@document.pdf"
```

### Example using Python:

```python
import requests

url = "http://localhost:5002/process_pdf"
files = {"file": open("document.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## How It Works

1. **PDF Upload**: User uploads a PDF file via the API
2. **Text Extraction**: The system extracts text using OCR (Tesseract) or direct PDF text extraction
3. **AI Processing**: GPT-4 analyzes the extracted text and structures it into JSON
4. **Local Storage**: The record is saved as a Word document (.docx) to the local `records/` folder with a timestamp
5. **CRM Insertion**: The record is automatically inserted into your Airtable table (with nested data flattened)
6. **Response**: The API returns the extracted data along with storage status

## Airtable Table Schema

Your Airtable table should have fields that match the **flattened** field names from the extracted JSON. The system automatically flattens nested structures:

**Nested JSON:**
```json
{
  "Invoice": {"Number": "123", "Date": "2024-01-15"},
  "Customer": {"Name": "John"}
}
```

**Flattened to Airtable fields:**
- `Invoice - Number` (Single line text)
- `Invoice - Date` (Single line text or Date)
- `Customer - Name` (Single line text)

**Important Notes:**
- Field names are flattened with " - " separator for nested objects
- Arrays are converted to formatted text strings
- Field names must match exactly (case-sensitive)
- See `AIRTABLE_SETUP.md` for detailed mapping guide

**Example fields for invoices:**
- `Invoice - Invoice Number` (Single line text)
- `Invoice - Date` (Date or Single line text)
- `Bill To - Customer Name` (Single line text)
- `Items` (Long text) - formatted as numbered list
- `TOTAL` (Single line text or Number)

## Error Handling

- If local storage fails, the API will continue and return the data
- If Airtable insertion fails, the API will continue and return the data
- Both failures are logged and included in the response status
- The API always returns the extracted JSON data even if storage fails

## Troubleshooting

### Airtable Integration Issues

1. **"AIRTABLE_API_KEY environment variable is required"**
   - Make sure your `.env` file contains `AIRTABLE_API_KEY`
   - Check that the API key is valid and has proper permissions

2. **"AIRTABLE_BASE_ID environment variable is required"**
   - Verify your Base ID is correct in the `.env` file
   - Check that you have access to the base

3. **Field mapping errors**
   - Ensure Airtable field names exactly match JSON keys (case-sensitive)
   - Check that field types are compatible (e.g., numbers, dates, text)

### Local Storage Issues

1. **Permission errors**
   - Ensure the `records/` directory is writable
   - Check Docker volume permissions if using containers

### OCR Issues

1. **Tesseract not found**
   - Verify Tesseract is installed in the Docker container
   - Check the Dockerfile includes Tesseract installation

## Development

### Running Tests

```bash
# Test the API endpoint
curl -X POST http://localhost:5002/process_pdf -F "file=@test.pdf"
```

### Viewing Logs

```bash
# Docker logs
docker logs ocr-api

# Or follow logs
docker logs -f ocr-api
```

## License

This project is for educational purposes.

## Support

For issues or questions, please check the troubleshooting section or review the logs for detailed error messages.

