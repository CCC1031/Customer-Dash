from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from models import User, Machine, Revenue
from datetime import datetime, timedelta
from sqlalchemy import func

revenue_bp = Blueprint('revenue', __name__)

@revenue_bp.route('/machine/<int:machine_id>', methods=['GET'])
@jwt_required()
def get_machine_revenue(machine_id):
    """Get revenue data for a specific machine"""
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
    
    # Get revenue for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    revenue_records = Revenue.query.filter(
        Revenue.machine_id == machine_id,
        Revenue.created_at >= thirty_days_ago
    ).order_by(Revenue.date.desc()).all()
    
    total_revenue = sum([r.total_revenue for r in revenue_records])
    total_units = sum([r.units_sold for r in revenue_records])
    
    return jsonify({
        'machine_id': machine_id,
        'revenue_records': [record.to_dict() for record in revenue_records],
        'total_revenue': total_revenue,
        'total_units_sold': total_units,
        'average_revenue_per_day': total_revenue / 30 if revenue_records else 0.0
    }), 200

@revenue_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_revenue():
    """Get aggregated revenue for all machines"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    machines = Machine.query.filter_by(customer_id=customer_id).all()
    machine_ids = [m.id for m in machines]
    
    # Get revenue for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    revenue_records = Revenue.query.filter(
        Revenue.machine_id.in_(machine_ids),
        Revenue.created_at >= thirty_days_ago
    ).order_by(Revenue.date.desc()).all()
    
    # Group by date
    daily_revenue = {}
    for record in revenue_records:
        date_str = record.date.isoformat()
        if date_str not in daily_revenue:
            daily_revenue[date_str] = {'revenue': 0.0, 'units': 0}
        daily_revenue[date_str]['revenue'] += record.total_revenue
        daily_revenue[date_str]['units'] += record.units_sold
    
    # Sort by date
    sorted_revenue = sorted(daily_revenue.items())
    
    total_revenue = sum([r[1]['revenue'] for r in sorted_revenue])
    total_units = sum([r[1]['units'] for r in sorted_revenue])
    
    return jsonify({
        'daily_revenue': [{'date': date, 'revenue': data['revenue'], 'units': data['units']} 
                         for date, data in sorted_revenue],
        'total_revenue': total_revenue,
        'total_units_sold': total_units,
        'average_revenue_per_day': total_revenue / 30 if sorted_revenue else 0.0,
        'machine_count': len(machines)
    }), 200

@revenue_bp.route('/', methods=['POST'])
@jwt_required()
def create_revenue_record():
    """Create a new revenue record"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.get_json()
    
    required_fields = ['machine_id', 'date', 'units_sold', 'total_revenue']
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
        revenue = Revenue(
            machine_id=data['machine_id'],
            date=datetime.fromisoformat(data['date']).date(),
            units_sold=data['units_sold'],
            total_revenue=data['total_revenue'],
            average_transaction=data.get('average_transaction', data['total_revenue'] / data['units_sold'] if data['units_sold'] > 0 else 0.0)
        )
        db.session.add(revenue)
        db.session.commit()
        
        return jsonify({
            'message': 'Revenue record created successfully',
            'record': revenue.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@revenue_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_revenue_summary():
    """Get revenue summary by machine"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    machines = Machine.query.filter_by(customer_id=customer_id).all()
    
    machine_summaries = []
    for machine in machines:
        # Get revenue for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        revenue_records = Revenue.query.filter(
            Revenue.machine_id == machine.id,
            Revenue.created_at >= thirty_days_ago
        ).all()
        
        total_revenue = sum([r.total_revenue for r in revenue_records])
        total_units = sum([r.units_sold for r in revenue_records])
        
        machine_summaries.append({
            'machine_id': machine.id,
            'machine_name': machine.machine_id,
            'location': machine.location,
            'total_revenue': total_revenue,
            'total_units_sold': total_units,
            'average_revenue_per_day': total_revenue / 30 if revenue_records else 0.0
        })
    
    # Sort by revenue descending
    machine_summaries.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    return jsonify({
        'machine_summaries': machine_summaries,
        'total_network_revenue': sum([m['total_revenue'] for m in machine_summaries])
    }), 200
