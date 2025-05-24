from flask import Blueprint, request, jsonify
from firebase_admin import firestore

fcm_bp = Blueprint('fcm_bp', __name__)

@fcm_bp.route('/fcm-token', methods=['POST'])
def save_fcm_token():
    try:
        data = request.json
        user_id = data.get("user_id")
        fcm_token = data.get("fcm_token")
        user_ref = firestore.client().collection('users').document(user_id)
        
        if not user_ref.get().exists:
            return jsonify({"message": "User not found"}), 404
        user_ref.update({"fcm_token": fcm_token})

    except Exception as e:
     return jsonify({"message": "Error updating token", "details": str(e)}), 500

