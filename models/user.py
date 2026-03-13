from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_system_owner = db.Column(db.Boolean, default=False)
    display_name = db.Column(db.String(100), nullable=True)
    current_fronter_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    front_start_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())