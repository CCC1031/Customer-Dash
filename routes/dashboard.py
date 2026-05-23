from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

def get_models():
    """Get model classes from current app"""
    return {
        'User': current_app.User,
        'Machine': current_app.Machine,
        'Revenue': current_app.Revenue,
        'SupportTicket': current_app.SupportTicket,
        'Activity': current_app.Activity,
        'Inventory': current_app.Inventory,
    }

def get_db():
    """Get db instance from current app"""
    return current_app.extensions['sqlalchemy'].db

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """Get dashboard overview with key metrics"""
    db = get_db()
    models = get_models()
    User = models['User']
    Machine = models['Machine']
    Revenue = models['Revenue']
    SupportTicket = models['SupportTicket']
    Activity = models['Activity']
    Inventory = models['Inventory']
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    
    # Get machines
    machines = Machine.query.filter_by(customer_id=customer_id).all()
    total_machines = len(machines)
    online_machines = len([m for m in machines if m.status == 'online'])
    
    # Calculate total revenue (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    revenue_data = db.session.query(func.sum(Revenue.total_revenue)).filter(
        Revenue.machine_id.in_([m.id for m in machines]),
        Revenue.created_at >= thirty_days_ago
    ).scalar() or 0.0
    
    # Get low stock alerts
    low_stock_items = Inventory.query.filter(
        Inventory.machine_id.in_([m.id for m in machines]),
        Inventory.status.in_(['low_stock', 'out_of_stock'])
    ).count()
    
    # Get open support tickets
    open_tickets = SupportTicket.query.filter(
        SupportTicket.customer_id == customer_id,
        SupportTicket.status.in_(['open', 'in_progress'])
    ).count()
    
    # Get recent activities
    recent_activities = Activity.query.filter(
        Activity.machine_id.in_([m.id for m in machines])
    ).order_by(Activity.created_at.desc()).limit(10).all()
    
    return jsonify({
        'total_machines': total_machines,
        'online_machines': online_machines,
        'revenue_30_days': revenue_data,
        'low_stock_alerts': low_stock_items,
        'open_tickets': open_tickets,
        'recent_activities': [activity.to_dict() for activity in recent_activities]
    }), 200

@dashboard_bp.route('/revenue-summary', methods=['GET'])
@jwt_required()
def get_revenue_summary():
    """Get revenue summary for the last 30 days"""
    models = get_models()
    User = models['User']
    Machine = models['Machine']
    Revenue = models['Revenue']
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    machines = Machine.query.filter_by(customer_id=customer_id).all()
    machine_ids = [m.id for m in machines]
    
    # Get revenue data for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    revenue_records = Revenue.query.filter(
        Revenue.machine_id.in_(machine_ids),
        Revenue.created_at >= thirty_days_ago
    ).all()
    
    # Group by date
    daily_revenue = {}
    for record in revenue_records:
        date_str = record.date.isoformat()
        if date_str not in daily_revenue:
            daily_revenue[date_str] = 0.0
        daily_revenue[date_str] += record.total_revenue
    
    # Sort by date
    sorted_revenue = sorted(daily_revenue.items())
    
    return jsonify({
        'daily_revenue': [{'date': date, 'revenue': revenue} for date, revenue in sorted_revenue],
        'total_revenue': sum([r[1] for r in sorted_revenue])
    }), 200

@dashboard_bp.route('/machine-status', methods=['GET'])
@jwt_required()
def get_machine_status():
    """Get status of all machines"""
    models = get_models()
    User = models['User']
    Machine = models['Machine']
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    machines = Machine.query.filter_by(customer_id=customer_id).all()
    
    machine_statuses = []
    for machine in machines:
        machine_statuses.append({
            'id': machine.id,
            'machine_id': machine.machine_id,
            'location': machine.location,
            'status': machine.status,
            'inventory_percentage': machine.inventory_percentage,
            'monthly_revenue': machine.monthly_revenue,
            'last_restock': machine.last_restock.isoformat() if machine.last_restock else None
        })
    
    return jsonify({'machines': machine_statuses}), 200
