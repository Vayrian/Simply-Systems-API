
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


from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.front_log import FrontLog

front_history_bp = Blueprint('front_history', __name__)

@front_history_bp.route('/front-history', methods=['GET'])
@jwt_required()
def front_history():
    user_id = int(get_jwt_identity())
    logs = FrontLog.query.filter_by(user_id=user_id).order_by(FrontLog.start_time.desc()).all()
    print(f"[HISTORY] Returning {len(logs)} entries for user {user_id}")
    return jsonify([log.to_dict() for log in logs]), 200