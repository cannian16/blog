from flask import Blueprint, request, jsonify
import jwt
import os
import time
from app.utils.decorators import token_required


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    from app.services.auth import verify_admin
    is_vail, error_response = verify_admin(username, password)

    if not is_vail:
        return jsonify(error_response[0]), error_response[1]
    
    jwt_token = jwt.encode({"admin": True, "iat": int(time.time()), "exp": int(time.time()) + 86400 * 30}, os.getenv('SECRET_KEY'), algorithm="HS256")

    return jsonify({"token": jwt_token}), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def is_auth():
    return jsonify({
        "username": os.getenv("ADMIN_USERNAME"),
        "avatar_url": "https://vip.123pan.cn/1826899604/yk6baz03t0m000d7w33girwfizdpc39iDIYvAqY2BIQOAcx1AdFy.jpg", 
        "role": "admin"
    }), 200