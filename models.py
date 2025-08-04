from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100))
    user_agent = db.Column(db.String(300))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime)