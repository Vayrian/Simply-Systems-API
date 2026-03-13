from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models.user import User

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/user/profile', methods=['GET', 'PATCH'])
@jwt_required()
def user_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if request.method == 'GET':
        print(f"[PROFILE GET] Fetched for user {user_id}")
        return jsonify({
            "id": user.id,
            "email": user.email,
            "is_system_owner": user.is_system_owner,
            "display_name": user.display_name,
            "current_fronter_id": user.current_fronter_id,
            "front_start_time": user.front_start_time.isoformat() if user.front_start_time else None
        }), 200

    if request.method == 'PATCH':
        if not request.is_json:
            return jsonify({"error": "JSON required"}), 400

        data = request.get_json()
        print(f"[PROFILE PATCH] Data for user {user_id}: {data}")

        if 'is_system_owner' in data:
            user.is_system_owner = bool(data['is_system_owner'])
        if 'display_name' in data:
            user.display_name = data['display_name'].strip() if data['display_name'] else None

        db.session.commit()
        print(f"[SUCCESS] Profile updated for user {user_id}")

        return jsonify({
            "is_system_owner": user.is_system_owner,
            "display_name": user.display_name
        }), 200