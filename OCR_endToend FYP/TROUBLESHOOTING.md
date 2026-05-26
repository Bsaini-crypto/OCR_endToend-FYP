# Troubleshooting Guide

## Docker Issues

### Error: "The system cannot find the file specified" / "dockerDesktopLinuxEngine"

**Problem**: Docker Desktop is not running on Windows.

**Solution**:
1. **Start Docker Desktop**:
   - Open Docker Desktop application on Windows
   - Wait for it to fully start (whale icon in system tray should be steady)
   - You should see "Docker Desktop is running" in the system tray

2. **Verify Docker is running**:
   ```powershell
   docker --version
   docker ps
   ```
   If these commands work, Docker is running.

3. **Try again**:
   ```powershell
   docker-compose up -d
   ```

### Alternative: Run Without Docker (Local Development)

If you prefer to run locally without Docker:

1. **Install Python 3.9+** (if not already installed)

2. **Install system dependencies**:
   - Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
   - Add Tesseract to your PATH

3. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Create .env file** with your credentials

5. **Run the Flask API**:
   ```powershell
   python flask-ocr.py
   ```

6. **Test the API**:
   ```powershell
   curl -X POST http://localhost:5002/process_pdf -F "file=@test.pdf"
   ```

## Common Issues

### Airtable Connection Errors

**Error**: "AIRTABLE_API_KEY environment variable is required"

**Solution**:
- Make sure your `.env` file exists in the project root
- Check that `.env` file contains `AIRTABLE_API_KEY=your_key_here`
- Verify the API key is correct (no extra spaces)

### Local Storage Errors

**Error**: Permission denied when saving records

**Solution**:
- Ensure the `records/` folder exists and is writable
- On Windows, check folder permissions
- Try running as administrator if needed

### Port Already in Use

**Error**: "Address already in use" on port 5002

**Solution**:
- Change the port in `flask-ocr.py` (last line)
- Or stop the service using port 5002:
  ```powershell
   netstat -ano | findstr :5002
   taskkill /PID <PID> /F
   ```

## Testing the Setup

1. **Test Docker**:
   ```powershell
   docker ps
   ```

2. **Test API Health**:
   ```powershell
   curl http://localhost:5002/
   ```

3. **Test PDF Processing**:
   ```powershell
   curl -X POST http://localhost:5002/process_pdf -F "file=@test.pdf"
   ```

## Getting Help

- Check Docker Desktop logs: Docker Desktop → Troubleshoot → View logs
- Check application logs: `docker logs ocr-api`
- Verify environment variables are loaded correctly

