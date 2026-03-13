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