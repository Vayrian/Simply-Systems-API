
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

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    pronouns = db.Column(db.String(50))
    description = db.Column(db.Text)
    color = db.Column(db.String(7))                     # hex, e.g. #FF5555
    age_range = db.Column(db.String(50), nullable=True) # new: "24-27", "ageless", "little"
    role = db.Column(db.String(100), nullable=True)     # new: "host", "protector", etc.
    birthday = db.Column(db.Date, nullable=True)        # new
    bio = db.Column(db.Text, nullable=True)             # new: longer bio/notes
    icon_emoji = db.Column(db.String(20), nullable=True)# new: single emoji or short string
    avatar_url = db.Column(db.String(255), nullable=True)  # new: optional image URL
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pronouns': self.pronouns,
            'description': self.description,
            'color': self.color,
            'age_range': self.age_range,
            'role': self.role,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'bio': self.bio,
            'icon_emoji': self.icon_emoji,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }