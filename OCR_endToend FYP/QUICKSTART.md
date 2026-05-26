# Quick Start Guide

## Step 1: Set Up Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-key
AIRTABLE_API_KEY=pat-your-airtable-key
AIRTABLE_BASE_ID=appYourBaseId
AIRTABLE_TABLE_NAME=Records
STORAGE_DIR=records
```

## Step 2: Set Up Airtable

1. Go to https://airtable.com/create/tokens and create a personal access token
2. Create a base and table (or use existing)
3. Copy your Base ID from the URL: `https://airtable.com/{BASE_ID}/...`
4. Add the token and Base ID to your `.env` file

## Step 3: Run with Docker

```bash
# Build and run
docker-compose up -d

# Or manually
docker build -t ocr-api .
docker run -d -p 5002:5002 --env-file .env -v $(pwd)/records:/app/records ocr-api
```

## Step 4: Test the API

```bash
# Test health check
curl http://localhost:5002/

# Process a PDF
curl -X POST http://localhost:5002/process_pdf -F "file=@your-document.pdf"
```

## Step 5: Check Results

- **Local Storage**: Check the `records/` folder for saved JSON files
- **Airtable**: Check your Airtable table for the new record

## Troubleshooting

- **Airtable errors**: Make sure field names in Airtable match JSON keys exactly
- **Storage errors**: Ensure `records/` directory is writable
- **API errors**: Check logs with `docker logs ocr-api`

