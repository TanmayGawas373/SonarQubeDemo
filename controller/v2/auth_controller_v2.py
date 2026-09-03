# controller/v2/auth_controller_v2.py
"""
v2 Authentication API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify, make_response
from service.auth_service import register_user, authenticate_user, verify_otp, resend_otp
from flask_login import login_user, logout_user as flask_logout, login_required, current_user
from utils.jwt_util import create_access_token, decode_token, jwt_required

auth_v2_bp = Blueprint('auth_v2', __name__, url_prefix='/api/v2/auth')


@auth_v2_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    try:
        user, msg = register_user(data)
        return jsonify({
            'message': msg,
            'email': user.email
        }), 201
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@auth_v2_bp.route('/verify-otp', methods=['POST'])
def verify_otp_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({'error': 'Email and OTP required'}), 400
    
    try:
        user, msg = verify_otp(email, otp)
        return jsonify({
            'message': msg,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
        }), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@auth_v2_bp.route('/resend-otp', methods=['POST'])
def resend_otp_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    try:
        user, msg = resend_otp(email)
        return jsonify({
            'message': msg
        }), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@auth_v2_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    user = authenticate_user(data)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    login_user(user)
    token = create_access_token(
        user_id=user.id,
        role=user.role,
        email=user.email
    )
    
    response = make_response(jsonify({
        'message': 'Logged in',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'role': user.role
        }
    }))
    response.set_cookie(
        'access_token',
        token,
        httponly=True,
        secure=False,
        samesite='Lax'
    )
    return response, 200


@auth_v2_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    flask_logout()
    response = make_response(jsonify({'message': 'Logged out'}))
    response.delete_cookie('access_token')
    return response, 200


@auth_v2_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    from dao.user_dao import get_user_by_id
    from flask import g
    user_id = g.current_user.get('sub')
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': user.role
    }), 200