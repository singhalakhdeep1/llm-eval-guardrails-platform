from typing import Dict, List
from openai import OpenAI

class ModerationService:
    def __init__(self):
        self.client = OpenAI()
    
    async def moderate_content(self, content: str) -> Dict[str, any]:
        """Moderate content using OpenAI Moderation API"""
        moderation = self.client.moderations.create(input=content)
        
        result = moderation.results[0]
        
        return {
            "flagged": result.flagged,
            "categories": {
                "hate": result.categories.hate,
                "hate_threatening": result.categories.hate_threatening,
                "self_harm": result.categories.self_harm,
                "sexual": result.categories.sexual,
                "violence": result.categories.violence,
                "violence_graphic": result.categories.violence_graphic,
            },
            "category_scores": {
                "hate": result.category_scores.hate,
                "hate_threatening": result.category_scores.hate_threatening,
                "self_harm": result.category_scores.self_harm,
                "sexual": result.category_scores.sexual,
                "violence": result.category_scores.violence,
                "violence_graphic": result.category_scores.violence_graphic,
            }
        }
    
    def detect_pii(self, content: str) -> List[Dict]:
        """Detect PII using spaCy"""
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(content)
            
            pii_entities = []
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "EMAIL", "PHONE", "GPE", "ORG"]:
                    pii_entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    })
            
            return pii_entities
        except Exception:
            return []
    
    def redact_pii(self, content: str) -> str:
        """Redact PII from content"""
        pii_entities = self.detect_pii(content)
        
        redacted = content
        offset = 0
        
        for entity in sorted(pii_entities, key=lambda x: x['start']):
            start = entity['start'] + offset
            end = entity['end'] + offset
            redacted = redacted[:start] + "[REDACTED]" + redacted[end:]
            offset += len("[REDACTED]") - (end - start)
        
        return redacted


class CustomModerationService:
    def __init__(self):
        self.blocked_words = self.load_blocked_words()
        self.whitelisted_domains = self.load_whitelist()
    
    def load_blocked_words(self) -> List[str]:
        """Load blocked words list"""
        return ["spam", "scam", "phishing"]
    
    def load_whitelist(self) -> List[str]:
        """Load whitelisted domains"""
        return ["example.com", "trusted.org"]
    
    def check_custom_rules(self, content: str) -> Dict:
        """Check custom moderation rules"""
        violations = []
        
        # Check blocked words
        for word in self.blocked_words:
            if word.lower() in content.lower():
                violations.append({
                    "type": "blocked_word",
                    "word": word,
                    "severity": "high"
                })
        
        # Check for suspicious links
        import re
        links = re.findall(r'https?://\S+', content)
        for link in links:
            domain = self.extract_domain(link)
            if domain not in self.whitelisted_domains:
                violations.append({
                    "type": "suspicious_link",
                    "link": link,
                    "severity": "medium"
                })
        
        return {
            "violations": violations,
            "flagged": len(violations) > 0
        }
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        import re
        match = re.search(r'https?://([^/]+)', url)
        return match.group(1) if match else url
