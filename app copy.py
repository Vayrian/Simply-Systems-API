# simply-plural-backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta, datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-me-immediately')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-me')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///simply.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("[CONFIG] JWT_SECRET_KEY length:", len(app.config['JWT_SECRET_KEY']))

# CORS - allow all for development (tighten in production)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"], "supports_credentials": True}})

socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)
db = SQLAlchemy(app)

# ──────────────────────────────────────────────────────────────
# MODELS
# ──────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_system_owner = db.Column(db.Boolean, default=False)
    display_name = db.Column(db.String(100), nullable=True)
    current_fronter_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    front_start_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    pronouns = db.Column(db.String(50))
    description = db.Column(db.Text)
    color = db.Column(db.String(7))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pronouns': self.pronouns,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FrontLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds
        }

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        sender = Member.query.get(self.sender_member_id)
        return {
            'id': self.id,
            'sender_id': self.sender_member_id,
            'sender_name': sender.name if sender else 'Unknown',
            'sender_color': sender.color if sender else '#808080',
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

# Create all tables
with app.app_context():
    db.create_all()

# JWT error logging
@jwt.invalid_token_loader
def invalid_token(error):
    print(f"[JWT INVALID] {error}")
    return jsonify({"error": "Invalid token", "details": str(error)}), 422

@jwt.unauthorized_loader
def missing_token(error):
    print(f"[JWT MISSING] {error}")
    return jsonify({"error": "Missing token"}), 401

# ──────────────────────────────────────────────────────────────
# SOCKET.IO – Internal group chat (system-wide)
# ──────────────────────────────────────────────────────────────

@socketio.on('connect')
def handle_connect():
    print("[SOCKET] Client connected")

@socketio.on('join_system_chat')
def on_join(data):
    user_id = data.get('user_id')
    if not user_id:
        return
    room = f"system_{user_id}"
    join_room(room)
    print(f"[SOCKET] Joined system chat room {room}")

@socketio.on('send_message')
def handle_message(data):
    print("[SOCKET] send_message received:", data)

    user_id = data.get('user_id')
    sender_member_id = data.get('sender_member_id')
    content = data.get('content')

    if not user_id or not sender_member_id or not content:
        emit('error', {'message': 'Missing required fields'})
        return

    # Verify sender belongs to the user/system
    member = Member.query.filter_by(id=sender_member_id, user_id=user_id).first()
    if not member:
        print(f"[CHAT ERROR] Invalid sender: member {sender_member_id} not owned by user {user_id}")
        emit('error', {'message': 'Invalid sender member'})
        return

    message = Message(
        sender_member_id=sender_member_id,
        content=content,
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    print(f"[MESSAGE] Saved message ID {message.id} from member {sender_member_id} in system {user_id}")

    room = f"system_{user_id}"
    emit('receive_message', message.to_dict(), room=room)

# ──────────────────────────────────────────────────────────────
# REST Routes
# ──────────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed = generate_password_hash(password)
    user = User(email=email, password_hash=hashed)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    print(f"[REGISTER] New user {email}, ID {user.id}")

    return jsonify({
        "message": "Registered",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "is_system_owner": user.is_system_owner,
            "display_name": user.display_name
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    print(f"[LOGIN] Success for {email}")

    return jsonify({
        "message": "Logged in",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "is_system_owner": user.is_system_owner,
            "display_name": user.display_name
        }
    }), 200

@app.route('/api/user/profile', methods=['GET', 'PATCH'])
@jwt_required()
def user_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if request.method == 'GET':
        print(f"[PROFILE GET] Fetched for user {user_id}")
        return jsonify({
            "id": user.id,
            "email": user.email,
            "is_system_owner": user.is_system_owner,
            "display_name": user.display_name,
            "current_fronter_id": user.current_fronter_id,
            "front_start_time": user.front_start_time.isoformat() if user.front_start_time else None
        }), 200

    if request.method == 'PATCH':
        if not request.is_json:
            return jsonify({"error": "JSON required"}), 400

        data = request.get_json()
        print(f"[PROFILE PATCH] Data for user {user_id}: {data}")

        if 'is_system_owner' in data:
            user.is_system_owner = bool(data['is_system_owner'])
        if 'display_name' in data:
            user.display_name = data['display_name'].strip() if data['display_name'] else None

        db.session.commit()
        print(f"[SUCCESS] Profile updated for user {user_id}")

        return jsonify({
            "is_system_owner": user.is_system_owner,
            "display_name": user.display_name
        }), 200

@app.route('/api/user/current_fronter', methods=['PATCH'])
@jwt_required()
def set_current_fronter():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400

    data = request.get_json()
    member_id = data.get('member_id')

    if member_id is not None:
        member = Member.query.filter_by(id=member_id, user_id=user_id).first()
        if not member:
            print(f"[FRONTING ERROR] User {user_id} tried to front member {member_id} (not owned)")
            return jsonify({"error": "Member not found or not owned by user"}), 404

        # Close any existing fronting session
        if user.current_fronter_id is not None and user.current_fronter_id != member_id:
            old_log = FrontLog.query.filter_by(member_id=user.current_fronter_id, end_time=None).first()
            if old_log:
                old_log.end_time = datetime.utcnow()
                old_log.duration_seconds = int((old_log.end_time - old_log.start_time).total_seconds())
                db.session.add(old_log)

        # Start new fronting log
        new_log = FrontLog(
            member_id=member_id,
            user_id=user_id,
            start_time=datetime.utcnow()
        )
        db.session.add(new_log)

        user.current_fronter_id = member_id
        user.front_start_time = datetime.utcnow()
    else:
        # Stop fronting - close current log
        if user.current_fronter_id is not None:
            log = FrontLog.query.filter_by(member_id=user.current_fronter_id, end_time=None).first()
            if log:
                log.end_time = datetime.utcnow()
                log.duration_seconds = int((log.end_time - log.start_time).total_seconds())
                db.session.add(log)

        user.current_fronter_id = None
        user.front_start_time = None

    db.session.commit()
    print(f"[FRONTING] User {user_id} set current fronter to {member_id}")

    return jsonify({
        "current_fronter_id": user.current_fronter_id,
        "front_start_time": user.front_start_time.isoformat() if user.front_start_time else None
    }), 200

@app.route('/api/front-history', methods=['GET'])
@jwt_required()
def front_history():
    user_id = int(get_jwt_identity())
    logs = FrontLog.query.filter_by(user_id=user_id).order_by(FrontLog.start_time.desc()).all()
    print(f"[HISTORY] Returning {len(logs)} entries for user {user_id}")
    return jsonify([log.to_dict() for log in logs]), 200

@app.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages():
    user_id = int(get_jwt_identity())
    messages = Message.query.join(Member, Message.sender_member_id == Member.id)\
        .filter(Member.user_id == user_id)\
        .order_by(Message.timestamp.asc()).all()

    print(f"[CHAT HISTORY] Query executed for user {user_id} - found {len(messages)} messages")
    return jsonify([m.to_dict() for m in messages]), 200

@app.route('/api/members', methods=['GET', 'POST'])
@jwt_required()
def members():
    user_id = int(get_jwt_identity())
    print(f"[DEBUG] User {user_id} -> /api/members ({request.method})")

    if request.method == 'GET':
        members = Member.query.filter_by(user_id=user_id).all()
        return jsonify([m.to_dict() for m in members]), 200

    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "JSON required"}), 400

        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({"error": "Name is required"}), 422

        member = Member(
            user_id=user_id,
            name=name,
            pronouns=data.get('pronouns'),
            description=data.get('description'),
            color=data.get('color')
        )
        db.session.add(member)
        db.session.commit()

        return jsonify(member.to_dict()), 201

@app.route('/api/members/<int:member_id>', methods=['PATCH', 'DELETE'])
@jwt_required()
def member_detail(member_id):
    user_id = int(get_jwt_identity())
    member = Member.query.filter_by(id=member_id, user_id=user_id).first_or_404()

    if request.method == 'DELETE':
        db.session.delete(member)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200

    if request.method == 'PATCH':
        if not request.is_json:
            return jsonify({"error": "JSON required"}), 400

        data = request.get_json()
        if 'name' in data:
            member.name = data['name']
        if 'pronouns' in data:
            member.pronouns = data['pronouns']
        if 'description' in data:
            member.description = data['description']
        if 'color' in data:
            member.color = data['color']

        db.session.commit()
        return jsonify(member.to_dict()), 200

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)