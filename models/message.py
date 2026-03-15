
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


from extensions import db

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