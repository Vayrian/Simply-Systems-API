
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


from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from extensions import db
from models.member import Member

members_bp = Blueprint('members', __name__)

@members_bp.route('/members', methods=['GET', 'POST'])
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
            color=data.get('color'),
            age_range=data.get('age_range'),
            role=data.get('role'),
            birthday=datetime.strptime(data['birthday'], '%Y-%m-%d').date() if data.get('birthday') else None,
            bio=data.get('bio'),
            icon_emoji=data.get('icon_emoji'),
            avatar_url=data.get('avatar_url')
        )
        db.session.add(member)
        db.session.commit()

        return jsonify(member.to_dict()), 201

@members_bp.route('/members/<int:member_id>', methods=['PATCH', 'DELETE'])
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
        print(f"[MEMBER PATCH] Data for member {member_id}: {data}")

        if 'name' in data:
            member.name = data['name']
        if 'pronouns' in data:
            member.pronouns = data['pronouns']
        if 'description' in data:
            member.description = data['description']
        if 'color' in data:
            member.color = data['color']
        if 'age_range' in data:
            member.age_range = data['age_range']
        if 'role' in data:
            member.role = data['role']
        if 'birthday' in data and data['birthday']:
            try:
                member.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid birthday format (use YYYY-MM-DD)"}), 400
        if 'bio' in data:
            member.bio = data['bio']
        if 'icon_emoji' in data:
            member.icon_emoji = data['icon_emoji']
        if 'avatar_url' in data:
            member.avatar_url = data['avatar_url']

        db.session.commit()
        return jsonify(member.to_dict()), 200