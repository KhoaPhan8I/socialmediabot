"""
SocialMediaBot - AI-Powered Social Media Automation
Micro-SaaS for small businesses and content creators
"""
import os
import json
import stripe
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Payment config
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_placeholder')
BMAC_USERNAME = os.getenv('BMAC_USERNAME', 'khoaphan')
PAYPAL_EMAIL = os.getenv('PAYPAL_EMAIL', '')

# In-memory storage (replace with DB in production)
users = {}
posts = {}

# Landing page HTML
LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialMediaBot - AI Social Media Automation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; }
        .hero { min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; padding: 2rem; }
        .hero h1 { font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 1.2rem; color: #888; max-width: 600px; margin: 0 auto 2rem; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 1rem 2rem; border: none; border-radius: 8px; font-size: 1.1rem; cursor: pointer; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .pricing { display: flex; gap: 2rem; justify-content: center; margin-top: 4rem; flex-wrap: wrap; }
        .price-card { background: #1a1a1a; padding: 2rem; border-radius: 12px; width: 280px; border: 1px solid #333; }
        .price-card.featured { border-color: #667eea; }
        .price { font-size: 2.5rem; font-weight: bold; margin: 1rem 0; }
        .price span { font-size: 1rem; color: #888; }
        ul { list-style: none; text-align: left; margin: 1.5rem 0; }
        ul li { padding: 0.5rem 0; color: #aaa; }
        ul li::before { content: "✓ "; color: #667eea; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; max-width: 1200px; margin: 4rem auto; padding: 0 2rem; }
        .feature { background: #1a1a1a; padding: 2rem; border-radius: 12px; }
        .feature h3 { margin-bottom: 1rem; color: #667eea; }
    </style>
</head>
<body>
    <div class="hero">
        <div>
            <h1>SocialMediaBot</h1>
            <p>AI-powered social media automation for small businesses. Schedule posts, analyze engagement, and grow your audience - all on autopilot.</p>
            <button class="btn" onclick="window.location.href='/dashboard'">Start Free Trial</button>
            
            <div class="pricing">
                <div class="price-card">
                    <h3>Starter</h3>
                    <div class="price">$19<span>/mo</span></div>
                    <ul>
                        <li>3 social accounts</li>
                        <li>30 posts/month</li>
                        <li>Basic analytics</li>
                        <li>Email support</li>
                    </ul>
                    <a href="/pay/starter" class="btn" style="width:100%; text-decoration:none; display:block; text-align:center;">Get Started</a>
                </div>
                <div class="price-card featured">
                    <h3>Pro</h3>
                    <div class="price">$49<span>/mo</span></div>
                    <ul>
                        <li>10 social accounts</li>
                        <li>Unlimited posts</li>
                        <li>AI content generation</li>
                        <li>Advanced analytics</li>
                        <li>Priority support</li>
                    </ul>
                    <a href="/pay/pro" class="btn" style="width:100%; text-decoration:none; display:block; text-align:center;">Get Started</a>
                </div>
                <div class="price-card">
                    <h3>Business</h3>
                    <div class="price">$99<span>/mo</span></div>
                    <ul>
                        <li>Unlimited accounts</li>
                        <li>Unlimited posts</li>
                        <li>White-label option</li>
                        <li>API access</li>
                        <li>Dedicated support</li>
                    </ul>
                    <a href="/pay/business" class="btn" style="width:100%; text-decoration:none; display:block; text-align:center;">Contact Us</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="features">
        <div class="feature">
            <h3>AI Content Generation</h3>
            <p>Generate engaging posts, captions, and hashtags using advanced AI. Just describe your topic and let AI create content that converts.</p>
        </div>
        <div class="feature">
            <h3>Smart Scheduling</h3>
            <p>AI analyzes your audience and suggests optimal posting times. Schedule weeks of content in minutes.</p>
        </div>
        <div class="feature">
            <h3>Analytics Dashboard</h3>
            <p>Track engagement, followers, and growth across all platforms in one beautiful dashboard.</p>
        </div>
    </div>
</body>
</html>
"""

# Payment Page HTML
PAYMENT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout - SocialMediaBot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .checkout { max-width: 500px; width: 100%; padding: 2rem; }
        .plan-info { background: #1a1a1a; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; text-align: center; }
        .plan-info h2 { color: #667eea; margin-bottom: 0.5rem; }
        .plan-info .price { font-size: 3rem; font-weight: bold; margin: 1rem 0; }
        .plan-info .price span { font-size: 1rem; color: #888; }
        .payment-methods { display: flex; flex-direction: column; gap: 1rem; }
        .payment-btn { display: flex; align-items: center; justify-content: center; gap: 0.8rem; padding: 1.2rem; border: 2px solid #333; border-radius: 12px; background: #1a1a1a; color: #fff; font-size: 1.1rem; cursor: pointer; transition: all 0.2s; text-decoration: none; }
        .payment-btn:hover { border-color: #667eea; transform: translateY(-2px); }
        .payment-btn.stripe { background: linear-gradient(135deg, #635bff 0%, #7a73ff 100%); border-color: #635bff; }
        .payment-btn.bmac { background: linear-gradient(135deg, #ffdd00 0%, #ffaa00 100%); border-color: #ffdd00; color: #000; }
        .payment-btn.paypal { background: linear-gradient(135deg, #0070ba 0%, #003087 100%); border-color: #0070ba; }
        .payment-btn.crypto { background: linear-gradient(135deg, #f7931a 0%, #e8850a 100%); border-color: #f7931a; }
        .icon { font-size: 1.5rem; }
        .badge { font-size: 0.7rem; background: rgba(255,255,255,0.2); padding: 0.2rem 0.5rem; border-radius: 4px; }
        .divider { text-align: center; margin: 1.5rem 0; color: #666; }
        .features { text-align: left; margin-top: 1.5rem; }
        .features li { padding: 0.5rem 0; color: #aaa; list-style: none; }
        .features li::before { content: "✓ "; color: #667eea; }
        .back { text-align: center; margin-top: 2rem; }
        .back a { color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="checkout">
        <div class="plan-info">
            <h2>{{ plan.name }} Plan</h2>
            <div class="price">${{ plan.price }}<span>/month</span></div>
            <ul class="features">
                {% for f in plan.features %}
                <li>{{ f }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <h3 style="text-align: center; margin-bottom: 1rem; color: #888;">Choose Payment Method</h3>
        
        <div class="payment-methods">
            <!-- Buy Me a Coffee (Recommended) -->
            <a href="https://www.buymeacoffee.com/e/{{ bmac_username }}?amount={{ plan.price }}" 
               target="_blank" class="payment-btn bmac">
                <span class="icon">☕</span>
                Buy Me a Coffee
                <span class="badge">RECOMMENDED</span>
            </a>
            
            <!-- Stripe (Credit/Debit Card) -->
            <button onclick="payStripe()" class="payment-btn stripe">
                <span class="icon">💳</span>
                Credit/Debit Card
                <span class="badge">STRIPE</span>
            </button>
            
            <!-- PayPal -->
            <a href="https://paypal.me/khoaphan/{{ plan.price }}?currencyCode=USD" 
               target="_blank" class="payment-btn paypal">
                <span class="icon">🅿️</span>
                PayPal
            </a>
            
            <!-- Crypto (USDT) -->
            <button onclick="payCrypto()" class="payment-btn crypto">
                <span class="icon">₿</span>
                Crypto (USDT/BTC)
                <span class="badge">COMING SOON</span>
            </button>
        </div>
        
        <div class="back">
            <a href="/">← Back to Home</a>
        </div>
    </div>
    
    <script>
        function payStripe() {
            fetch('/api/create-checkout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({plan: '{{ plan.name|lower }}', price: {{ plan.price }}})
            })
            .then(res => res.json())
            .then(data => {
                if (data.url) window.location.href = data.url;
                else alert('Stripe not configured yet. Use Buy Me a Coffee!');
            })
            .catch(() => alert('Stripe not configured. Use Buy Me a Coffee!'));
        }
        
        function payCrypto() {
            alert('Crypto payments coming soon! Use Buy Me a Coffee or PayPal for now.');
        }
    </script>
</body>
</html>
"""

# Dashboard HTML
DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - SocialMediaBot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; }
        .nav { background: #1a1a1a; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .nav h2 { color: #667eea; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .card { background: #1a1a1a; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
        textarea, input, select { width: 100%; padding: 1rem; border: 1px solid #333; border-radius: 8px; background: #0a0a0a; color: #fff; margin: 0.5rem 0; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 0.8rem 1.5rem; border: none; border-radius: 8px; cursor: pointer; }
        .stat { text-align: center; padding: 1.5rem; }
        .stat h3 { font-size: 2rem; color: #667eea; }
        .stat p { color: #888; margin-top: 0.5rem; }
        .post-list { margin-top: 1rem; }
        .post-item { background: #0a0a0a; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
    </style>
</head>
<body>
    <div class="nav">
        <h2>SocialMediaBot</h2>
        <span>Dashboard</span>
    </div>
    <div class="container">
        <div class="grid">
            <div class="card stat">
                <h3 id="total-posts">0</h3>
                <p>Posts Scheduled</p>
            </div>
            <div class="card stat">
                <h3 id="total-accounts">0</h3>
                <p>Connected Accounts</p>
            </div>
            <div class="card stat">
                <h3 id="total-engagement">0</h3>
                <p>Total Engagement</p>
            </div>
        </div>
        
        <div class="card">
            <h3>Create New Post</h3>
            <select id="platform">
                <option value="twitter">Twitter/X</option>
                <option value="linkedin">LinkedIn</option>
                <option value="instagram">Instagram</option>
                <option value="facebook">Facebook</option>
            </select>
            <textarea id="content" placeholder="What do you want to post? Describe your topic and AI will generate content..."></textarea>
            <button class="btn" onclick="generateContent()">AI Generate</button>
            <button class="btn" onclick="schedulePost()" style="margin-left: 0.5rem">Schedule Post</button>
            <div id="generated-content" style="margin-top: 1rem; display: none;">
                <textarea id="final-content" rows="4"></textarea>
            </div>
        </div>
        
        <div class="card">
            <h3>Scheduled Posts</h3>
            <div id="post-list" class="post-list">No posts yet</div>
        </div>
    </div>
    
    <script>
        async function generateContent() {
            const topic = document.getElementById('content').value;
            if (!topic) return alert('Please describe your topic');
            
            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({topic, platform: document.getElementById('platform').value})
                });
                const data = await res.json();
                document.getElementById('final-content').value = data.content;
                document.getElementById('generated-content').style.display = 'block';
            } catch (e) {
                alert('Error generating content');
            }
        }
        
        async function schedulePost() {
            const content = document.getElementById('final-content').value || document.getElementById('content').value;
            if (!content) return alert('No content to post');
            
            try {
                const res = await fetch('/api/schedule', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        content,
                        platform: document.getElementById('platform').value,
                        scheduled_at: new Date().toISOString()
                    })
                });
                const data = await res.json();
                alert('Post scheduled!');
                loadPosts();
            } catch (e) {
                alert('Error scheduling post');
            }
        }
        
        async function loadPosts() {
            try {
                const res = await fetch('/api/posts');
                const data = await res.json();
                const list = document.getElementById('post-list');
                if (data.posts && data.posts.length > 0) {
                    list.innerHTML = data.posts.map(p => 
                        '<div class="post-item"><strong>' + p.platform + '</strong>: ' + p.content.substring(0, 100) + '...</div>'
                    ).join('');
                    document.getElementById('total-posts').textContent = data.posts.length;
                }
            } catch (e) {}
        }
        
        loadPosts();
    </script>
</body>
</html>
"""

@app.route('/')
def landing():
    return render_template_string(LANDING_PAGE)

@app.route('/pay/<plan>')
def payment_page(plan):
    """Multi-payment checkout page"""
    plans = {
        'starter': {'name': 'Starter', 'price': 19, 'features': ['3 social accounts', '30 posts/month', 'Basic analytics']},
        'pro': {'name': 'Pro', 'price': 49, 'features': ['10 social accounts', 'Unlimited posts', 'AI content generation']},
        'business': {'name': 'Business', 'price': 99, 'features': ['Unlimited accounts', 'API access', 'White-label']}
    }
    p = plans.get(plan, plans['pro'])
    return render_template_string(PAYMENT_PAGE, plan=p, bmac_username=BMAC_USERNAME)

@app.route('/dashboard')
def dashboard():
    return render_template_string(DASHBOARD_PAGE)

# API endpoints
@app.route('/api/generate', methods=['POST'])
def generate_content():
    """Generate AI content for social media"""
    data = request.json
    topic = data.get('topic', '')
    platform = data.get('platform', 'twitter')
    
    # Simple content generation (replace with actual AI API)
    templates = {
        'twitter': f"🚀 {topic}\n\nKey insights:\n✅ Save time with automation\n✅ Grow your audience\n✅ Boost engagement\n\n#SocialMedia #Automation #Growth",
        'linkedin': f"I've been thinking about {topic} lately.\n\nHere are my key takeaways:\n\n1. Automation saves 10+ hours/week\n2. Consistency is key to growth\n3. Data-driven decisions win\n\nWhat's your experience? Share below! 👇\n\n#ProfessionalDevelopment #Growth",
        'instagram': f"✨ {topic} ✨\n\nDouble tap if you agree! 💖\n\n#Motivation #Growth #Success",
        'facebook': f"Hey everyone! 👋\n\nI wanted to share my thoughts on {topic}...\n\nWhat do you think? Let me know in the comments!"
    }
    
    content = templates.get(platform, templates['twitter'])
    return jsonify({'content': content, 'platform': platform})

@app.route('/api/schedule', methods=['POST'])
def schedule_post():
    """Schedule a social media post"""
    data = request.json
    post_id = str(len(posts) + 1)
    posts[post_id] = {
        'id': post_id,
        'content': data.get('content', ''),
        'platform': data.get('platform', 'twitter'),
        'scheduled_at': data.get('scheduled_at', datetime.now().toISOString()),
        'status': 'scheduled',
        'created_at': datetime.now().toISOString()
    }
    return jsonify({'success': True, 'post_id': post_id})

@app.route('/api/posts')
def get_posts():
    """Get all scheduled posts"""
    return jsonify({'posts': list(posts.values())})

@app.route('/api/analytics')
def get_analytics():
    """Get analytics data"""
    return jsonify({
        'total_posts': len(posts),
        'total_accounts': 3,
        'engagement_rate': 4.5,
        'followers_growth': 127
    })

# Stripe payment endpoints
@app.route('/api/create-checkout', methods=['POST'])
def create_checkout():
    """Create Stripe checkout session"""
    data = request.json
    price_id = data.get('price_id', 'price_placeholder')
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'dashboard?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url,
        )
        return jsonify({'sessionId': session.id, 'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Stripe webhook handler"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    # Verify webhook (add your webhook secret)
    # event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    
    # For now, just return success
    return jsonify({'success': True})

# Health check
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'SocialMediaBot', 'version': '1.0.0'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)