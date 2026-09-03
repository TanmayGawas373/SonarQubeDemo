from flask import Blueprint, flash, make_response, redirect, request, jsonify, session, render_template, url_for
from service.auth_service import register_user, authenticate_user, logout_user, verify_otp, resend_otp
from flask_login import login_user, logout_user as flask_logout, login_required, current_user

from utils.jwt_util import create_access_token
from utils.logger import log_general_action

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST','GET'])
@auth_bp.route('/auth/register', methods=['POST','GET'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    data = request.get_json(silent=True) or request.form
    is_json = request.is_json or (request.get_json(silent=True) is not None)
    try:
        user, msg = register_user(data)
        if is_json:
            return jsonify({'message': msg, 'email': user.email}), 201
        flash(msg, 'success')
        return redirect(url_for('auth.verify_otp_page', email=user.email))
    except ValueError as exc:
        if is_json:
            return jsonify({'error': str(exc)}), 400
        flash(str(exc), 'error')
        return redirect(url_for('auth.register'))

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
@auth_bp.route('/auth/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    email = request.args.get('email') or request.form.get('email') or session.get('pending_verification_email')
    if request.method == 'GET':
        if not email:
            flash('Please register first', 'error')
            return redirect(url_for('auth.register'))
        session['pending_verification_email'] = email
        return render_template('auth/verify_otp.html', email=email)
    
    data = request.get_json(silent=True) or request.form
    is_json = request.is_json or (request.get_json(silent=True) is not None)
    otp = data.get('otp')
    email = data.get('email') or session.get('pending_verification_email')
    
    if not otp or not email:
        if is_json:
            return jsonify({'error': 'OTP and email required'}), 400
        flash('OTP and email required', 'error')
        return redirect(url_for('auth.verify_otp_page', email=email))
    
    try:
        user, msg = verify_otp(email, otp)
        session.pop('pending_verification_email', None)
        if is_json:
            return jsonify({'message': msg}), 200
        flash(msg, 'success')
        return redirect(url_for('auth.login_jwt'))
    except ValueError as exc:
        if is_json:
            return jsonify({'error': str(exc)}), 400
        flash(str(exc), 'error')
        return redirect(url_for('auth.verify_otp_page', email=email))

@auth_bp.route('/resend-otp', methods=['POST'])
@auth_bp.route('/auth/resend-otp', methods=['POST'])
def resend_otp_route():
    data = request.get_json(silent=True) or request.form
    is_json = request.is_json or (request.get_json(silent=True) is not None)
    email = data.get('email') or session.get('pending_verification_email')
    
    if not email:
        if is_json:
            return jsonify({'error': 'Email required'}), 400
        flash('Email required', 'error')
        return redirect(url_for('auth.register'))
    
    try:
        user, msg = resend_otp(email)
        if is_json:
            return jsonify({'message': msg}), 200
        flash(msg, 'success')
        return redirect(url_for('auth.verify_otp_page', email=email))
    except ValueError as exc:
        if is_json:
            return jsonify({'error': str(exc)}), 400
        flash(str(exc), 'error')
        return redirect(url_for('auth.verify_otp_page', email=email))

@auth_bp.route('/login', methods=['GET','POST'])
@auth_bp.route('/auth/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    data = request.form if request.form else request.get_json()
    try:
        user = authenticate_user(data)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 401
    if user:
        login_user(user)
        from utils.jwt_util import create_access_token
        token = create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email
        )
        log_general_action(f"[OK] User Logged In Successfully with email {user.email}", "info")
        response = make_response(jsonify({'message': 'Logged in', 'token': token}))
        response.set_cookie(
            'access_token',
            token,
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        return response, 200
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/login_jwt', methods=['GET', 'POST'])
@auth_bp.route('/auth/login_jwt', methods=['GET', 'POST'])
def login_jwt():

    if request.method == 'GET':
        return render_template('auth/login.html')

    data = request.get_json(silent=True) or request.form
    is_json = request.is_json or (request.get_json(silent=True) is not None)

    try:
        user = authenticate_user(data)
    except ValueError as exc:
        if is_json:
            return jsonify({'error': str(exc)}), 401
        flash(str(exc), 'error')
        return redirect(url_for('auth.login_jwt'))

    if not user:
        if is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        flash('Invalid credentials', 'error')
        return redirect(url_for('auth.login_jwt'))

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        email=user.email
    )

    if is_json:
        return jsonify({'token': token}), 200

    response = make_response(
        redirect(url_for('dashboard.home'))
    )

    response.set_cookie(
        'access_token',
        token,
        httponly=True,
        secure=False,
        samesite='Lax'
    )

    return response


@auth_bp.route('/logout', methods=['POST'])
@auth_bp.route('/auth/logout', methods=['POST'])
def logout():

    response = make_response(redirect(url_for('auth.login_jwt')))

    response.delete_cookie('access_token')

    return response