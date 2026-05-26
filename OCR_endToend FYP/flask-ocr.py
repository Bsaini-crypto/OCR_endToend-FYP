from flask import Flask, request, jsonify
import tempfile
import os
import re
import json
import pdfplumber
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import logging

# Import custom modules
from storage import LocalStorage
from airtable_client import AirtableClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize storage and Airtable client
try:
    storage = LocalStorage(storage_dir=os.getenv("STORAGE_DIR", "records"))
    logger.info("Local storage initialized")
except Exception as e:
    logger.error(f"Failed to initialize local storage: {e}")
    storage = None

try:
    airtable_client = AirtableClient()
    logger.info("Airtable client initialized")
except Exception as e:
    logger.warning(f"Airtable client not initialized: {e}. Airtable integration will be disabled.")
    airtable_client = None

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "OCR API",
        "storage": {
            "local": storage is not None,
            "airtable": airtable_client is not None
        }
    }), 200

def ocr_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        if not text.strip():
            return "Error: No text could be extracted from the PDF."
        return text
    except Exception as e:
        return f"Error performing OCR: {str(e)}"

def sanitize_json_response(response):
    try:
        # Remove any code block formatting like ```json
        cleaned_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
        cleaned_response = cleaned_response.strip()  # Remove leading/trailing spaces
        
        # Attempt to load the cleaned response as JSON
        json_data = json.loads(cleaned_response)
        return json_data
    except json.JSONDecodeError as e:
        app.logger.error(f"JSON Decode Error: {str(e)}")
        return None

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        uploaded_file = request.files['file']
        
        if uploaded_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name
        
        # Perform OCR on the PDF
        ocr_text = ocr_from_pdf(temp_path)
        
        if ocr_text.startswith("Error:"):
            return jsonify({"error": ocr_text}), 500
        
        # Load extracted text into the LLM for understanding
        openai_api_key = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(temperature=0, model_name="gpt-4", openai_api_key=openai_api_key)
        
        template = """
        You are given a text extracted from a PDF document. Your task is to infer all relevant fields and data from the text 
        and structure it in a JSON format without any manual mapping of fields. Please focus on extracting important data points that might be useful to the user.
        Do not hallucinate, be very accurate and only extract the fields that actually exist in the PDF file.
        
        Text:
        {document_text}
        
        Please return the relevant data in JSON format.
        """
        
        prompt = PromptTemplate(template=template, input_variables=["document_text"])
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Use the LLM to generate JSON
        result = chain.run(document_text=ocr_text)
        
        # Sanitize and parse the result to JSON
        sanitized_json = sanitize_json_response(result)
        
        # Cleanup: remove the temporary file after use
        os.remove(temp_path)
        
        if not sanitized_json:
            return jsonify({"error": "Failed to generate valid JSON."}), 500
        
        # Save to local storage
        saved_file_path = None
        if storage:
            try:
                saved_file_path = storage.save_record(sanitized_json)
                logger.info(f"Record saved locally: {saved_file_path}")
            except Exception as e:
                logger.error(f"Failed to save record locally: {e}")
                # Continue even if local save fails
        
        # Insert to Airtable
        airtable_record_id = None
        airtable_error = None
        if airtable_client:
            try:
                airtable_record = airtable_client.create_record(sanitized_json)
                airtable_record_id = airtable_record.get('id')
                logger.info(f"Record inserted to Airtable: {airtable_record_id}")
            except Exception as e:
                error_msg = str(e)
                airtable_error = error_msg
                logger.error(f"Failed to insert record to Airtable: {error_msg}")
                # Log full exception for debugging
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Continue even if Airtable insertion fails
        
        # Prepare response
        response = {
            "data": sanitized_json,
            "status": "success",
            "storage": {
                "local": {
                    "saved": saved_file_path is not None,
                    "file_path": saved_file_path
                } if storage else {"enabled": False},
                "airtable": {
                    "inserted": airtable_record_id is not None,
                    "record_id": airtable_record_id,
                    "error": airtable_error if airtable_error else None
                } if airtable_client else {"enabled": False}
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        app.logger.error(f"Error processing PDF: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)