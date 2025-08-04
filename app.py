from flask import Flask, request, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
import random
import requests

app = Flask(__name__)
app.secret_key = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime)

    user_agent = db.Column(db.Text)
    language = db.Column(db.String(20))
    platform = db.Column(db.String(100))
    screen_width = db.Column(db.String(10))
    screen_height = db.Column(db.String(10))
    timezone = db.Column(db.String(50))
    referer = db.Column(db.Text)

@app.before_first_request
def create_db():
    db.create_all()

@app.route('/')
def index():
    return redirect("/redirect")

@app.route('/redirect')
def redirect_page():
    return render_template('redirect.html')

@app.route('/collect', methods=['POST'])
def collect():
    data = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    now = datetime.datetime.now()

    city = region = country = None
    try:
        geo = requests.get(f"https://ipinfo.io/{ip}/json").json()
        city = geo.get('city')
        region = geo.get('region')
        country = geo.get('country')
    except:
        pass

    visit = Visit(
        ip=ip,
        city=city,
        region=region,
        country=country,
        timestamp=now,
        user_agent=data.get("user_agent"),
        language=data.get("language"),
        platform=data.get("platform"),
        screen_width=data.get("screen_width"),
        screen_height=data.get("screen_height"),
        timezone=data.get("timezone"),
        referer=data.get("referer")
    )
    db.session.add(visit)
    db.session.commit()

    return jsonify({"status": "ok"})

@app.route('/api/visits')
def api_visits():
    visits = Visit.query.order_by(Visit.timestamp.desc()).limit(100).all()
    return jsonify([
        {
            "timestamp": v.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "ip": v.ip,
            "city": v.city,
            "region": v.region,
            "country": v.country,
            "user_agent": v.user_agent,
            "language": v.language,
            "platform": v.platform,
            "screen": f"{v.screen_width}x{v.screen_height}",
            "timezone": v.timezone,
            "referer": v.referer
        } for v in visits
    ])

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
