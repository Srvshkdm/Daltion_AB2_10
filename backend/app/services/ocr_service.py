import pytesseract
import pdfplumber
import cv2
import numpy as np
from PIL import Image
import io
import os
from typing import Tuple, Dict, List, Any

class OCRService:
    def __init__(self):
        # Configure pytesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # For Windows
        pass
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image to improve OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get black and white image
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Noise removal
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return opening
    
    def extract_text_from_image(self, image_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
        """Extract text from image bytes"""
        # Convert bytes to image
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        # Preprocess
        if len(image_np.shape) == 3:  # Color image
            processed_image = self.preprocess_image(image_np)
        else:  # Already grayscale
            processed_image = image_np
        
        # Extract text with pytesseract
        extracted_text = pytesseract.image_to_string(processed_image)
        
        # Get positions of words for redaction purposes
        word_data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
        
        return extracted_text, word_data
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        with io.BytesIO(pdf_bytes) as pdf_file:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
        return text
    
    def process_file(self, file_content: bytes, file_extension: str) -> Tuple[str, Dict[str, Any]]:
        """Process file based on its extension"""
        if file_extension.lower() in ['.pdf']:
            text = self.extract_text_from_pdf(file_content)
            return text, {}  # No word data for PDFs through pdfplumber
        elif file_extension.lower() in ['.jpg', '.jpeg', '.png']:
            return self.extract_text_from_image(file_content)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")