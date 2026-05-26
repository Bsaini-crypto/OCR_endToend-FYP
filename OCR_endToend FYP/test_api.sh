#!/bin/bash
# Test script for OCR API (Linux/Mac)

API_URL="http://localhost:5002"
ENDPOINT="${API_URL}/process_pdf"

echo "============================================================"
echo "OCR API Test Script"
echo "============================================================"
echo

# Test health check
echo "Testing Health Check..."
echo "----------------------------------------"
curl -s "${API_URL}/" | python -m json.tool
echo
echo

# Test PDF processing
if [ -z "$1" ]; then
    echo "Usage: ./test_api.sh <path_to_pdf_file>"
    echo "Example: ./test_api.sh sample.pdf"
    exit 1
fi

PDF_FILE="$1"

if [ ! -f "$PDF_FILE" ]; then
    echo "Error: PDF file not found: $PDF_FILE"
    exit 1
fi

echo "Processing PDF: $PDF_FILE"
echo "----------------------------------------"
echo "⏳ Processing... (this may take a minute)"
echo

response=$(curl -s -X POST "${ENDPOINT}" -F "file=@${PDF_FILE}")

echo "$response" | python -m json.tool > test_response.json

echo
echo "✅ Response saved to test_response.json"
echo "============================================================"

