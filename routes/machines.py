from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from models import User, Machine, Activity

machines_bp = Blueprint('machines', __name__)

@machines_bp.route('/', methods=['GET'])
@jwt_required()
def get_machines():
    """Get all machines for the customer"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    machines = Machine.query.filter_by(customer_id=customer_id).all()
    
    return jsonify({
        'machines': [machine.to_dict() for machine in machines]
    }), 200

@machines_bp.route('/<int:machine_id>', methods=['GET'])
@jwt_required()
def get_machine(machine_id):
    """Get details of a specific machine"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    machine = Machine.query.filter_by(
        id=machine_id,
        customer_id=user.customer.id
    ).first()
    
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    
    return jsonify(machine.to_dict()), 200

@machines_bp.route('/', methods=['POST'])
@jwt_required()
def create_machine():
    """Create a new machine"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.get_json()
    
    required_fields = ['machine_id', 'location']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        machine = Machine(
            customer_id=user.customer.id,
            machine_id=data['machine_id'],
            location=data['location'],
            haha_device_id=data.get('haha_device_id'),
            status=data.get('status', 'online')
        )
        db.session.add(machine)
        db.session.commit()
        
        # Log activity
        activity = Activity(
            machine_id=machine.id,
            activity_type='machine_added',
            description=f'Machine {machine.machine_id} added to inventory'
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Machine created successfully',
            'machine': machine.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@machines_bp.route('/<int:machine_id>', methods=['PUT'])
@jwt_required()
def update_machine(machine_id):
    """Update machine details"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    machine = Machine.query.filter_by(
        id=machine_id,
        customer_id=user.customer.id
    ).first()
    
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'location' in data:
            machine.location = data['location']
        if 'status' in data:
            machine.status = data['status']
        if 'inventory_percentage' in data:
            machine.inventory_percentage = data['inventory_percentage']
        if 'monthly_revenue' in data:
            machine.monthly_revenue = data['monthly_revenue']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Machine updated successfully',
            'machine': machine.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@machines_bp.route('/<int:machine_id>', methods=['DELETE'])
@jwt_required()
def delete_machine(machine_id):
    """Delete a machine"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    machine = Machine.query.filter_by(
        id=machine_id,
        customer_id=user.customer.id
    ).first()
    
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    
    try:
        db.session.delete(machine)
        db.session.commit()
        
        return jsonify({'message': 'Machine deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
