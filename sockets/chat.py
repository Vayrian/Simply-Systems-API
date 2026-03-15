
#  -----------------------------------------------------------------------------
#  Simply Systems
#  A mobile app (iOS & Android) for plural systems to manage system members,
#  track fronting history, communicate internally via real-time chat, etc.
# -----------------------------------------------------------------------------
#  Copyright (C) 2026 Vayrian

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see https://www.gnu.org/licenses/.

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