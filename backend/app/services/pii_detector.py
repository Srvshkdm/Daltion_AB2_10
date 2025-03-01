import re
import spacy
from typing import List, Dict, Any, Tuple

class PIIDetector:
    def __init__(self):
        # Load spaCy model for named entity recognition
        self.nlp = spacy.load("en_core_web_sm")
        
        # Define regex patterns for Indian PII
        self.patterns = {
            "Aadhaar": r"[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}",  # Format: XXXX XXXX XXXX
            "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]{1}",  # Format: ABCDE1234F
            "Phone": r"(\+91[\-\s]?)?[0]?(91)?[789]\d{9}",  # Indian phone numbers
            "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "GST": r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}"  # GST format
        }
    
    def detect_pii_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using regex patterns"""
        pii_found = []
        
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                pii_found.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        return pii_found
    
    def detect_pii_with_ner(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using NER"""
        pii_found = []
        doc = self.nlp(text)
        
        # Map spaCy entity types to PII types
        entity_mapping = {
            "PERSON": "Name",
            "GPE": "Location",
            "ORG": "Organization",
            "LOC": "Location",
            "DATE": "Date"
        }
        
        for ent in doc.ents:
            if ent.label_ in entity_mapping:
                pii_found.append({
                    "type": entity_mapping[ent.label_],
                    "value": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
        
        return pii_found
    
    def calculate_risk_score(self, pii_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate risk score based on detected PII"""
        # Define risk weights for different PII types
        risk_weights = {
            "Aadhaar": 10,
            "PAN": 8,
            "Name": 5,
            "Phone": 6,
            "Email": 4,
            "Location": 3,
            "Organization": 2,
            "Date": 1,
            "GST": 7
        }
        
        total_score = 0
        pii_count = len(pii_items)
        
        for pii in pii_items:
            pii_type = pii["type"]
            weight = risk_weights.get(pii_type, 1)
            total_score += weight
        
        # Determine risk level
        if total_score >= 15:
            risk_level = "High"
        elif total_score >= 8:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "risk_level": risk_level,
            "risk_score": total_score,
            "pii_count": pii_count
        }
    
    def detect_pii(self, text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Detect all PII in the given text and calculate risk score"""
        # Detect PII using regex
        regex_pii = self.detect_pii_with_regex(text)
        
        # Detect PII using NER
        ner_pii = self.detect_pii_with_ner(text)
        
        # Combine results
        all_pii = regex_pii + ner_pii
        
        # Calculate risk score
        risk_assessment = self.calculate_risk_score(all_pii)
        
        return all_pii, risk_assessment