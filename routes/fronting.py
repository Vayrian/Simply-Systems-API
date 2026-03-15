
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

from extensions import db
from models.user import User
from models.member import Member
from models.front_log import FrontLog
from datetime import datetime

fronting_bp = Blueprint('fronting', __name__)

@fronting_bp.route('/user/current_fronter', methods=['PATCH'])
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