import os
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.sentiment_analyzer = None
        self.use_huggingface = False
        self.setup_ai_models()
    
    def setup_ai_models(self):
        """Try to setup AI models, fallback to enhanced analysis"""
        try:
            logger.info("🔄 Attempting to load Hugging Face model...")
            # Try a smaller, faster model first
            from transformers import pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",  # Smaller model
                device=-1  # Use CPU only (faster loading)
            )
            self.use_huggingface = True
            logger.info("✅ Hugging Face model loaded successfully")
        except Exception as e:
            logger.warning(f"❌ Hugging Face loading failed: {e}")
            logger.info("🔄 Using enhanced keyword analysis instead")
            self.sentiment_analyzer = None
            self.use_huggingface = False
    
    def analyze_sentiment_ai(self, text):
        """
        Analyze sentiment using available methods
        Returns: (sentiment, emotion, confidence)
        """
        if self.use_huggingface and self.sentiment_analyzer:
            return self.analyze_with_transformers(text)
        else:
            return self.analyze_sentiment_enhanced(text)
    
    def analyze_with_transformers(self, text):
        """Use Hugging Face transformers for sentiment analysis"""
        try:
            clean_text = self.clean_text(text)
            if len(clean_text) < 3:
                return 'neutral', 'neutral', 50
            
            results = self.sentiment_analyzer(clean_text[:512])
            best_result = results[0]
            
            sentiment = 'positive' if best_result['label'] == 'POSITIVE' else 'negative'
            confidence = round(best_result['score'] * 100)
            
            emotion = 'joy' if sentiment == 'positive' else 'frustration'
            return sentiment, emotion, confidence
            
        except Exception as e:
            logger.warning(f"Transformers analysis failed: {e}")
            return self.analyze_sentiment_enhanced(text)
    
    def analyze_sentiment_enhanced(self, text):
        """Enhanced keyword-based sentiment analysis with confidence scoring"""
        if not text:
            return 'neutral', 'neutral', 50
            
        text_lower = text.lower()
        
        # Comprehensive sentiment dictionaries with weights
        positive_words = {
            'love': 3, 'amazing': 3, 'great': 2, 'excellent': 3, 'awesome': 2,
            'best': 2, 'perfect': 3, 'outstanding': 3, 'good': 1, 'nice': 1,
            'happy': 2, 'fantastic': 2, 'brilliant': 2, 'superb': 2, 'wonderful': 2,
            'recommend': 2, 'impressed': 2, 'pleased': 1, 'satisfied': 1, 'excited': 2,
            'outstanding': 3, 'stellar': 3, 'phenomenal': 3, 'exceptional': 3
        }
        
        negative_words = {
            'hate': 3, 'terrible': 3, 'awful': 3, 'worst': 3, 'disappointed': 2,
            'bad': 1, 'poor': 2, 'horrible': 3, 'angry': 2, 'frustrating': 2,
            'waste': 2, 'useless': 2, 'broken': 2, 'failed': 2, 'rubbish': 2,
            'avoid': 2, 'complaint': 2, 'issue': 1, 'problem': 1, 'terrible': 3,
            'disgusting': 3, 'appalling': 3, 'unacceptable': 3, 'dreadful': 3
        }
        
        urgent_words = ['urgent', 'immediately', 'asap', 'emergency', 'critical', 'important']
        
        # Calculate weighted scores
        positive_score = sum(positive_words.get(word, 0) for word in text_lower.split() if word in positive_words)
        negative_score = sum(negative_words.get(word, 0) for word in text_lower.split() if word in negative_words)
        urgent_score = sum(1 for word in urgent_words if word in text_lower)
        
        total_score = positive_score + negative_score
        
        if total_score == 0:
            # Analyze sentence structure for neutral/positive/negative patterns
            if any(word in text_lower for word in ['not bad', 'not great', 'okay', 'average', 'decent']):
                return 'neutral', 'neutral', 60
            elif any(word in text_lower for word in ['?', 'not sure', 'thinking about']):
                return 'neutral', 'curious', 55
            else:
                return 'neutral', 'neutral', 50
        
        if negative_score > positive_score:
            sentiment = 'negative'
            emotion = 'anger' if urgent_score > 0 else 'frustration'
            confidence = min(95, 60 + (negative_score * 5))
        elif positive_score > negative_score:
            sentiment = 'positive'
            emotion = 'excitement' if urgent_score > 0 else 'joy'
            confidence = min(95, 60 + (positive_score * 5))
        else:
            sentiment = 'neutral'
            emotion = 'neutral'
            confidence = 50
            
        return sentiment, emotion, confidence
    
    def clean_text(self, text):
        """Clean text for analysis"""
        if not text:
            return ""
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text.strip()
    
    def is_ai_available(self):
        """Check if AI models are available"""
        return self.use_huggingface

# Global AI service instance
ai_service = AIService()