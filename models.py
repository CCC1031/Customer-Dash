from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Import db will be done after app initialization
# This prevents circular imports

def get_db():
    """Get db instance from app context"""
    from flask import current_app
    return current_app.extensions.get('sqlalchemy').db

class User:
    """User model - will be created after db initialization"""
    pass

class Customer:
    """Customer model - will be created after db initialization"""
    pass

class Machine:
    """Machine model - will be created after db initialization"""
    pass

class Inventory:
    """Inventory model - will be created after db initialization"""
    pass

class Revenue:
    """Revenue model - will be created after db initialization"""
    pass

class SupportTicket:
    """Support Ticket model - will be created after db initialization"""
    pass

class Activity:
    """Activity model - will be created after db initialization"""
    pass


def create_models(db):
    """Create all model classes with db instance"""
    
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        first_name = db.Column(db.String(120), nullable=False)
        last_name = db.Column(db.String(120), nullable=False)
        phone = db.Column(db.String(20))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        customer = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
        
        def set_password(self, password):
            self.password_hash = generate_password_hash(password)
        
        def check_password(self, password):
            return check_password_hash(self.password_hash, password)
        
        def to_dict(self):
            return {
                'id': self.id,
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'phone': self.phone,
                'created_at': self.created_at.isoformat() if self.created_at else None,
            }

    class Customer(db.Model):
        __tablename__ = 'customers'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        company_name = db.Column(db.String(255), nullable=False)
        haha_merchant_id = db.Column(db.String(255))
        address = db.Column(db.String(255))
        city = db.Column(db.String(120))
        state = db.Column(db.String(50))
        zip_code = db.Column(db.String(20))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        machines = db.relationship('Machine', backref='customer', cascade='all, delete-orphan')
        support_tickets = db.relationship('SupportTicket', backref='customer', cascade='all, delete-orphan')
        
        def to_dict(self):
            return {
                'id': self.id,
                'company_name': self.company_name,
                'address': self.address,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code,
                'created_at': self.created_at.isoformat() if self.created_at else None,
            }

    class Machine(db.Model):
        __tablename__ = 'machines'
        
        id = db.Column(db.Integer, primary_key=True)
        customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
        machine_id = db.Column(db.String(120), nullable=False)
        haha_device_id = db.Column(db.String(255))
        location = db.Column(db.String(255), nullable=False)
        status = db.Column(db.String(50), default='online')
        inventory_percentage = db.Column(db.Float, default=100.0)
        monthly_revenue = db.Column(db.Float, default=0.0)
        last_restock = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        # Relationships
        inventory_items = db.relationship('Inventory', backref='machine', cascade='all, delete-orphan')
        revenue_records = db.relationship('Revenue', backref='machine', cascade='all, delete-orphan')
        support_tickets = db.relationship('SupportTicket', backref='machine', cascade='all, delete-orphan')
        activities = db.relationship('Activity', backref='machine', cascade='all, delete-orphan')
        
        def to_dict(self):
            return {
                'id': self.id,
                'machine_id': self.machine_id,
                'location': self.location,
                'status': self.status,
                'inventory_percentage': self.inventory_percentage,
                'monthly_revenue': self.monthly_revenue,
                'last_restock': self.last_restock.isoformat() if self.last_restock else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
            }

    class Inventory(db.Model):
        __tablename__ = 'inventory'
        
        id = db.Column(db.Integer, primary_key=True)
        machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
        product_name = db.Column(db.String(255), nullable=False)
        sku = db.Column(db.String(120))
        quantity = db.Column(db.Integer, default=0)
        low_stock_threshold = db.Column(db.Integer, default=10)
        status = db.Column(db.String(50), default='in_stock')
        last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'machine_id': self.machine_id,
                'product_name': self.product_name,
                'sku': self.sku,
                'quantity': self.quantity,
                'low_stock_threshold': self.low_stock_threshold,
                'status': self.status,
                'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            }

    class Revenue(db.Model):
        __tablename__ = 'revenue'
        
        id = db.Column(db.Integer, primary_key=True)
        machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
        date = db.Column(db.Date, nullable=False)
        units_sold = db.Column(db.Integer, default=0)
        total_revenue = db.Column(db.Float, default=0.0)
        average_transaction = db.Column(db.Float, default=0.0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'machine_id': self.machine_id,
                'date': self.date.isoformat() if self.date else None,
                'units_sold': self.units_sold,
                'total_revenue': self.total_revenue,
                'average_transaction': self.average_transaction,
            }

    class SupportTicket(db.Model):
        __tablename__ = 'support_tickets'
        
        id = db.Column(db.Integer, primary_key=True)
        customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
        machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'))
        ticket_number = db.Column(db.String(120), unique=True, nullable=False)
        subject = db.Column(db.String(255), nullable=False)
        description = db.Column(db.Text, nullable=False)
        status = db.Column(db.String(50), default='open')
        priority = db.Column(db.String(50), default='medium')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        resolved_at = db.Column(db.DateTime)
        
        def to_dict(self):
            return {
                'id': self.id,
                'ticket_number': self.ticket_number,
                'subject': self.subject,
                'description': self.description,
                'status': self.status,
                'priority': self.priority,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            }

    class Activity(db.Model):
        __tablename__ = 'activities'
        
        id = db.Column(db.Integer, primary_key=True)
        machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
        activity_type = db.Column(db.String(120), nullable=False)
        description = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'activity_type': self.activity_type,
                'description': self.description,
                'created_at': self.created_at.isoformat() if self.created_at else None,
            }
    
    return {
        'User': User,
        'Customer': Customer,
        'Machine': Machine,
        'Inventory': Inventory,
        'Revenue': Revenue,
        'SupportTicket': SupportTicket,
        'Activity': Activity,
    }
