from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

print("🚀 Echosphere Backend Server Starting...")

def generate_mock_mentions(brand_name, count=25):
    # More realistic data
    sentiments = ['positive', 'negative', 'neutral']
    platforms = ['Twitter', 'Reddit', 'Instagram', 'News', 'Forum']
    emotions = ['anger', 'excitement', 'neutral', 'frustration', 'joy', 'surprise']
    
    # Realistic comment templates for different brands
    comment_templates = {
        'positive': [
            f"Just bought the new {brand_name} product and I'm loving it! 🎉",
            f"{brand_name} never disappoints. Quality is always top-notch!",
            f"Big fan of {brand_name}'s customer service. They really care!",
            f"The {brand_name} team is doing amazing work. Keep it up! 👏",
            f"Just tried {brand_name} for the first time - blown away by the quality!",
            f"{brand_name}'s new feature is a game-changer! 🔥",
            f"Shoutout to {brand_name} for their excellent support team!",
            f"Been using {brand_name} for months now - absolutely worth it!",
        ],
        'negative': [
            f"Very disappointed with {brand_name}'s service today. 😠",
            f"{brand_name} product stopped working after just 2 weeks. Poor quality!",
            f"Waiting on {brand_name} support for 3 days now. Very frustrating!",
            f"{brand_name}'s pricing is getting ridiculous. Time to switch?",
            f"Had a terrible experience with {brand_name} customer service.",
            f"{brand_name} promised features that don't work as advertised.",
            f"Product from {brand_name} arrived damaged. Poor packaging!",
            f"{brand_name} needs to improve their quality control. 😞",
        ],
        'neutral': [
            f"Just saw {brand_name} mentioned in the news today.",
            f"Anyone else using {brand_name}? What are your thoughts?",
            f"Thinking about trying {brand_name}. Any recommendations?",
            f"{brand_name} is trending in my feed right now.",
            f"Interesting discussion about {brand_name} on the forum.",
            f"Read an article about {brand_name}'s market strategy.",
            f"Not sure how I feel about {brand_name}'s new direction.",
            f"{brand_name} seems to be expanding to new markets.",
        ]
    }
    
    mentions = []
    for i in range(count):
        sentiment = random.choice(sentiments)
        emotion = random.choice(emotions)
        
        # Make emotions match sentiments more realistically
        if sentiment == 'positive' and emotion in ['anger', 'frustration']:
            emotion = random.choice(['excitement', 'joy', 'surprise'])
        elif sentiment == 'negative' and emotion in ['excitement', 'joy']:
            emotion = random.choice(['anger', 'frustration', 'neutral'])
        
        mention = {
            'id': i + 1,
            'text': random.choice(comment_templates[sentiment]),
            'platform': random.choice(platforms),
            'sentiment': sentiment,
            'emotion': emotion,
            'timestamp': (datetime.now() - timedelta(
                hours=random.randint(0, 48),
                minutes=random.randint(0, 59)
            )).isoformat(),
            'username': f"user_{random.randint(1000, 9999)}",
            'engagement': random.randint(5, 2500),  # More realistic engagement numbers
            'location': random.choice(['New York', 'London', 'Mumbai', 'Tokyo', 'Sydney', 'Berlin', 'San Francisco'])
        }
        mentions.append(mention)
    
    return mentions

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Echosphere API is running! 🌐"})

@app.route('/api/analyze', methods=['POST'])
def analyze_brand():
    try:
        data = request.json
        brand_name = data.get('brand', 'Unknown Brand')
        
        print(f"📊 Analyzing brand: {brand_name}")
        
        # Generate realistic mentions
        mentions = generate_mock_mentions(brand_name)
        
        # Calculate metrics
        total_mentions = len(mentions)
        positive_mentions = len([m for m in mentions if m['sentiment'] == 'positive'])
        negative_mentions = len([m for m in mentions if m['sentiment'] == 'negative'])
        anger_mentions = len([m for m in mentions if m['emotion'] == 'anger'])
        
        # More realistic risk calculation
        sentiment_score = round((positive_mentions / total_mentions) * 100, 1) if total_mentions > 0 else 0
        risk_score = min(100, (negative_mentions * 8) + (anger_mentions * 12))
        
        if risk_score > 70:
            risk_level = "high"
            risk_icon = "🔴"
        elif risk_score > 40:
            risk_level = "medium" 
            risk_icon = "🟡"
        else:
            risk_level = "low"
            risk_icon = "🟢"
        
        response = {
            'brand': brand_name,
            'mentions': mentions,
            'total_mentions': total_mentions,
            'summary': {
                'positive_mentions': positive_mentions,
                'negative_mentions': negative_mentions,
                'sentiment_score': sentiment_score,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_icon': risk_icon,
                'anger_mentions': anger_mentions
            }
        }
        
        print(f"✅ Analysis complete: {sentiment_score}% positive, {risk_level} risk")
        return jsonify(response)
    
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/competitors', methods=['POST'])
def competitor_analysis():
    data = request.json
    main_brand = data.get('brand', 'Your Brand')
    
    competitors = ['Adidas', 'Puma', 'Reebok'] if 'nike' in main_brand.lower() else ['Starbucks', 'Dunkin'] if 'starbucks' in main_brand.lower() else ['Samsung', 'Google'] if 'apple' in main_brand.lower() else ['Competitor A', 'Competitor B']
    
    analysis = {
        'main_brand': {
            'name': main_brand,
            'mentions': random.randint(50, 200),
            'sentiment_score': random.randint(60, 90),
        },
        'competitors': []
    }
    
    for competitor in competitors:
        analysis['competitors'].append({
            'name': competitor,
            'mentions': random.randint(30, 150),
            'sentiment_score': random.randint(50, 85),
        })
    
    return jsonify(analysis)

if __name__ == '__main__':
    print("🌐 Server: http://localhost:5000")
    print("✅ Health Check: http://localhost:5000/api/health")
    app.run(debug=True, port=5000)