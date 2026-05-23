from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from models import User, SupportTicket
from datetime import datetime
import uuid

support_bp = Blueprint('support', __name__)

@support_bp.route('/', methods=['GET'])
@jwt_required()
def get_support_tickets():
    """Get all support tickets for the customer"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    tickets = SupportTicket.query.filter_by(customer_id=customer_id).order_by(
        SupportTicket.created_at.desc()
    ).all()
    
    return jsonify({
        'tickets': [ticket.to_dict() for ticket in tickets]
    }), 200

@support_bp.route('/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_support_ticket(ticket_id):
    """Get details of a specific support ticket"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    ticket = SupportTicket.query.filter_by(
        id=ticket_id,
        customer_id=user.customer.id
    ).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    return jsonify(ticket.to_dict()), 200

@support_bp.route('/', methods=['POST'])
@jwt_required()
def create_support_ticket():
    """Create a new support ticket"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.get_json()
    
    required_fields = ['subject', 'description']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Generate unique ticket number
        ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        
        ticket = SupportTicket(
            customer_id=user.customer.id,
            machine_id=data.get('machine_id'),
            ticket_number=ticket_number,
            subject=data['subject'],
            description=data['description'],
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'open')
        )
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({
            'message': 'Support ticket created successfully',
            'ticket': ticket.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@support_bp.route('/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_support_ticket(ticket_id):
    """Update a support ticket"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    ticket = SupportTicket.query.filter_by(
        id=ticket_id,
        customer_id=user.customer.id
    ).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'subject' in data:
            ticket.subject = data['subject']
        if 'description' in data:
            ticket.description = data['description']
        if 'priority' in data:
            ticket.priority = data['priority']
        if 'status' in data:
            ticket.status = data['status']
            # Set resolved_at if status is resolved or closed
            if data['status'] in ['resolved', 'closed'] and not ticket.resolved_at:
                ticket.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket updated successfully',
            'ticket': ticket.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@support_bp.route('/<int:ticket_id>', methods=['DELETE'])
@jwt_required()
def delete_support_ticket(ticket_id):
    """Delete a support ticket"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    ticket = SupportTicket.query.filter_by(
        id=ticket_id,
        customer_id=user.customer.id
    ).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    try:
        db.session.delete(ticket)
        db.session.commit()
        
        return jsonify({'message': 'Ticket deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@support_bp.route('/status/<status>', methods=['GET'])
@jwt_required()
def get_tickets_by_status(status):
    """Get support tickets filtered by status"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    tickets = SupportTicket.query.filter_by(
        customer_id=customer_id,
        status=status
    ).order_by(SupportTicket.created_at.desc()).all()
    
    return jsonify({
        'status': status,
        'tickets': [ticket.to_dict() for ticket in tickets]
    }), 200

@support_bp.route('/priority/<priority>', methods=['GET'])
@jwt_required()
def get_tickets_by_priority(priority):
    """Get support tickets filtered by priority"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    customer_id = user.customer.id
    tickets = SupportTicket.query.filter_by(
        customer_id=customer_id,
        priority=priority
    ).order_by(SupportTicket.created_at.desc()).all()
    
    return jsonify({
        'priority': priority,
        'tickets': [ticket.to_dict() for ticket in tickets]
    }), 200
