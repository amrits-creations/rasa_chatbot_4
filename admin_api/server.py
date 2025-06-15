from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import (AdminAuth, ProductManager, OrderManager, UserManager, 
                 FAQManager, UnansweredQuestionManager, RoleManager)

app = Flask(__name__)
CORS(app)

# Simple session storage
active_sessions = {}

# Create instances of our managers
auth = AdminAuth()
product_manager = ProductManager()
order_manager = OrderManager()
user_manager = UserManager()
faq_manager = FAQManager()
unanswered_manager = UnansweredQuestionManager()
role_manager = RoleManager()

def check_user_session(token):
    """Check if user session is valid"""
    if token in active_sessions:
        return active_sessions[token]
    return None

def check_user_access(user_role, resource):
    """Check if user has access to resource"""
    return auth.check_access(user_role, resource)

# Authentication endpoints
@app.route('/api/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    user_info = auth.verify_admin_user(username, password)

    if user_info:
        session_token = f"{username}_{hash(password)}_{len(active_sessions)}"
        active_sessions[session_token] = user_info

        return jsonify({
            'success': True,
            'token': session_token,
            'user': user_info
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """Admin logout endpoint"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token in active_sessions:
        del active_sessions[token]
    return jsonify({'success': True})

# Product endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'products'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    products = product_manager.get_all()
    return jsonify({'success': True, 'data': products})

@app.route('/api/products', methods=['POST'])
def create_product():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'products'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = product_manager.create(
        data.get('name', ''),
        int(data.get('stock', 0)),
        int(data.get('moq', 1)),
        data.get('quantity_type', 'pcs')
    )
    return jsonify(result)

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'products'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = product_manager.update(
        product_id,
        data.get('name'),
        data.get('stock'),
        data.get('moq'),
        data.get('quantity_type')
    )
    return jsonify(result)

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'products'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    result = product_manager.delete(product_id)
    return jsonify(result)

# Order endpoints
@app.route('/api/orders', methods=['GET'])
def get_orders():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'orders'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    orders = order_manager.get_all()
    return jsonify({'success': True, 'data': orders})

@app.route('/api/orders', methods=['POST'])
def create_order():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'orders'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = order_manager.create(
        int(data.get('user_id', 0)),
        int(data.get('product_id', 0)),
        data.get('status', 'pending'),
        data.get('estimated_delivery')
    )
    return jsonify(result)

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'orders'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = order_manager.update(
        order_id,
        data.get('status'),
        data.get('estimated_delivery')
    )
    return jsonify(result)

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'orders'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    result = order_manager.delete(order_id)
    return jsonify(result)

# User endpoints
@app.route('/api/users', methods=['GET'])
def get_users():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'users'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    users = user_manager.get_all()
    return jsonify({'success': True, 'data': users})

@app.route('/api/users', methods=['POST'])
def create_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'users'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = user_manager.create(
        data.get('username', ''),
        data.get('password', ''),
        data.get('role_name', '')
    )
    return jsonify(result)

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'users'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = user_manager.update(
        user_id,
        data.get('username'),
        data.get('password'),
        data.get('role_name')
    )
    return jsonify(result)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'users'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    result = user_manager.delete(user_id)
    return jsonify(result)

# FAQ endpoints
@app.route('/api/faq', methods=['GET'])
def get_faq():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'faq'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    faqs = faq_manager.get_all()
    return jsonify({'success': True, 'data': faqs})

@app.route('/api/faq', methods=['POST'])
def create_faq():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'faq'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = faq_manager.create(
        data.get('question', ''),
        data.get('answer', '')
    )
    return jsonify(result)

@app.route('/api/faq/<int:faq_id>', methods=['PUT'])
def update_faq(faq_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'faq'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = faq_manager.update(
        faq_id,
        data.get('question'),
        data.get('answer')
    )
    return jsonify(result)

@app.route('/api/faq/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'faq'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    result = faq_manager.delete(faq_id)
    return jsonify(result)

# Unanswered Questions endpoints
@app.route('/api/unanswered', methods=['GET'])
def get_unanswered():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'unanswered'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    questions = unanswered_manager.get_all()
    return jsonify({'success': True, 'data': questions})

@app.route('/api/unanswered/<int:uq_id>', methods=['PUT'])
def update_unanswered(uq_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'unanswered'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = unanswered_manager.update(uq_id, data.get('status'))
    return jsonify(result)

@app.route('/api/unanswered/<int:uq_id>', methods=['DELETE'])
def delete_unanswered(uq_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'unanswered'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    result = unanswered_manager.delete(uq_id)
    return jsonify(result)

# Role endpoints (System Admin only)
@app.route('/api/roles', methods=['GET'])
def get_roles():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'roles'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    roles = role_manager.get_all()
    return jsonify({'success': True, 'data': roles})

@app.route('/api/roles', methods=['POST'])
def create_role():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'roles'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    result = role_manager.create(data.get('role_name', ''))
    return jsonify(result)

@app.route('/api/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user = check_user_session(token)
    
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    if not check_user_access(user['role'], 'roles'):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    result = role_manager.delete(role_id)
    return jsonify(result)

@app.route('/api/user/login', methods=['POST'])
def user_login():
    """Regular user login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Use existing auth but check for End User role
    user_info = auth.verify_user(username, password, allowed_roles=['End User'])
    
    if user_info:
        session_token = f"user_{username}_{hash(password)}_{len(active_sessions)}"
        active_sessions[session_token] = user_info
        return jsonify({'success': True, 'token': session_token, 'user': user_info})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5000)
