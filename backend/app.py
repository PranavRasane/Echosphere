from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime, timedelta
import logging
import os
import time
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enhanced CORS configuration
CORS(app, 
     origins=[
         "http://localhost:3000", 
         "https://echosphere.netlify.app",
         "https://your-frontend.netlify.app"
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

print("🚀 Echosphere Backend Starting...")

# Safe AI Service Import with Fallback
try:
    from ai_services import ai_service
    print(f"✅ AI Service Available: {ai_service.is_ai_available()}")
except ImportError as e:
    print(f"⚠️ AI Service not available: {e}")
    # Create fallback AI service
    class FallbackAIService:
        def __init__(self):
            self.ai_available = False
        
        def is_ai_available(self):
            return False
        
        def get_service_status(self):
            return {"status": "fallback", "ai_available": False}
        
        def analyze_sentiment_ai(self, text):
            """Fallback sentiment analysis"""
            if not text:
                return 'neutral', 'neutral', 50
                
            text_lower = text.lower()
            positive_words = ['love', 'great', 'amazing', 'good', 'best', 'awesome']
            negative_words = ['hate', 'terrible', 'awful', 'bad', 'worst', 'horrible']
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return 'positive', 'happy', min(90, 50 + (positive_count * 10))
            elif negative_count > positive_count:
                return 'negative', 'sad', min(90, 50 + (negative_count * 10))
            else:
                return 'neutral', 'neutral', 50
    
    ai_service = FallbackAIService()

# Rate limiting storage (in production, use Redis)
request_times = {}

def rate_limit(max_requests=100, window_seconds=60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Handle OPTIONS preflight
            if request.method == 'OPTIONS':
                return jsonify({'status': 'ok'}), 200
                
            client_ip = request.remote_addr
            now = time.time()
            
            # Initialize or clean old entries for this IP
            if client_ip not in request_times:
                request_times[client_ip] = []
            
            # Remove requests outside the current window
            request_times[client_ip] = [req_time for req_time in request_times[client_ip] 
                                      if now - req_time < window_seconds]
            
            # Check if over limit
            if len(request_times[client_ip]) >= max_requests:
                return jsonify({
                    "error": "Rate limit exceeded", 
                    "message": f"Maximum {max_requests} requests per {window_seconds} seconds"
                }), 429
            
            # Add current request
            request_times[client_ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class BrandAIAnalyzer:
    def __init__(self):
        self.brand_categories = {
            'sports': ['nike', 'adidas', 'puma', 'reebok', 'under armour'],
            'tech': ['apple', 'samsung', 'google', 'microsoft', 'xiaomi'],
            'retail': ['amazon', 'flipkart', 'myntra', 'ajio', 'nykaa'],
            'beverage': ['starbucks', 'coca', 'pepsi', 'redbull', 'monster'],
            'automotive': ['tesla', 'toyota', 'ford', 'honda', 'bmw'],
            'fashion': ['zara', 'hm', 'forever21', 'uniqlo', 'levis'],
            'food': ['mcdonalds', 'kfc', 'subway', 'dominos', 'pizzahut'],
            'finance': ['paypal', 'stripe', 'visa', 'mastercard', 'american express']
        }
    
    def predict_competitors(self, brand_name):
        """AI-powered competitor prediction based on brand categories"""
        brand_lower = brand_name.lower()
        
        for category, brands in self.brand_categories.items():
            if brand_lower in brands:
                # Return other brands from same category
                return [b for b in brands if b != brand_lower][:4]
        
        # Enhanced AI fallback - generate relevant competitors based on brand name patterns
        brand_patterns = {
            'wear|fashion|clothing|apparel': ['Zara', 'H&M', 'Forever 21', 'Uniqlo'],
            'tech|electronic|phone|mobile|computer': ['Samsung', 'Google', 'OnePlus', 'Xiaomi'],
            'car|auto|vehicle|motor': ['Toyota', 'Ford', 'Honda', 'BMW'],
            'food|restaurant|burger|pizza': ['McDonalds', 'KFC', 'Subway', 'Dominos'],
            'bank|finance|payment|money': ['PayPal', 'Stripe', 'Visa', 'Mastercard'],
            'social|media|network': ['Facebook', 'Instagram', 'Twitter', 'TikTok'],
            'stream|video|music|entertainment': ['Netflix', 'YouTube', 'Spotify', 'Disney+']
        }
        
        for pattern, competitors in brand_patterns.items():
            if any(word in brand_lower for word in pattern.split('|')):
                return competitors
        
        return ['Market Leader', 'Emerging Brand', 'Local Competitor', 'Industry Disruptor']
    
    def calculate_ai_risk(self, mentions):
        """Advanced AI risk calculation with real sentiment analysis"""
        if not mentions:
            return 0, 'low', '🟢'
        
        negative_count = len([m for m in mentions if m['sentiment'] == 'negative'])
        anger_count = len([m for m in mentions if m['emotion'] in ['anger', 'frustration']])
        total_mentions = len(mentions)
        
        # Enhanced risk algorithm considering multiple factors
        negative_mentions = [m for m in mentions if m['sentiment'] == 'negative']
        
        if negative_mentions:
            total_confidence = sum(m.get('confidence', 50) for m in negative_mentions)
            avg_confidence = total_confidence / len(negative_mentions)
            # High confidence negative mentions are more concerning
            risk_multiplier = 1 + (avg_confidence / 100)
        else:
            avg_confidence = 0
            risk_multiplier = 1
        
        # Calculate risk score with multiple factors
        base_risk = (negative_count * 8) + (anger_count * 12)
        confidence_risk = avg_confidence * 0.3
        volume_risk = min(20, total_mentions * 0.1)  # Small penalty for high volume
        
        risk_score = min(100, (base_risk + confidence_risk + volume_risk) * risk_multiplier)
        
        # Enhanced pattern detection
        if risk_score > 70:
            return round(risk_score), 'high', '🔴'
        elif risk_score > 40:
            return round(risk_score), 'medium', '🟡'
        else:
            return round(risk_score), 'low', '🟢'

    def get_industry_actions(self, industry):
        """Get industry-specific recommended actions"""
        actions = {
            "technology": [
                "Monitor software update feedback closely",
                "Engage with developer community",
                "Track competitor feature releases",
                "Address security concern mentions promptly"
            ],
            "fashion": [
                "Monitor seasonal collection feedback",
                "Track influencer collaborations",
                "Address sizing and quality concerns",
                "Highlight sustainable initiatives"
            ],
            "food": [
                "Monitor food quality mentions",
                "Track location-specific feedback",
                "Address service speed concerns",
                "Highlight new menu items"
            ],
            "automotive": [
                "Monitor safety feature discussions",
                "Track reliability mentions",
                "Address customer service experiences",
                "Highlight innovation in sustainability"
            ],
            "general": [
                "Engage with negative feedback on social media",
                "Highlight positive customer stories",
                "Monitor competitor pricing strategies",
                "Improve response time to customer queries"
            ]
        }
        return actions.get(industry, actions["general"])

    def get_industry_opportunities(self, industry):
        """Get industry-specific opportunity areas"""
        opportunities = {
            "technology": [
                "User experience improvements",
                "Feature request analysis",
                "Integration opportunities",
                "Performance optimization"
            ],
            "fashion": [
                "Product quality mentions",
                "Style trend identification",
                "Sustainability initiatives",
                "Size inclusivity"
            ],
            "food": [
                "Menu innovation opportunities",
                "Service quality improvements",
                "Location expansion potential",
                "Dietary preference accommodation"
            ],
            "automotive": [
                "Safety feature development",
                "Fuel efficiency improvements",
                "Technology integration",
                "Customer service enhancement"
            ],
            "general": [
                "Product quality mentions",
                "Customer service experience",
                "Pricing competitiveness",
                "Brand perception"
            ]
        }
        return opportunities.get(industry, opportunities["general"])

# Initialize AI analyzer
brand_analyzer = BrandAIAnalyzer()

def generate_ai_mentions(brand_name, count=20):
    """Generate mentions with sentiment analysis"""
    platforms = ['Twitter', 'Reddit', 'Instagram', 'News', 'Forum', 'Blog', 'YouTube', 'TikTok']
    
    mention_templates = [
        f"Just tried {{brand}}'s new product {{context}}",
        f"{{brand}} customer service was {{context}} today",
        f"Thinking about switching from {{brand}} to a competitor {{context}}",
        f"{{brand}}'s latest campaign is getting {{context}} reactions",
        f"Had a {{context}} experience with {{brand}} support",
        f"{{brand}} is trending for {{context}} reasons today",
        f"Compared {{brand}} with competitors - {{context}}",
        f"{{brand}} needs to improve their {{context}}",
        f"Love the new {{brand}} collection! {{context}}",
        f"Disappointed with {{brand}}'s quality {{context}}",
        f"{{brand}} just announced {{context}}",
        f"Can't believe what {{brand}} did {{context}}",
        f"{{brand}} is changing the game {{context}}",
        f"Not impressed with {{brand}}'s new feature {{context}}"
    ]
    
    contexts = [
        "and it's amazing!", "very disappointing", "mixed feelings", 
        "highly recommended", "would not recommend", "better than expected",
        "worse than I thought", "exceeded expectations", "failed to deliver",
        "absolutely love it!", "needs improvement", "surprisingly good",
        "not worth the price", "game changing innovation"
    ]
    
    mentions = []
    for i in range(count):
        template = random.choice(mention_templates)
        context = random.choice(contexts)
        
        mention_text = template.format(brand=brand_name, context=context)
        
        # Use AI service for sentiment analysis
        sentiment, emotion, confidence = ai_service.analyze_sentiment_ai(mention_text)
        
        # Generate more realistic timestamps
        hours_ago = random.randint(0, 72)  # Up to 3 days
        minutes_ago = random.randint(0, 59)
        
        mention = {
            'id': i + 1,
            'text': mention_text,
            'platform': random.choice(platforms),
            'sentiment': sentiment,
            'emotion': emotion,
            'confidence': confidence,
            'ai_analyzed': ai_service.is_ai_available(),
            'timestamp': (datetime.now() - timedelta(hours=hours_ago, minutes=minutes_ago)).isoformat(),
            'username': f"user_{random.randint(1000, 9999)}",
            'engagement': random.randint(5, 5000),
            'verified': random.choice([True, False, False, False]),
            'impact_score': round(random.uniform(0.1, 1.0), 2)
        }
        mentions.append(mention)
    
    # Sort by timestamp (newest first)
    mentions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return mentions

# API Routes
@app.route('/')
def home():
    return jsonify({
        "message": "Echosphere AI Backend Server",
        "status": "running", 
        "version": "2.0.0",
        "endpoints": {
            "health": "/api/health",
            "analyze": "/api/analyze",
            "competitors": "/api/competitors",
            "ai_insights": "/api/ai-insights"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    ai_status = ai_service.get_service_status()
    return jsonify({
        "status": "Echosphere AI API is running!",
        "ai_available": ai_service.is_ai_available(),
        "ai_service_status": ai_status,
        "timestamp": datetime.now().isoformat(),
        "environment": os.environ.get('FLASK_ENV', 'development'),
        "version": "2.0.0"
    })

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
@rate_limit(max_requests=50, window_seconds=60)
def analyze_brand():
    start_time = time.time()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        brand_name = data.get('brand', '').strip()
        
        if not brand_name:
            return jsonify({"error": "Brand name is required"}), 400
        
        if len(brand_name) > 100:
            return jsonify({"error": "Brand name too long"}), 400
        
        logger.info(f"🧠 Analyzing brand: {brand_name}")
        
        # Generate mentions with sentiment analysis
        mentions = generate_ai_mentions(brand_name)
        
        # Calculate metrics with sentiment data
        total_mentions = len(mentions)
        positive_mentions = len([m for m in mentions if m['sentiment'] == 'positive'])
        negative_mentions = len([m for m in mentions if m['sentiment'] == 'negative'])
        neutral_mentions = total_mentions - positive_mentions - negative_mentions
        
        # AI risk analysis
        risk_score, risk_level, risk_icon = brand_analyzer.calculate_ai_risk(mentions)
        
        # Calculate additional metrics
        avg_confidence = round(sum(m.get('confidence', 50) for m in mentions) / len(mentions), 1) if mentions else 0
        sentiment_score = round((positive_mentions / total_mentions) * 100, 1) if total_mentions > 0 else 0
        
        response = {
            'brand': brand_name,
            'mentions': mentions,
            'total_mentions': total_mentions,
            'summary': {
                'positive_mentions': positive_mentions,
                'negative_mentions': negative_mentions,
                'neutral_mentions': neutral_mentions,
                'sentiment_score': sentiment_score,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_icon': risk_icon,
                'ai_analysis': ai_service.is_ai_available(),
                'ai_confidence_avg': avg_confidence,
                'analysis_timestamp': datetime.now().isoformat(),
                'processing_time': round(time.time() - start_time, 2)
            }
        }
        
        logger.info(f"✅ Analysis complete: {sentiment_score}% positive, {risk_level} risk, {total_mentions} mentions")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"❌ Analysis error: {e}")
        return jsonify({
            "error": "Internal server error during analysis",
            "ai_available": ai_service.is_ai_available(),
            "message": "Please try again later"
        }), 500

@app.route('/api/competitors', methods=['POST', 'OPTIONS'])
@rate_limit(max_requests=50, window_seconds=60)
def competitor_analysis():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        main_brand = data.get('brand', '').strip()
        
        if not main_brand:
            return jsonify({"error": "Brand name is required"}), 400
        
        # AI-powered competitor prediction
        competitors = brand_analyzer.predict_competitors(main_brand)
        
        # Generate more realistic competitor data
        main_brand_mentions = random.randint(100, 500)
        main_sentiment = random.randint(65, 85)
        
        analysis = {
            'main_brand': {
                'name': main_brand,
                'mentions': main_brand_mentions,
                'sentiment_score': main_sentiment,
                'ai_categorized': True,
                'market_share': round(random.uniform(15, 45), 1)
            },
            'competitors': []
        }
        
        for competitor in competitors:
            # Competitors have slightly different metrics
            comp_mentions = max(10, int(main_brand_mentions * random.uniform(0.3, 0.8)))
            comp_sentiment = random.randint(
                max(40, main_sentiment - 15), 
                min(90, main_sentiment + 5)
            )
            
            analysis['competitors'].append({
                'name': competitor,
                'mentions': comp_mentions,
                'sentiment_score': comp_sentiment,
                'trend': random.choice(['rising', 'stable', 'declining']),
                'threat_level': random.choice(['low', 'medium', 'high'])
            })
        
        return jsonify(analysis)
    
    except Exception as e:
        logger.error(f"❌ Competitor analysis error: {e}")
        return jsonify({"error": "Internal server error during competitor analysis"}), 500

@app.route('/api/ai-insights', methods=['POST', 'OPTIONS'])
@rate_limit(max_requests=30, window_seconds=60)
def ai_insights():
    """Advanced AI insights endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        brand_name = data.get('brand', '').strip()
        
        if not brand_name:
            return jsonify({"error": "Brand name is required"}), 400
        
        # More sophisticated insights based on brand characteristics
        brand_lower = brand_name.lower()
        
        # Determine industry for relevant insights
        industry = "general"
        if any(word in brand_lower for word in ['tech', 'software', 'app', 'digital']):
            industry = "technology"
        elif any(word in brand_lower for word in ['fashion', 'clothing', 'wear']):
            industry = "fashion"
        elif any(word in brand_lower for word in ['food', 'restaurant', 'cafe']):
            industry = "food"
        elif any(word in brand_lower for word in ['car', 'auto', 'vehicle']):
            industry = "automotive"
        
        insights = {
            'brand': brand_name,
            'industry': industry,
            'ai_insights': {
                'market_position': random.choice(['Leader', 'Challenger', 'Niche Player', 'Emerging']),
                'growth_trend': random.choice(['Rapid Growth', 'Stable', 'Volatile', 'Declining']),
                'customer_sentiment_trend': random.choice(['Improving', 'Stable', 'Concerning', 'Volatile']),
                'brand_health': random.choice(['Excellent', 'Good', 'Needs Attention', 'At Risk']),
                'recommended_actions': brand_analyzer.get_industry_actions(industry),
                'opportunity_areas': brand_analyzer.get_industry_opportunities(industry),
                'key_metrics': {
                    'social_engagement': f"{random.randint(50, 95)}%",
                    'response_rate': f"{random.randint(60, 98)}%",
                    'customer_satisfaction': f"{random.randint(70, 95)}%"
                }
            },
            'confidence_score': round(random.uniform(0.75, 0.95), 2),
            'ai_analysis': ai_service.is_ai_available(),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return jsonify(insights)
    
    except Exception as e:
        logger.error(f"❌ AI insights error: {e}")
        return jsonify({"error": "Internal server error generating insights"}), 500

@app.route('/api/ai-status', methods=['GET'])
def ai_status():
    """Check AI service status"""
    try:
        status = ai_service.get_service_status()
        return jsonify({
            'ai_available': ai_service.is_ai_available(),
            'status': 'active' if ai_service.is_ai_available() else 'fallback',
            'detailed_status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ AI status check error: {e}")
        return jsonify({
            'ai_available': False,
            'status': 'error',
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found", "path": request.path}), 404

@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests, please try again later"
    }), 429

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Store startup time for uptime tracking
app.start_time = time.time()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🧠 Echosphere AI Server Starting...")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"✅ Health Check: http://localhost:{port}/api/health")
    print(f"🔍 AI Status: http://localhost:{port}/api/ai-status")
    print(f"🤖 AI Available: {ai_service.is_ai_available()}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)