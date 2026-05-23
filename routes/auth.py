from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new customer account"""
    from flask import current_app
    User = current_app.User
    Customer = current_app.Customer
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'company_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    try:
        # Create user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone', '')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        # Create customer profile
        customer = Customer(
            user_id=user.id,
            company_name=data['company_name'],
            address=data.get('address', ''),
            city=data.get('city', ''),
            state=data.get('state', ''),
            zip_code=data.get('zip_code', '')
        )
        db.session.add(customer)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Account created successfully',
            'access_token': access_token,
            'user': user.to_dict(),
            'customer': customer.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    User = current_app.User
    Customer = current_app.Customer
    
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    customer = Customer.query.filter_by(user_id=user.id).first()
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict(),
        'customer': customer.to_dict() if customer else None
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    User = current_app.User
    Customer = current_app.Customer
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    customer = Customer.query.filter_by(user_id=user.id).first()
    
    return jsonify({
        'user': user.to_dict(),
        'customer': customer.to_dict() if customer else None
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    from flask import current_app
    User = current_app.User
    Customer = current_app.Customer
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    try:
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        
        user.updated_at = datetime.utcnow()
        
        # Update customer fields
        customer = Customer.query.filter_by(user_id=user.id).first()
        if customer:
            if 'company_name' in data:
                customer.company_name = data['company_name']
            if 'address' in data:
                customer.address = data['address']
            if 'city' in data:
                customer.city = data['city']
            if 'state' in data:
                customer.state = data['state']
            if 'zip_code' in data:
                customer.zip_code = data['zip_code']
            customer.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(),
            'customer': customer.to_dict() if customer else None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout (token invalidation handled by client)"""
    return jsonify({'message': 'Logged out successfully'}), 200
