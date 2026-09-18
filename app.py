from flask import Flask, render_template, request, session, redirect, url_for, flash
import sqlite3
import joblib
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secure_key_123'

# --- 1. CONFIGURATION ---
try:
    model = joblib.load('crop_recommendation.pkl')
except FileNotFoundError:
    print("❌ Model not found. Run 'python train_model.py'")
    model = None

# LOCAL IMAGE PATHS
CROP_IMAGES = {
    'rice': '/static/images/rice.jpg', 'maize': '/static/images/maize.jpg',
    'chickpea': '/static/images/chickpea.jpg', 'kidneybeans': '/static/images/kidneybeans.jpg',
    'pigeonpeas': '/static/images/pigeonpeas.jpg', 'mothbeans': '/static/images/mothbeans.jpg',
    'mungbean': '/static/images/mungbean.jpg', 'blackgram': '/static/images/blackgram.jpg',
    'lentil': '/static/images/lentil.jpg', 'pomegranate': '/static/images/pomegranate.jpg',
    'banana': '/static/images/banana.jpg', 'mango': '/static/images/mango.jpg',
    'grapes': '/static/images/grapes.jpg', 'watermelon': '/static/images/watermelon.jpg',
    'muskmelon': '/static/images/muskmelon.jpg', 'apple': '/static/images/apple.jpg',
    'orange': '/static/images/orange.jpg', 'papaya': '/static/images/papaya.jpg',
    'coconut': '/static/images/coconut.jpg', 'cotton': '/static/images/cotton.jpg',
    'jute': '/static/images/jute.jpg', 'coffee': '/static/images/coffee.jpg',
    'ragi': '/static/images/ragi.jpg', 'wheat': '/static/images/wheat.jpg',
    'mustard': '/static/images/mustard.jpg', 'sugarcane': '/static/images/sugarcane.jpg',
    'groundnut': '/static/images/groundnut.jpg', 'default': '/static/images/default.jpg'
}

# MARKET PRICES (Updated 2025 Estimates - INR/Quintal)
# MARKET PRICES (Updated 2024-25 MSP & Mandi Rates - INR per Quintal)
MARKET_PRICES = {
    'rice': 2300,        # Common Paddy MSP approx
    'wheat': 2275,       # Rabi MSP
    'maize': 2090,       # Kharif MSP
    'cotton': 6620,      # Medium Staple MSP
    'sugarcane': 2840,    # FRP (Fair Remunerative Price)
    'jute': 5335,        # MSP 2024-25
    'groundnut': 6783,   # MSP
    'mustard': 5650,     # Rabi MSP
    'coffee': 18500,     # Arabica Avg Market Rate
    'ragi': 4290,        # MSP
    'chickpea': 5440,    # Gram MSP
    'kidneybeans': 8500, # Rajma (High Market Value)
    'pigeonpeas': 7550,  # Tur/Arhar MSP
    'mothbeans': 7000,   # Avg Market Rate
    'mungbean': 8558,    # Moong MSP (High Value)
    'blackgram': 7400,   # Urad MSP
    'lentil': 6425,      # Masur MSP
    'pomegranate': 11000,# High Value Fruit
    'banana': 3500,      # Avg Market Rate
    'mango': 5500,       # Seasonal Avg
    'grapes': 7500,      # Avg Market Rate
    'watermelon': 1800,  # Summer Rate
    'muskmelon': 2200,   # Summer Rate
    'apple': 12000,      # Shimla/Kashmir Avg
    'orange': 4500,      # Nagpur Avg
    'papaya': 2800,      # Avg Market Rate
    'coconut': 11160     # Milling Copra MSP
}

def get_db():
    conn = sqlite3.connect('farm.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- AUTH ROUTES --
@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name'] = user['full_name']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (username, password_hash, full_name) VALUES (?,?,?)', (username, hashed_pw, name))
            conn.commit()
            conn.close()
            flash("Registration Successful!")
            return redirect(url_for('login'))
        except:
            flash("Username exists.")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- DASHBOARD & TOOLS ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['name'])

@app.route('/soil', methods=['GET', 'POST'])
def soil():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        session['input_data'] = {
            'land_size': float(request.form['land_size']),
            'soil_type': request.form['soil_type'],
            'N': float(request.form['nitrogen']),
            'P': float(request.form['phosphorus']),
            'K': float(request.form['potassium']),
            'ph': float(request.form['ph'])
        }
        return redirect(url_for('weather'))
    return render_template('soil.html')

# --- UPDATE THIS FUNCTION IN APP.PY ---

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        temp = float(request.form['temperature'])
        hum = float(request.form['humidity'])
        rain = float(request.form['rainfall'])
        data = session.get('input_data')
        
        # 1. Prediction (Get Top 3)
        ml_input = np.array([[data['N'], data['P'], data['K'], temp, hum, data['ph'], rain]])
        probs = model.predict_proba(ml_input)[0]
        classes = model.classes_
        top3_indices = np.argsort(probs)[::-1][:3]
        
        results = []
        for i in top3_indices:
            c_name = classes[i]
            results.append({
                'name': c_name.upper(),
                'score': int(probs[i] * 100),
                'price': MARKET_PRICES.get(c_name.lower(), 'N/A'),
                'image': CROP_IMAGES.get(c_name.lower(), CROP_IMAGES['default'])
            })
            
        # 2. LAND BALANCING LOGIC (Strict > 1 Acre Rule)
        land_size = data['land_size']
        farm_plan = []
        
        if land_size > 1.0:
            # --- SPLIT STRATEGY (> 1 Acre) ---
            # 60% Primary Crop, 40% Secondary Crop (if available)
            area_main = round(land_size * 0.60, 2)
            farm_plan.append({'crop': results[0], 'area': area_main, 'percent': 60, 'type': 'Primary (High Yield)'})
            
            if len(results) > 1:
                area_sec = round(land_size * 0.40, 2)
                farm_plan.append({'crop': results[1], 'area': area_sec, 'percent': 40, 'type': 'Secondary (Insurance)'})
            else:
                # If model only returns 1 good crop, fallback to full land
                farm_plan[0]['area'] = land_size
                farm_plan[0]['percent'] = 100
        else:
            # --- MONOCULTURE STRATEGY (<= 1 Acre) ---
            # Small land is more efficient with a single focus
            farm_plan.append({'crop': results[0], 'area': land_size, 'percent': 100, 'type': 'Full Plantation'})

        session['results'] = results
        session['farm_plan'] = farm_plan
        
        # 3. Save to Database
        conn = get_db()
        try:
            conn.execute('INSERT INTO history (user_id, soil_type, n, p, k, ph, temperature, humidity, rainfall, predicted_crop) VALUES (?,?,?,?,?,?,?,?,?,?)',
                         (session['user_id'], data['soil_type'], data['N'], data['P'], data['K'], data['ph'], temp, hum, rain, results[0]['name']))
            conn.commit()
        except: pass
        conn.close()
        
        return redirect(url_for('result'))
        
    return render_template('weather.html')

@app.route('/result')
def result():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('result.html', crops=session.get('results', []), plan=session.get('farm_plan', []))

@app.route('/records')
def records():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    try:
        rows = conn.execute("SELECT users.full_name, history.*, strftime('%d-%m-%Y %H:%M', datetime(history.date, 'localtime')) as formatted_date FROM history JOIN users ON history.user_id = users.id WHERE history.user_id = ? ORDER BY date DESC", (session['user_id'],)).fetchall()
    except: rows = []
    conn.close()
    return render_template('records.html', rows=rows)

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.route('/guide')
def guide(): return render_template('guide.html')

# --- MARKET PRICES PAGE ---
@app.route('/market')
def market():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    # Pass the dictionary to the HTML page
    return render_template('market.html', prices=MARKET_PRICES)
# --- NEW BASIC FEATURES ---

@app.route('/fertilizer')
def fertilizer():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('fertilizer.html')

@app.route('/news')
def news():
    if 'user_id' not in session: return redirect(url_for('login'))
    # Dummy News Data (In a real app, this would come from an API)
    news_items = [
        {'title': 'Govt Increases MSP for Wheat', 'date': '28 Nov 2025', 'desc': 'The Minimum Support Price for Wheat has been hiked by ₹150 per quintal.', 'img': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=500'},
        {'title': 'New Subsidy for Drip Irrigation', 'date': '25 Nov 2025', 'desc': 'Farmers can now avail 45% subsidy on installing drip systems.', 'img': 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=500'},
        {'title': 'Organic Farming on the Rise', 'date': '20 Nov 2025', 'desc': 'Demand for organic vegetables sees a 30% spike in urban markets.', 'img': 'https://images.unsplash.com/photo-1595837941703-999330922881?w=500'}
    ]
    return render_template('news.html', news=news_items)

if __name__ == '__main__':
    app.run(debug=True)