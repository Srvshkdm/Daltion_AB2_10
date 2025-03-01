import cv2
import numpy as np
from PIL import Image
import io
from typing import List, Dict, Any, Tuple

class RedactionService:
    def __init__(self):
        pass
    
    def redact_text(self, text: str, pii_items: List[Dict[str, Any]]) -> str:
        """Redact PII in text by replacing with asterisks"""
        # Sort PII items by start position in descending order to avoid changing positions
        sorted_pii = sorted(pii_items, key=lambda x: x["start"], reverse=True)
        
        # Replace each PII with asterisks
        redacted_text = text
        for pii in sorted_pii:
            start = pii["start"]
            end = pii["end"]
            value = pii["value"]
            redacted_value = '*' * len(value)
            redacted_text = redacted_text[:start] + redacted_value + redacted_text[end:]
        
        return redacted_text
    
    def redact_image(self, image_bytes: bytes, word_data: Dict[str, Any], pii_items: List[Dict[str, Any]]) -> bytes:
        """Redact PII in image by blurring the regions"""
        if not word_data or not pii_items:
            return image_bytes
        
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        # Get bounding boxes for words
        words = word_data["text"]
        word_boxes = []
        
        for i in range(len(words)):
            if int(word_data["conf"][i]) > 0:  # Only consider words with confidence > 0
                x, y, w, h = (
                    word_data["left"][i],
                    word_data["top"][i],
                    word_data["width"][i],
                    word_data["height"][i]
                )
                word_boxes.append((words[i], (x, y, w, h)))
        
        # For each PII item, find the corresponding words in the image and blur them
        for pii in pii_items:
            pii_value = pii["value"]
            
            # Find words that match the PII
            for word, (x, y, w, h) in word_boxes:
                if word in pii_value:
                    # Apply blur to this region
                    roi = image_np[y:y+h, x:x+w]
                    if roi.size > 0:  # Check if ROI is not empty
                        blurred_roi = cv2.GaussianBlur(roi, (25, 25), 0)
                        image_np[y:y+h, x:x+w] = blurred_roi
        
        # Convert back to bytes
        result_image = Image.fromarray(image_np)
        img_byte_arr = io.BytesIO()
        result_image.save(img_byte_arr, format=image.format)
        
        return img_byte_arr.getvalue()