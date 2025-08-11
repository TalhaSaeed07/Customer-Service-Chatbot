from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import requests
import re

# === Load environment variables from .env ===
load_dotenv()

# === Initialize Flask App ===
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# === Database Setup ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
db = SQLAlchemy(app)

# === Database Model ===
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Boolean, default=True)
    price = db.Column(db.Float, nullable=False)
    delivery_charge = db.Column(db.Float, nullable=False, default=200.0)

# === Initialize DB & Add Sample Products if Missing ===
with app.app_context():
    db.drop_all()  
    db.create_all()
    
    # Add Smart Watch 110 if not exists
    if not Product.query.filter_by(name="Smart Watch 110").first():
        sample_product = Product(name="Smart Watch 110", available=True, price=1999.99, delivery_charge=150.0)
        db.session.add(sample_product)
    
    # Add Premium Watch Series X if not exists
    if not Product.query.filter_by(name="Premium Watch Series X").first():
        premium_watch = Product(name="Premium Watch Series X", available=True, price=3499.99, delivery_charge=250.0)
        db.session.add(premium_watch)
    
    # Add Fitness Tracker Pro if not exists
    if not Product.query.filter_by(name="Fitness Tracker Pro").first():
        fitness_tracker = Product(name="Fitness Tracker Pro", available=True, price=2799.99, delivery_charge=180.0)
        db.session.add(fitness_tracker)
    
    # Add Classic Analog Watch if not exists
    if not Product.query.filter_by(name="Classic Analog Watch").first():
        classic_watch = Product(name="Classic Analog Watch", available=True, price=1299.99, delivery_charge=120.0)
        db.session.add(classic_watch)
    
    # Add Digital Smart Band if not exists
    if not Product.query.filter_by(name="Digital Smart Band").first():
        smart_band = Product(name="Digital Smart Band", available=True, price=899.99, delivery_charge=100.0)
        db.session.add(smart_band)
    
    db.session.commit()

# === OpenRouter Setup ===
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",  
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "MyTestApp"
}


# === ROUTES ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    lower_msg = user_message.lower()

    # === STEP 1: Capture FAQ Type ===
    faq_info = check_faqs(user_message)  
    faq_text = faq_info if faq_info else ""

    # === STEP 2: Check for mentioned product ===
    product_text = ""
    matched_product = None
    products = Product.query.all()

    for product in products:
        if product.name.lower() in lower_msg:
            matched_product = product
            session["last_product"] = product.name
            status = "🟢 Available" if product.available else "🔴 Out of Stock"
            product_text = f"📦 Product: {product.name}\nPrice: Rs{product.price}\nDelivery Charge: Rs{product.delivery_charge}\nStatus: {status}"
            break  

    # === STEP 3: Fallback to LLM with both FAQ and product info if any ===
    available_products = Product.query.filter_by(available=True).all()
    product_list = "\n".join([f"- {p.name} (Rs {p.price}, Delivery: Rs{p.delivery_charge})" for p in available_products])

    # Combine system prompt
    system_prompt = f"""
You are a precise and professional customer support assistant for 'The Brands' - a Pakistani eCommerce store specializing in watches.

**CRITICAL RULES:**
1. ONLY provide information about these available products:
{product_list}

2. If customer asks about unavailable products, politely redirect to available options
3. Keep responses concise (2-3 sentences maximum)
4. Always mention prices in Pakistani Rupees (Rs)
5. Only deliver within Pakistan - no international shipping
6. Never invent features, links, or product details not provided

**CUSTOMER QUERY:** "{user_message}"

**RELEVANT INFORMATION:**
{faq_text}

{product_text}

**RESPONSE GUIDELINES:**
- If product-specific info is available, lead with that
- If FAQ applies, include it briefly
- Be direct and solution-oriented
- Use friendly but professional tone
- End with a clear next step or question if needed
"""

    # === Maintain chat history ===
    if "chat_history" not in session:
        session["chat_history"] = []

    session["chat_history"].append({"role": "user", "content": user_message})
    session["chat_history"] = session["chat_history"][-10:]

    messages = [{"role": "system", "content": system_prompt}] + session["chat_history"]

    try:
        response_text = send_message(messages)
        session["chat_history"].append({"role": "assistant", "content": response_text})
        session["chat_history"] = session["chat_history"][-10:]
        return jsonify({"reply": response_text})
    except Exception as e:
        print("API Error:", e)
        return jsonify({"reply": "Sorry, something went wrong. Please try again later."})


# === SEND TO LLM ===
def send_message(messages):
    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# === PRODUCT LOOKUP ===
def check_product_query(text):
    text_lower = text.lower()
    products = Product.query.all()
    for product in products:
        if product.name.lower() in text_lower:
            session["last_product"] = product.name  # ✅ Remember product
            status = "🟢 Available" if product.available else "🔴 Out of Stock"
            return f"📦 Product: {product.name}\nPrice: Rs{product.price}\nDelivery Charge: Rs{product.delivery_charge}\nStatus: {status}"
    return None

# === FAQ HANDLERS ===
def check_faqs(user_input):
    if international_delivery_check(user_input):
        return "🚫 Sorry, we currently only deliver within Pakistan."

    if product_information_faq(user_input):
        return "Please specify the product name you're interested in. I will provide the details."

    if shipping_details_faq(user_input):
        return (
            "📦 Shipping Info:\n"
            "- Standard delivery: 3–5 business days\n"
            "- Express delivery: 1–2 business days\n"
            "- Free shipping on orders over Rs5000\n"
            "- 7-day return policy\n"
            "🚚 Delivery only within Pakistan."
        )

    if customer_support_faq(user_input):
        return (
            "🛠️ Customer Support:\n"
            "Customer care: \n"
            "- For order issues, contact: support@example.com\n"
            "- Call us at +92-800-123-4567"
        )

    return None

# === FAQ SUBLOGIC ===
def international_delivery_check(text):
    keywords = {
        "do you deliver to", "can you ship to", "outside pakistan",
        "international shipping", "deliver abroad", "ship worldwide",
        "ship to usa", "ship to uk", "ship to india", "ship to canada",
        "ship internationally", "deliver to other countries", "deliver to china",
        "deliver to australia", "deliver to europe", "deliver to middle east",
        "deliver within china", "deliver within india", "deliver within usa",
        "deliver within uk", "deliver within canada", "deliver within australia", "deliver it in china", "deliver in india"
    }
    return any(k in text.lower() for k in keywords)

def product_information_faq(text):
    keywords = {"product", "products", "items", "features", "specification", "price"}
    return any(k in text.lower() for k in keywords)

def shipping_details_faq(text):
    keywords = {"shipping", "delivery", "return", "returns", "track", "tracking"}
    return any(k in text.lower() for k in keywords)

def customer_support_faq(text):
    keywords = {"support", "help", "issue", "problem", "contact", "complaint", "service"}
    return any(k in text.lower() for k in keywords)

def is_international_location(text):
    international_keywords = {
        "outside pakistan", "international", "abroad", "worldwide", "overseas", "china", "india", "usa", "uk", "canada",
        "australia", "europe", "germany", "uae", "dubai", "qatar", "france", "singapore"
    }
    return any(k in text.lower() for k in international_keywords)

def is_domestic_location(text):
    pakistan_cities = {
        "lahore", "karachi", "islamabad", "rawalpindi", "faisalabad", "multan", "peshawar", "quetta", "sialkot"
    }
    return any(k in text.lower() for k in pakistan_cities)

# === MAIN ===
if __name__ == "__main__":
    app.run(debug=True)
