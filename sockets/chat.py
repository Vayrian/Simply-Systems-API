from flask_socketio import emit, join_room

from extensions import socketio
from extensions import db
from models.member import Member
from models.message import Message
from datetime import datetime

def init_socket_handlers(socketio):
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