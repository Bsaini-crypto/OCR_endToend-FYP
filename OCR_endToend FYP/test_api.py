"""
Test script for OCR API
Tests the /process_pdf endpoint with a sample PDF file
"""
import requests
import json
import os
import sys
from pathlib import Path

# API Configuration
API_URL = "http://localhost:5002"
ENDPOINT = f"{API_URL}/process_pdf"
HEALTH_ENDPOINT = f"{API_URL}/"

def test_health_check():
    """Test if the API is running."""
    print("=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API is running!")
            print(f"Status: {data.get('status')}")
            print(f"Local Storage: {'Enabled' if data.get('storage', {}).get('local') else 'Disabled'}")
            print(f"Airtable: {'Enabled' if data.get('storage', {}).get('airtable') else 'Disabled'}")
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running on http://localhost:5002?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pdf_processing(pdf_path):
    """Test PDF processing endpoint."""
    print("\n" + "=" * 60)
    print("Testing PDF Processing")
    print("=" * 60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    print(f"📄 Processing PDF: {pdf_path}")
    print(f"📡 Sending request to: {ENDPOINT}")
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {'file': (os.path.basename(pdf_path), pdf_file, 'application/pdf')}
            
            print("\n⏳ Processing... (this may take a minute)")
            response = requests.post(ENDPOINT, files=files, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ PDF processed successfully!")
            print("\n" + "-" * 60)
            print("EXTRACTED DATA:")
            print("-" * 60)
            print(json.dumps(data.get('data', {}), indent=2))
            
            print("\n" + "-" * 60)
            print("STORAGE STATUS:")
            print("-" * 60)
            storage = data.get('storage', {})
            
            # Local storage status
            local = storage.get('local', {})
            if local.get('enabled', True):
                if local.get('saved'):
                    print(f"✅ Local: Saved to {local.get('file_path')}")
                else:
                    print("❌ Local: Failed to save")
            else:
                print("⚠️  Local: Disabled")
            
            # Airtable status
            airtable = storage.get('airtable', {})
            if airtable.get('enabled', True):
                if airtable.get('inserted'):
                    print(f"✅ Airtable: Record inserted (ID: {airtable.get('record_id')})")
                else:
                    print("❌ Airtable: Failed to insert")
            else:
                print("⚠️  Airtable: Disabled")
            
            # Save full response to file
            output_file = "test_response.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Full response saved to: {output_file}")
            
            return True
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_path}")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The PDF might be too large or the API is slow.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("OCR API Test Script")
    print("=" * 60)
    print()
    
    # Test health check first
    if not test_health_check():
        print("\n❌ API is not running. Please start the API first.")
        print("   Run: docker-compose up -d")
        print("   Or:  python flask-ocr.py")
        sys.exit(1)
    
    # Get PDF file path
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Look for common PDF files in current directory
        pdf_files = list(Path('.').glob('*.pdf'))
        if pdf_files:
            pdf_path = str(pdf_files[0])
            print(f"\n📄 Found PDF file: {pdf_path}")
            print("   (You can also specify a file: python test_api.py <path_to_pdf>)")
        else:
            print("\n❌ No PDF file found in current directory.")
            print("   Usage: python test_api.py <path_to_pdf_file>")
            print("\n   Example:")
            print("   python test_api.py sample.pdf")
            print("   python test_api.py C:\\Users\\YourName\\Documents\\invoice.pdf")
            sys.exit(1)
    
    # Test PDF processing
    success = test_pdf_processing(pdf_path)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests completed successfully!")
    else:
        print("❌ Tests failed. Check the errors above.")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()

