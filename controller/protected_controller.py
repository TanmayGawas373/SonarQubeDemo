from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from utils.role import role_required

protected_bp = Blueprint('protected', __name__)

@protected_bp.route('/protected', methods=['GET'])
@login_required
def protected_route():
    if not getattr(current_user, 'role', None):
        return jsonify({'error': 'Role not set'}), 403
    return jsonify({'message': f'Protected route accessed by {current_user.role}'}), 200

@protected_bp.route('/admin-only', methods=['GET'])
@login_required
@role_required('admin')
def admin_only_route():
    return jsonify({'message': 'Hello admin'}), 200
