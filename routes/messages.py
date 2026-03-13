from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.message import Message
from models.member import Member

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    user_id = int(get_jwt_identity())
    messages = Message.query.join(Member, Message.sender_member_id == Member.id)\
        .filter(Member.user_id == user_id)\
        .order_by(Message.timestamp.asc()).all()

    print(f"[CHAT HISTORY] Found {len(messages)} messages for user {user_id}")
    return jsonify([m.to_dict() for m in messages]), 200