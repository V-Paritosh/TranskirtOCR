FROM python:3.11-slim

# Install system packages and Tesseract with extra language packs
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-san \
    tesseract-ocr-guj \
    tesseract-ocr-hin \
    && rm -rf /var/lib/apt/lists/*

# Set tessdata path (important for non-English)
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app
WORKDIR /app

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
