from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime, timedelta
import re

app = Flask(__name__)
CORS(app)

print("🚀 Echosphere AI-Powered Backend Server Starting...")

class BrandAIAnalyzer:
    def __init__(self):
        self.sentiment_keywords = {
            'positive': ['love', 'amazing', 'great', 'excellent', 'awesome', 'best', 'perfect', 'outstanding'],
            'negative': ['hate', 'terrible', 'awful', 'worst', 'disappointed', 'bad', 'poor', 'horrible'],
            'urgent': ['urgent', 'immediately', 'asap', 'emergency', 'critical', 'important']
        }
        
        self.brand_categories = {
            'sports': ['nike', 'adidas', 'puma', 'reebok', 'under armour'],
            'tech': ['apple', 'samsung', 'google', 'microsoft', 'xiaomi'],
            'retail': ['amazon', 'flipkart', 'myntra', 'ajio', 'nykaa'],
            'beverage': ['starbucks', 'coca', 'pepsi', 'redbull', 'monster']
        }
    
    def analyze_sentiment(self, text):
        """AI-powered sentiment analysis using keyword matching"""
        text_lower = text.lower()
        
        positive_score = sum(1 for word in self.sentiment_keywords['positive'] if word in text_lower)
        negative_score = sum(1 for word in self.sentiment_keywords['negative'] if word in text_lower)
        urgent_score = sum(1 for word in self.sentiment_keywords['urgent'] if word in text_lower)
        
        if negative_score > positive_score:
            return 'negative', 'anger' if urgent_score > 0 else 'frustration'
        elif positive_score > negative_score:
            return 'positive', 'excitement' if urgent_score > 0 else 'joy'
        else:
            return 'neutral', 'neutral'
    
    def predict_competitors(self, brand_name):
        """AI-powered competitor prediction based on brand categories"""
        brand_lower = brand_name.lower()
        
        for category, brands in self.brand_categories.items():
            if brand_lower in brands:
                # Return other brands from same category
                return [b for b in brands if b != brand_lower][:3]
        
        # AI fallback - generate relevant competitors
        if 'wear' in brand_lower or 'fashion' in brand_lower:
            return ['Zara', 'H&M', 'Forever 21']
        elif 'tech' in brand_lower or 'electronic' in brand_lower:
            return ['Samsung', 'Google', 'OnePlus']
        else:
            return ['Market Leader', 'Emerging Brand', 'Local Competitor']
    
    def calculate_ai_risk(self, mentions):
        """Advanced AI risk calculation"""
        if not mentions:
            return 0, 'low', '🟢'
        
        negative_count = len([m for m in mentions if m['sentiment'] == 'negative'])
        anger_count = len([m for m in mentions if m['emotion'] == 'anger'])
        total_mentions = len(mentions)
        
        # AI risk algorithm
        risk_score = min(100, (negative_count * 10) + (anger_count * 20))
        
        # AI pattern detection
        if risk_score > 70:
            return risk_score, 'high', '🔴'
        elif risk_score > 40:
            return risk_score, 'medium', '🟡'
        else:
            return risk_score, 'low', '🟢'

# Initialize AI analyzer
ai_analyzer = BrandAIAnalyzer()

def generate_ai_mentions(brand_name, count=25):
    """Generate AI-enhanced realistic mentions"""
    platforms = ['Twitter', 'Reddit', 'Instagram', 'News', 'Forum', 'Blog']
    
    mention_templates = [
        f"Just tried {{brand}}'s new product and it's {{sentiment}}!",
        f"{{brand}} customer service was {{sentiment}} today.",
        f"Thinking about switching from {{brand}} to a competitor.",
        f"{{brand}}'s latest campaign is getting {{sentiment}} reactions.",
        f"Had a {{sentiment}} experience with {{brand}} support.",
        f"{{brand}} is trending for {{sentiment}} reasons today.",
        f"Compared {{brand}} with competitors - here are my thoughts.",
        f"{{brand}} needs to improve their {{aspect}} according to users."
    ]
    
    aspects = ['quality', 'pricing', 'service', 'delivery', 'features', 'innovation']
    
    mentions = []
    for i in range(count):
        template = random.choice(mention_templates)
        sentiment, emotion = ai_analyzer.analyze_sentiment(template)
        
        mention_text = template.format(
            brand=brand_name,
            sentiment='amazing' if sentiment == 'positive' else 'disappointing',
            aspect=random.choice(aspects)
        )
        
        # AI-enhanced mention generation
        mention = {
            'id': i + 1,
            'text': mention_text,
            'platform': random.choice(platforms),
            'sentiment': sentiment,
            'emotion': emotion,
            'timestamp': (datetime.now() - timedelta(
                hours=random.randint(0, 48),
                minutes=random.randint(0, 59)
            )).isoformat(),
            'username': f"user_{random.randint(1000, 9999)}",
            'engagement': random.randint(5, 2500),
            'verified': random.choice([True, False, False, False])  # 25% verified users
        }
        mentions.append(mention)
    
    return mentions

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Echosphere AI API is running! 🧠🌐"})

@app.route('/api/analyze', methods=['POST'])
def analyze_brand():
    try:
        data = request.json
        brand_name = data.get('brand', 'Unknown Brand')
        
        print(f"🧠 AI Analyzing brand: {brand_name}")
        
        # Generate AI-powered mentions
        mentions = generate_ai_mentions(brand_name)
        
        # Calculate AI metrics
        total_mentions = len(mentions)
        positive_mentions = len([m for m in mentions if m['sentiment'] == 'positive'])
        negative_mentions = len([m for m in mentions if m['sentiment'] == 'negative'])
        
        # AI risk analysis
        risk_score, risk_level, risk_icon = ai_analyzer.calculate_ai_risk(mentions)
        
        response = {
            'brand': brand_name,
            'mentions': mentions,
            'total_mentions': total_mentions,
            'summary': {
                'positive_mentions': positive_mentions,
                'negative_mentions': negative_mentions,
                'sentiment_score': round((positive_mentions / total_mentions) * 100, 1),
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_icon': risk_icon,
                'ai_analysis': True,
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        print(f"✅ AI Analysis complete: {response['summary']['sentiment_score']}% positive, {risk_level} risk")
        return jsonify(response)
    
    except Exception as e:
        print("❌ AI Analysis error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/competitors', methods=['POST'])
def competitor_analysis():
    data = request.json
    main_brand = data.get('brand', 'Your Brand')
    
    # AI-powered competitor prediction
    competitors = ai_analyzer.predict_competitors(main_brand)
    
    analysis = {
        'main_brand': {
            'name': main_brand,
            'mentions': random.randint(50, 200),
            'sentiment_score': random.randint(60, 90),
            'ai_categorized': True
        },
        'competitors': []
    }
    
    for competitor in competitors:
        analysis['competitors'].append({
            'name': competitor.title(),
            'mentions': random.randint(30, 150),
            'sentiment_score': random.randint(50, 85),
            'trend': random.choice(['rising', 'stable', 'declining'])
        })
    
    return jsonify(analysis)

@app.route('/api/ai-insights', methods=['POST'])
def ai_insights():
    """Advanced AI insights endpoint"""
    data = request.json
    brand_name = data.get('brand', 'Unknown Brand')
    
    insights = {
        'brand': brand_name,
        'ai_insights': {
            'market_position': random.choice(['Leader', 'Challenger', 'Niche', 'Emerging']),
            'growth_trend': random.choice(['Rapid', 'Stable', 'Volatile', 'Declining']),
            'customer_sentiment_trend': random.choice(['Improving', 'Stable', 'Concerning']),
            'recommended_actions': [
                "Engage with negative feedback on social media",
                "Highlight positive customer stories",
                "Monitor competitor pricing strategies",
                "Improve response time to customer queries"
            ],
            'opportunity_areas': [
                "Product quality mentions",
                "Customer service experience", 
                "Pricing competitiveness",
                "Brand perception"
            ]
        },
        'confidence_score': round(random.uniform(0.7, 0.95), 2)
    }
    
    return jsonify(insights)

if __name__ == '__main__':
    print("🧠 AI Server: http://localhost:5000")
    print("✅ Health Check: http://localhost:5000/api/health")
    print("🔍 AI Insights: http://localhost:5000/api/ai-insights")
    app.run(debug=True, port=5000)