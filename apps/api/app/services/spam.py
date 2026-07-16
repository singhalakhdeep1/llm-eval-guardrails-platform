from typing import Dict
import re

class PatternSpamDetector:
    def __init__(self):
        self.spam_patterns = [
            r'\b(buy now|click here|free money|winner|congratulations)\b',
            r'https?://\S{20,}',  # Excessively long URLs
            r'[A-Z]{5,}',  # Excessive caps
            r'(.{1,}\s){15,}',  # Repetitive patterns
            r'\$\d+,\d+',  # Money patterns
        ]
    
    def detect_patterns(self, content: str) -> Dict:
        """Detect spam using pattern matching"""
        detected = []
        
        for pattern in self.spam_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                detected.append({
                    "pattern": pattern,
                    "matches": len(matches),
                    "severity": "medium"
                })
        
        # Check for excessive links
        links = re.findall(r'https?://\S+', content)
        if len(links) > 5:
            detected.append({
                "pattern": "excessive_links",
                "matches": len(links),
                "severity": "high"
            })
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        if caps_ratio > 0.5:
            detected.append({
                "pattern": "excessive_caps",
                "matches": int(caps_ratio * 100),
                "severity": "medium"
            })
        
        return {
            "pattern_matches": detected,
            "flagged": len(detected) > 0,
            "spam_score": min(len(detected) * 10, 100)
        }


class SpamDetectionService:
    def __init__(self):
        self.pattern_detector = PatternSpamDetector()
        self.user_reputation = {}  # In production, use Redis or database
    
    def detect_spam(self, content: str, user_id: str = None) -> Dict:
        """Detect spam using multiple methods"""
        # Pattern-based detection
        pattern_result = self.pattern_detector.detect_patterns(content)
        
        # User reputation check
        reputation_score = 0
        if user_id:
            reputation_score = self.user_reputation.get(user_id, 50)
        
        # Combined spam score
        pattern_score = pattern_result["spam_score"]
        reputation_penalty = (100 - reputation_score) * 0.3
        final_spam_score = pattern_score + reputation_penalty
        
        return {
            "is_spam": final_spam_score > 50,
            "spam_probability": min(final_spam_score / 100, 1.0),
            "confidence": "high" if final_spam_score > 70 else "medium" if final_spam_score > 50 else "low",
            "pattern_matches": pattern_result["pattern_matches"],
            "reputation_score": reputation_score
        }
    
    def report_spam(self, user_id: str, is_spam: bool):
        """Update user reputation based on spam reports"""
        current_score = self.user_reputation.get(user_id, 50)
        
        if is_spam:
            self.user_reputation[user_id] = max(0, current_score - 10)
        else:
            self.user_reputation[user_id] = min(100, current_score + 5)
    
    def get_user_reputation(self, user_id: str) -> int:
        """Get user reputation score"""
        return self.user_reputation.get(user_id, 50)
