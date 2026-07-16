from typing import Dict

class SentimentService:
    def __init__(self):
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader = SentimentIntensityAnalyzer()
        except Exception:
            self.vader = None
    
    def analyze_sentiment(self, content: str) -> Dict:
        """Analyze sentiment using VADER"""
        if not self.vader:
            return self._fallback_sentiment(content)
        
        vader_scores = self.vader.polarity_scores(content)
        
        # Determine overall sentiment
        if vader_scores['compound'] >= 0.05:
            sentiment = "positive"
        elif vader_scores['compound'] <= -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "compound_score": vader_scores['compound'],
            "positive_score": vader_scores['pos'],
            "negative_score": vader_scores['neg'],
            "neutral_score": vader_scores['neu'],
            "intensity": "high" if abs(vader_scores['compound']) > 0.5 else "medium" if abs(vader_scores['compound']) > 0.2 else "low"
        }
    
    def _fallback_sentiment(self, content: str) -> Dict:
        """Fallback sentiment analysis using keyword matching"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy", "love", "best"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "sad", "angry", "poor"]
        
        words = content.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
            compound = (positive_count - negative_count) / max(len(words), 1)
        elif negative_count > positive_count:
            sentiment = "negative"
            compound = (negative_count - positive_count) / max(len(words), 1) * -1
        else:
            sentiment = "neutral"
            compound = 0
        
        return {
            "sentiment": sentiment,
            "compound_score": compound,
            "positive_score": positive_count / max(len(words), 1),
            "negative_score": negative_count / max(len(words), 1),
            "neutral_score": 1 - (positive_count + negative_count) / max(len(words), 1),
            "intensity": "low"
        }


class EmotionDetectionService:
    def __init__(self):
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
        except Exception:
            self.classifier = None
    
    async def detect_emotions(self, content: str) -> Dict:
        """Detect emotions using transformers"""
        if not self.classifier:
            return self._fallback_emotion(content)
        
        results = self.classifier(content)[0]
        
        emotions = {
            result['label']: result['score']
            for result in results
        }
        
        # Get dominant emotion
        dominant = max(emotions, key=emotions.get)
        
        return {
            "dominant_emotion": dominant,
            "emotions": emotions,
            "confidence": emotions[dominant]
        }
    
    def _fallback_emotion(self, content: str) -> Dict:
        """Fallback emotion detection using keyword matching"""
        emotion_keywords = {
            "joy": ["happy", "excited", "great", "wonderful", "amazing"],
            "anger": ["angry", "furious", "mad", "annoyed", "frustrated"],
            "sadness": ["sad", "depressed", "unhappy", "down", "miserable"],
            "fear": ["scared", "afraid", "terrified", "anxious", "worried"],
            "surprise": ["surprised", "shocked", "amazed", "astonished"],
            "neutral": []
        }
        
        words = content.lower().split()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for word in words if word in keywords)
            emotion_scores[emotion] = score / max(len(words), 1)
        
        dominant = max(emotion_scores, key=emotion_scores.get)
        
        return {
            "dominant_emotion": dominant,
            "emotions": emotion_scores,
            "confidence": emotion_scores[dominant]
        }
