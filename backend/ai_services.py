import os
import re
import logging
import time
from functools import lru_cache

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if torch is available
TORCH_AVAILABLE = False
try:
    import torch
    TORCH_AVAILABLE = True
    logger.info("✅ PyTorch is available")
except ImportError:
    logger.warning("⚠️ PyTorch not available - using fallback mode")

# Optimize for Render free tier
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'

class AIService:
    def __init__(self):
        self.sentiment_analyzer = None
        self.use_huggingface = False
        self.model_load_time = None
        self.setup_ai_models()
    
    def setup_ai_models(self):
        """Try to setup AI models with Render optimizations"""
        start_time = time.time()
        
        try:
            logger.info("🔄 Attempting to load Hugging Face model...")
            
            # Check if we're in production (Render)
            is_render = os.environ.get('RENDER', False)
            
            from transformers import pipeline
            
            if is_render:
                logger.info("🚀 Render environment - using lightweight model")
                # Use a much smaller, faster model for Render
                model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            else:
                # Use your preferred model for local development
                model_name = "distilbert-base-uncased-finetuned-sst-2-english"
            
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=-1,  # CPU only
                max_length=512,
                truncation=True
            )
            
            self.use_huggingface = True
            self.model_load_time = time.time() - start_time
            logger.info(f"✅ Hugging Face model loaded successfully in {self.model_load_time:.2f}s")
            
        except ImportError as e:
            logger.warning(f"❌ Transformers not available: {e}")
            self.fallback_setup()
        except Exception as e:
            logger.warning(f"❌ Hugging Face loading failed: {e}")
            self.fallback_setup()
    
    def fallback_setup(self):
        """Setup fallback analysis system"""
        logger.info("🔄 Using enhanced keyword analysis instead")
        self.sentiment_analyzer = None
        self.use_huggingface = False
    
    def analyze_sentiment_ai(self, text):
        """
        Analyze sentiment using available methods
        Returns: (sentiment, emotion, confidence)
        """
        if not text or len(text.strip()) < 2:
            return 'neutral', 'neutral', 50
            
        # Use transformers if available, otherwise fallback
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
            
            # Limit text length for performance
            processed_text = clean_text[:512]
            
            results = self.sentiment_analyzer(processed_text)
            best_result = results[0]
            
            # Map transformer output to our sentiment system
            sentiment = 'positive' if best_result['label'] in ['POSITIVE', 'LABEL_2'] else 'negative'
            if best_result['label'] in ['NEUTRAL', 'LABEL_1']:
                sentiment = 'neutral'
                
            confidence = round(best_result['score'] * 100)
            
            # Enhanced emotion detection based on text content
            emotion = self.detect_emotion(text, sentiment, confidence)
            
            logger.debug(f"🤖 AI Analysis: {sentiment} ({confidence}%) - {emotion}")
            return sentiment, emotion, confidence
            
        except Exception as e:
            logger.warning(f"Transformers analysis failed: {e}")
            # Fallback to enhanced analysis
            return self.analyze_sentiment_enhanced(text)
    
    def analyze_sentiment_enhanced(self, text):
        """Enhanced keyword-based sentiment analysis with confidence scoring"""
        if not text:
            return 'neutral', 'neutral', 50
            
        text_lower = text.lower()
        
        # Enhanced sentiment dictionaries with weights and context
        positive_words = {
            'love': 3, 'amazing': 3, 'great': 2, 'excellent': 3, 'awesome': 2,
            'best': 2, 'perfect': 3, 'outstanding': 3, 'good': 1, 'nice': 1,
            'happy': 2, 'fantastic': 2, 'brilliant': 2, 'superb': 2, 'wonderful': 2,
            'recommend': 2, 'impressed': 2, 'pleased': 1, 'satisfied': 1, 'excited': 2,
            'stellar': 3, 'phenomenal': 3, 'exceptional': 3, 'outstanding': 3,
            'beautiful': 2, 'smooth': 1, 'fast': 1, 'reliable': 2, 'innovative': 2
        }
        
        negative_words = {
            'hate': 3, 'terrible': 3, 'awful': 3, 'worst': 3, 'disappointed': 2,
            'bad': 1, 'poor': 2, 'horrible': 3, 'angry': 2, 'frustrating': 2,
            'waste': 2, 'useless': 2, 'broken': 2, 'failed': 2, 'rubbish': 2,
            'avoid': 2, 'complaint': 2, 'issue': 1, 'problem': 1, 'disgusting': 3,
            'appalling': 3, 'unacceptable': 3, 'dreadful': 3, 'slow': 1, 'buggy': 2,
            'crash': 2, 'freeze': 1, 'expensive': 1, 'overpriced': 2
        }
        
        # Context modifiers
        intensifiers = {'very': 1.5, 'really': 1.3, 'extremely': 1.7, 'absolutely': 1.6}
        negations = {'not': -1, "don't": -1, "doesn't": -1, "isn't": -1, "aren't": -1}
        
        # Calculate weighted scores with context
        words = text_lower.split()
        positive_score = 0
        negative_score = 0
        modifier = 1
        
        for i, word in enumerate(words):
            # Check for intensifiers
            if word in intensifiers:
                modifier = intensifiers[word]
                continue
                
            # Check for negations
            if word in negations:
                modifier = negations[word]
                continue
            
            # Reset modifier after use
            current_modifier = modifier
            modifier = 1
            
            # Score positive words
            if word in positive_words:
                score = positive_words[word] * current_modifier
                positive_score += max(score, 0)  # Ensure positive score
                
            # Score negative words  
            elif word in negative_words:
                score = negative_words[word] * abs(current_modifier)  # Use absolute value for negatives
                negative_score += score
        
        total_score = positive_score + negative_score
        
        if total_score == 0:
            # Advanced neutral detection
            return self.analyze_neutral_sentiment(text_lower)
        
        # Calculate sentiment with enhanced logic
        if negative_score > positive_score:
            sentiment = 'negative'
            emotion = self.detect_emotion(text, sentiment, negative_score)
            confidence = min(95, 50 + (negative_score * 3))
        elif positive_score > negative_score:
            sentiment = 'positive'
            emotion = self.detect_emotion(text, sentiment, positive_score)
            confidence = min(95, 50 + (positive_score * 3))
        else:
            sentiment = 'neutral'
            emotion = 'neutral'
            confidence = 60
            
        logger.debug(f"🔍 Enhanced Analysis: {sentiment} ({confidence}%) - {emotion}")
        return sentiment, emotion, confidence
    
    def analyze_neutral_sentiment(self, text_lower):
        """Analyze neutral or ambiguous sentiment patterns"""
        # Question patterns
        if any(word in text_lower for word in ['?', 'how', 'what', 'when', 'where', 'why']):
            return 'neutral', 'curious', 65
        
        # Uncertain patterns
        if any(phrase in text_lower for phrase in ['not sure', 'thinking about', 'maybe', 'perhaps', 'possibly']):
            return 'neutral', 'uncertain', 60
        
        # Mixed patterns
        if any(phrase in text_lower for phrase in ['not bad', 'could be worse', 'so so', 'average']):
            return 'neutral', 'mixed', 55
        
        # Default neutral
        return 'neutral', 'neutral', 50
    
    def detect_emotion(self, text, sentiment, score):
        """Detect specific emotions based on text content and sentiment"""
        text_lower = text.lower()
        
        if sentiment == 'positive':
            if any(word in text_lower for word in ['excited', 'thrilled', 'amazing', 'wow']):
                return 'excitement'
            elif any(word in text_lower for word in ['love', 'adore', 'beautiful', 'perfect']):
                return 'love'
            elif any(word in text_lower for word in ['happy', 'pleased', 'satisfied']):
                return 'joy'
            else:
                return 'satisfaction'
                
        else:  # negative
            if any(word in text_lower for word in ['angry', 'furious', 'outraged', 'hate']):
                return 'anger'
            elif any(word in text_lower for word in ['frustrated', 'annoyed', 'disappointed']):
                return 'frustration'
            elif any(word in text_lower for word in ['sad', 'upset', 'unhappy', 'depressed']):
                return 'sadness'
            elif any(word in text_lower for word in ['scared', 'worried', 'anxious', 'nervous']):
                return 'fear'
            else:
                return 'disappointment'
    
    def clean_text(self, text):
        """Clean text for analysis with enhanced cleaning"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove special characters but keep basic punctuation for context
        text = re.sub(r'[^\w\s\.\!\?]', ' ', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def is_ai_available(self):
        """Check if AI models are available"""
        return self.use_huggingface
    
    def get_service_status(self):
        """Get detailed service status"""
        return {
            'ai_available': self.use_huggingface,
            'model_loaded': self.sentiment_analyzer is not None,
            'model_load_time': self.model_load_time,
            'service_type': 'huggingface' if self.use_huggingface else 'enhanced_keyword'
        }

# Global AI service instance
ai_service = AIService()