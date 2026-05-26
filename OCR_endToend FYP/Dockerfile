# Use Python slim-bullseye for better security and smaller size
FROM python:3.9-slim-bullseye

# Build arguments
ARG TESSERACT_LANG=eng
ARG USER_NAME=appuser
ARG USER_UID=1000
ARG USER_GID=1000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Set correct Tesseract data path
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata \
    DEBIAN_FRONTEND=noninteractive

# Create non-root user
RUN groupadd -g ${USER_GID} ${USER_NAME} && \
    useradd -m -u ${USER_UID} -g ${USER_GID} -s /bin/bash ${USER_NAME}

# Install system dependencies and cleanup in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libtesseract-dev \
        poppler-utils \
        wget \
        curl && \
    # Create Tesseract data directory
    mkdir -p /usr/share/tesseract-ocr/4.00/tessdata && \
    # Download English language data directly from GitHub
    wget -O /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata \
        https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata && \
    # Clean up
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Verify Tesseract installation and language data
RUN tesseract --version && \
    tesseract --list-langs && \
    ls -la /usr/share/tesseract-ocr/4.00/tessdata/

# Set working directory and change ownership
WORKDIR /app
RUN chown ${USER_NAME}:${USER_NAME} /app

# Copy requirements first for better caching
COPY --chown=${USER_NAME}:${USER_NAME} requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=${USER_NAME}:${USER_NAME} . .

# Create directories for temporary files and records
RUN mkdir -p /app/temp /app/records && \
    chown ${USER_NAME}:${USER_NAME} /app/temp /app/records

# Switch to non-root user
USER ${USER_NAME}

# Expose ports (Flask default: 5002, Streamlit default: 8501)
EXPOSE 5002 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    TEMP_DIR=/app/temp \
    FLASK_APP=flask-ocr.py \
    FLASK_ENV=production

# Healthcheck for Flask API
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/ || exit 1

# Default command: Run Flask API
# To run Streamlit instead, override with: streamlit run ocr.py --server.address=0.0.0.0 --server.port=8501
CMD ["python", "flask-ocr.py"]