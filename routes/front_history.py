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