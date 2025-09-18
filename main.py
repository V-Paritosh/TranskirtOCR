from fastapi import FastAPI, UploadFile, File, Form
import cv2
import numpy as np
import pytesseract
import os
from skimage.filters import threshold_local
import imutils

app = FastAPI()

@app.get("/")
def root():
    return {"message": "OCR Service with crop support is running"}

@app.post("/scan-ocr/")
async def scan_and_ocr(
    file: UploadFile = File(...),
    x: int = Form(...),
    y: int = Form(...),
    w: int = Form(...),
    h: int = Form(...),
    lang: str = Form("guj")
):
    """
    file → uploaded image
    x, y, w, h → crop rectangle coordinates (provided by frontend)
    lang → OCR language (default Gujarati)
    """

    # Read uploaded file
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Step 1: Crop based on coordinates from frontend
    cropped = image[y:y+h, x:x+w]

    # Step 2: Convert to grayscale + threshold
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    T = threshold_local(gray, 11, offset=10, method="gaussian")
    processed = (gray > T).astype("uint8") * 255

    # Step 3: Save for debugging (optional)
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "cropped_result.png")
    cv2.imwrite(output_path, processed)

    # Step 4: OCR
    text = pytesseract.image_to_string(processed, lang=lang)

    return {
        "extracted_text": text,
        "saved_image": output_path
    }
