import streamlit as st
from langchain_community.vectorstores import FstAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import pytesseract
from pdf2image import convert_from_path
import json
import tempfile
import os
import re

load_dotenv()

# OCR function to extract text from images (scanned PDFs)
def ocr_from_pdf(pdf_path):
    try:
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        poppler_path = r"C:\Program Files\poppler-24.07.0\Library\bin"
        st.write(f"Performing OCR on PDF: {pdf_path}")
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img)
        return ocr_text
    except Exception as e:
        st.error(f"Error performing OCR: {e}")
        return None

# Function to temporarily save the uploaded file and return the path
def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name
        return temp_path
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        return None

# Function to sanitize the response and extract valid JSON
def sanitize_json_response(response):
    try:
        # Remove any code block formatting like ```json
        cleaned_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
        cleaned_response = cleaned_response.strip()  # Remove leading/trailing spaces
        
        # Attempt to load the cleaned response as JSON
        json_data = json.loads(cleaned_response)
        return json_data
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON: {e}")
        return None

def set_page_config():
    st.set_page_config(
        page_title="PDF OCR and Data Extraction",
        page_icon=":bird:",
        layout="centered",
        initial_sidebar_state="auto"
    )

# Function to use GenAI to infer relevant fields and output JSON
def generate_json_response(document_text, chain):
    response = chain.run(document_text=document_text)
    return response

def main():
    set_page_config()

    st.header("PDF OCR and Data Extraction :dog:")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if st.button("Extract and Generate JSON") and uploaded_file:
        st.write("Extracting and generating relevant data in JSON format...")

        # Save the uploaded file and get the path
        pdf_path = save_uploaded_file(uploaded_file)

        if pdf_path:
            # Perform OCR if the PDF is scanned
            ocr_text = ocr_from_pdf(pdf_path)

            if ocr_text:
                st.write("OCR completed successfully.")
                
                # Print OCR output to terminal
                print("OCR Output:")
                print(ocr_text)  # This will log to the terminal

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

                prompt = PromptTemplate(
                    input_variables=["document_text"],
                    template=template
                )

                chain = LLMChain(llm=llm, prompt=prompt)

                # Use the LLM to generate JSON
                result = generate_json_response(ocr_text, chain)
                
                # Sanitize and parse the result to JSON
                sanitized_json = sanitize_json_response(result)

                if sanitized_json:
                    st.json(sanitized_json)
                else:
                    st.error("Failed to generate valid JSON.")

        # Cleanup: remove the temporary file after use
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == '__main__':
    main()