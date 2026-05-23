from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from models import User, Machine, Inventory, Activity

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/machine/<int:machine_id>', methods=['GET'])
@jwt_required()
def get_machine_inventory(machine_id):
    """Get inventory for a specific machine"""
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
    
    inventory_items = Inventory.query.filter_by(machine_id=machine_id).all()
    
    return jsonify({
        'machine_id': machine_id,
        'inventory': [item.to_dict() for item in inventory_items]
    }), 200

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_inventory():
    """Get all inventory across all machines"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    machines = Machine.query.filter_by(customer_id=customer_id).all()
    machine_ids = [m.id for m in machines]
    
    inventory_items = Inventory.query.filter(
        Inventory.machine_id.in_(machine_ids)
    ).all()
    
    # Group by machine
    inventory_by_machine = {}
    for item in inventory_items:
        if item.machine_id not in inventory_by_machine:
            inventory_by_machine[item.machine_id] = []
        inventory_by_machine[item.machine_id].append(item.to_dict())
    
    return jsonify({
        'inventory_by_machine': inventory_by_machine
    }), 200

@inventory_bp.route('/<int:item_id>', methods=['GET'])
@jwt_required()
def get_inventory_item(item_id):
    """Get details of a specific inventory item"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    item = Inventory.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    # Verify ownership
    machine = Machine.query.get(item.machine_id)
    if machine.customer_id != user.customer.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(item.to_dict()), 200

@inventory_bp.route('/', methods=['POST'])
@jwt_required()
def create_inventory_item():
    """Add a new inventory item to a machine"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.get_json()
    
    required_fields = ['machine_id', 'product_name', 'sku', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify machine ownership
    machine = Machine.query.filter_by(
        id=data['machine_id'],
        customer_id=user.customer.id
    ).first()
    
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    
    try:
        item = Inventory(
            machine_id=data['machine_id'],
            product_name=data['product_name'],
            sku=data['sku'],
            quantity=data['quantity'],
            low_stock_threshold=data.get('low_stock_threshold', 10),
            status=data.get('status', 'in_stock')
        )
        db.session.add(item)
        db.session.commit()
        
        # Log activity
        activity = Activity(
            machine_id=data['machine_id'],
            activity_type='inventory_added',
            description=f'Added {data["product_name"]} to inventory'
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory item created successfully',
            'item': item.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_inventory_item(item_id):
    """Update an inventory item"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    item = Inventory.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    # Verify ownership
    machine = Machine.query.get(item.machine_id)
    if machine.customer_id != user.customer.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        if 'quantity' in data:
            item.quantity = data['quantity']
        if 'low_stock_threshold' in data:
            item.low_stock_threshold = data['low_stock_threshold']
        if 'status' in data:
            item.status = data['status']
        if 'product_name' in data:
            item.product_name = data['product_name']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory item updated successfully',
            'item': item.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_inventory_item(item_id):
    """Delete an inventory item"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    item = Inventory.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    # Verify ownership
    machine = Machine.query.get(item.machine_id)
    if machine.customer_id != user.customer.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'Inventory item deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_items():
    """Get all low stock or out of stock items"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    machines = Machine.query.filter_by(customer_id=customer_id).all()
    machine_ids = [m.id for m in machines]
    
    low_stock_items = Inventory.query.filter(
        Inventory.machine_id.in_(machine_ids),
        Inventory.status.in_(['low_stock', 'out_of_stock'])
    ).all()
    
    return jsonify({
        'low_stock_items': [item.to_dict() for item in low_stock_items]
    }), 200
