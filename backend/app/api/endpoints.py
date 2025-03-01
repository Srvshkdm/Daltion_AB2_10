\from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, Response
import os
import io
from typing import List, Dict, Any, Optional
import json

from app.services.ocr_service import OCRService
from app.services.pii_detector import PIIDetector
from app.services.redaction_service import RedactionService

router = APIRouter()
ocr_service = OCRService()
pii_detector = PIIDetector()
redaction_service = RedactionService()

@router.get("/test")
def test_endpoint():
    return {"status": "OK"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a file for PII detection
    """
    # Check file extension
    _, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in ['.pdf', '.jpg', '.jpeg', '.png']:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    
    # Read file content
    file_content = await file.read()
    
    # Extract text using OCR
    try:
        extracted_text, word_data = ocr_service.process_file(file_content, file_extension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in OCR processing: {str(e)}")
    
    # Detect PII
    detected_pii, risk_assessment = pii_detector.detect_pii(extracted_text)
    
    # Redact PII in text
    redacted_text = redaction_service.redact_text(extracted_text, detected_pii)
    
    # Prepare response
    response = {
        "filename": file.filename,
        "extracted_text": extracted_text,
        "redacted_text": redacted_text,
        "detected_pii": detected_pii,
        "risk_assessment": risk_assessment
    }
    
    return response

@router.post("/redact-image")
async def redact_image(file: UploadFile = File(...)):
    """
    Upload, detect PII, and return a redacted image
    """
    # Check file extension
    _, file_extension = os.path.splitext(file.filename)
    if file_extension.lower() not in ['.jpg', '.jpeg', '.png']:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    
    # Read file content
    file_content = await file.read()
    
    # Extract text using OCR
    try:
        extracted_text, word_data = ocr_service.extract_text_from_image(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in OCR processing: {str(e)}")
    
    # Detect PII
    detected_pii, risk_assessment = pii_detector.detect_pii(extracted_text)
    
    # Redact image
    redacted_image = redaction_service.redact_image(file_content, word_data, detected_pii)
    
    # Return redacted image
    return Response(content=redacted_image, media_type=f"image/{file_extension[1:]}")