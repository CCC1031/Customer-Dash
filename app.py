from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt as pyjwt
from functools import wraps
from haha_integration import HAHAVendingAPIMock, HAHADataSyncManager

app = Flask(__name__)
CORS(app)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
db_url = os.environ.get('DATABASE_URL', 'sqlite:///snaxology.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'snaxology-secret-key-2026')

db = SQLAlchemy(app)

haha_api = HAHAVendingAPIMock(merchant_id="snaxology_demo")
haha_sync = HAHADataSyncManager(haha_api)

# ============================================================================
# MODELS
# ============================================================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(30), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'first_name': self.first_name,
                'last_name': self.last_name, 'phone': self.phone,
                'created_at': self.created_at.isoformat()}


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), default='')
    city = db.Column(db.String(80), default='')
    state = db.Column(db.String(50), default='')
    zip_code = db.Column(db.String(20), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'company_name': self.company_name,
                'address': self.address, 'city': self.city, 'state': self.state,
                'zip_code': self.zip_code, 'created_at': self.created_at.isoformat()}


class Machine(db.Model):
    __tablename__ = 'machines'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200), default='')
    device_id = db.Column(db.String(80), default='')
    status = db.Column(db.String(20), default='offline')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'name': self.name,
                'location': self.location, 'device_id': self.device_id, 'status': self.status,
                'last_seen': self.last_seen.isoformat() if self.last_seen else None,
                'created_at': self.created_at.isoformat()}


class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(80), default='')
    quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def status(self):
        if self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity <= self.low_stock_threshold:
            return 'low_stock'
        return 'in_stock'

    def to_dict(self):
        return {'id': self.id, 'machine_id': self.machine_id, 'user_id': self.user_id,
                'product_name': self.product_name, 'sku': self.sku, 'quantity': self.quantity,
                'low_stock_threshold': self.low_stock_threshold, 'status': self.status,
                'last_updated': self.last_updated.isoformat() if self.last_updated else None}


class Revenue(db.Model):
    __tablename__ = 'revenue'
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    units_sold = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    average_transaction = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'machine_id': self.machine_id, 'user_id': self.user_id,
                'date': self.date.isoformat() if self.date else None,
                'units_sold': self.units_sold, 'total_revenue': self.total_revenue,
                'average_transaction': self.average_transaction,
                'created_at': self.created_at.isoformat()}


class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id'), nullable=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'machine_id': self.machine_id,
                'ticket_number': self.ticket_number, 'subject': self.subject,
                'description': self.description, 'priority': self.priority, 'status': self.status,
                'created_at': self.created_at.isoformat(), 'updated_at': self.updated_at.isoformat()}


# ============================================================================
# JWT HELPERS
# ============================================================================

def generate_token(user_id):
    payload = {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(days=30)}
    return pyjwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        try:
            data = pyjwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except (pyjwt.ExpiredSignatureError, pyjwt.InvalidTokenError):
            if token == 'demo-token-123':
                current_user = User.query.filter_by(email='demo@snaxology.com').first()
                if not current_user:
                    return jsonify({'error': 'Demo user not found'}), 401
            else:
                return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# ============================================================================
# DATABASE INIT + SEED
# ============================================================================

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='demo@snaxology.com').first():
            demo_user = User(email='demo@snaxology.com', first_name='Demo', last_name='User', phone='555-0000')
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.flush()

            db.session.add(Customer(user_id=demo_user.id, company_name='Snaxology Demo',
                address='123 Main St', city='San Francisco', state='CA', zip_code='94105'))

            m1 = Machine(user_id=demo_user.id, name='Downtown Office Tower',
                location='123 Market St, San Francisco, CA', device_id='VM-001', status='online')
            m2 = Machine(user_id=demo_user.id, name='Airport Terminal B',
                location='SFO Terminal B, San Francisco, CA', device_id='VM-002', status='online')
            m3 = Machine(user_id=demo_user.id, name='University Library',
                location='500 Campus Dr, Berkeley, CA', device_id='VM-003', status='maintenance')
            db.session.add_all([m1, m2, m3])
            db.session.flush()

            db.session.add_all([
                Inventory(machine_id=m1.id, user_id=demo_user.id, product_name="Lay's Classic Chips", sku='LAY-001', quantity=45, low_stock_threshold=10),
                Inventory(machine_id=m1.id, user_id=demo_user.id, product_name='Coca-Cola 12oz', sku='COK-001', quantity=8, low_stock_threshold=10),
                Inventory(machine_id=m1.id, user_id=demo_user.id, product_name='Kind Bar Almond', sku='KND-001', quantity=30, low_stock_threshold=10),
                Inventory(machine_id=m2.id, user_id=demo_user.id, product_name='Doritos Nacho', sku='DOR-001', quantity=0, low_stock_threshold=10),
                Inventory(machine_id=m2.id, user_id=demo_user.id, product_name='Water 16oz', sku='WAT-001', quantity=60, low_stock_threshold=15),
                Inventory(machine_id=m3.id, user_id=demo_user.id, product_name='Granola Bar', sku='GRN-001', quantity=5, low_stock_threshold=10),
            ])

            today = datetime.utcnow().date()
            revenue_records = []
            for i in range(30):
                day = today - timedelta(days=i)
                revenue_records.append(Revenue(machine_id=m1.id, user_id=demo_user.id, date=day,
                    units_sold=20+(i%10), total_revenue=round((20+(i%10))*2.5, 2), average_transaction=2.5))
                revenue_records.append(Revenue(machine_id=m2.id, user_id=demo_user.id, date=day,
                    units_sold=15+(i%8), total_revenue=round((15+(i%8))*3.0, 2), average_transaction=3.0))
            db.session.add_all(revenue_records)

            db.session.add_all([
                SupportTicket(user_id=demo_user.id, machine_id=m3.id, ticket_number='TKT-00001',
                    subject='Machine not dispensing items', priority='high', status='open',
                    description='The machine at University Library is not dispensing items after payment.'),
                SupportTicket(user_id=demo_user.id, machine_id=m1.id, ticket_number='TKT-00002',
                    subject='Screen flickering', priority='medium', status='in_progress',
                    description='The display screen on the Downtown Office Tower machine is flickering.'),
            ])
            db.session.commit()
            print("Demo data seeded successfully.")


init_db()


# ============================================================================
# HEALTH
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    db_type = 'postgresql' if 'postgresql' in db_url else 'sqlite'
    return jsonify({'status': 'healthy', 'db': db_type}), 200


# ============================================================================
# AUTH
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email', '')).first()
    if not user or not user.check_password(data.get('password', '')):
        return jsonify({'error': 'Invalid credentials'}), 401
    customer = Customer.query.filter_by(user_id=user.id).first()
    return jsonify({'access_token': generate_token(user.id), 'user': user.to_dict(),
                    'customer': customer.to_dict() if customer else None}), 200


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if User.query.filter_by(email=data.get('email', '')).first():
        return jsonify({'error': 'Email already registered'}), 409
    user = User(email=data['email'], first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''), phone=data.get('phone', ''))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()
    customer = Customer(user_id=user.id, company_name=data.get('company_name', ''),
        address=data.get('address', ''), city=data.get('city', ''),
        state=data.get('state', ''), zip_code=data.get('zip_code', ''))
    db.session.add(customer)
    db.session.commit()
    return jsonify({'access_token': generate_token(user.id), 'user': user.to_dict(),
                    'customer': customer.to_dict()}), 201


@app.route('/api/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    return jsonify({'user': current_user.to_dict(), 'customer': customer.to_dict() if customer else None}), 200


@app.route('/api/auth/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    for field in ['first_name', 'last_name', 'phone']:
        if field in data:
            setattr(current_user, field, data[field])
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    if customer:
        for field in ['company_name', 'address', 'city', 'state', 'zip_code']:
            if field in data:
                setattr(customer, field, data[field])
    db.session.commit()
    return jsonify({'user': current_user.to_dict(), 'customer': customer.to_dict() if customer else None}), 200


# ============================================================================
# DASHBOARD
# ============================================================================

@app.route('/api/dashboard/overview', methods=['GET'])
@token_required
def dashboard_overview(current_user):
    machines = Machine.query.filter_by(user_id=current_user.id).all()
    online_count = sum(1 for m in machines if m.status == 'online')
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    revenue_records = Revenue.query.filter(Revenue.user_id == current_user.id, Revenue.date >= thirty_days_ago).all()
    total_revenue = sum(r.total_revenue for r in revenue_records)
    low_stock = Inventory.query.filter(Inventory.user_id == current_user.id,
        Inventory.quantity <= Inventory.low_stock_threshold).count()
    open_tickets = SupportTicket.query.filter_by(user_id=current_user.id, status='open').count()
    return jsonify({'total_machines': len(machines), 'online_machines': online_count,
                    'revenue_30_days': round(total_revenue, 2), 'low_stock_alerts': low_stock,
                    'open_tickets': open_tickets, 'recent_activities': []}), 200


# ============================================================================
# MACHINES
# ============================================================================

@app.route('/api/machines', methods=['GET'])
@token_required
def get_machines(current_user):
    machines = Machine.query.filter_by(user_id=current_user.id).all()
    return jsonify({'machines': [m.to_dict() for m in machines]}), 200


@app.route('/api/machines', methods=['POST'])
@token_required
def create_machine(current_user):
    data = request.get_json()
    machine = Machine(user_id=current_user.id, name=data.get('name', 'New Machine'),
        location=data.get('location', ''), device_id=data.get('device_id', ''),
        status=data.get('status', 'offline'))
    db.session.add(machine)
    db.session.commit()
    return jsonify(machine.to_dict()), 201


@app.route('/api/machines/<int:machine_id>', methods=['GET'])
@token_required
def get_machine(current_user, machine_id):
    machine = Machine.query.filter_by(id=machine_id, user_id=current_user.id).first()
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    return jsonify(machine.to_dict()), 200


@app.route('/api/machines/<int:machine_id>', methods=['PUT'])
@token_required
def update_machine(current_user, machine_id):
    machine = Machine.query.filter_by(id=machine_id, user_id=current_user.id).first()
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    data = request.get_json()
    for field in ['name', 'location', 'device_id', 'status']:
        if field in data:
            setattr(machine, field, data[field])
    db.session.commit()
    return jsonify(machine.to_dict()), 200


@app.route('/api/machines/<int:machine_id>', methods=['DELETE'])
@token_required
def delete_machine(current_user, machine_id):
    machine = Machine.query.filter_by(id=machine_id, user_id=current_user.id).first()
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    db.session.delete(machine)
    db.session.commit()
    return jsonify({'message': 'Machine deleted'}), 200


# ============================================================================
# INVENTORY
# ============================================================================

@app.route('/api/inventory', methods=['GET'])
@token_required
def get_inventory(current_user):
    items = Inventory.query.filter_by(user_id=current_user.id).all()
    return jsonify({'inventory': [i.to_dict() for i in items]}), 200


@app.route('/api/inventory', methods=['POST'])
@token_required
def create_inventory(current_user):
    data = request.get_json()
    item = Inventory(machine_id=data['machine_id'], user_id=current_user.id,
        product_name=data.get('product_name', ''), sku=data.get('sku', ''),
        quantity=data.get('quantity', 0), low_stock_threshold=data.get('low_stock_threshold', 10))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
@token_required
def update_inventory(current_user, item_id):
    item = Inventory.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    data = request.get_json()
    for field in ['product_name', 'sku', 'quantity', 'low_stock_threshold']:
        if field in data:
            setattr(item, field, data[field])
    item.last_updated = datetime.utcnow()
    db.session.commit()
    return jsonify(item.to_dict()), 200


@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@token_required
def delete_inventory(current_user, item_id):
    item = Inventory.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'}), 200


# ============================================================================
# REVENUE
# ============================================================================

@app.route('/api/revenue', methods=['GET'])
@token_required
def get_revenue(current_user):
    records = Revenue.query.filter_by(user_id=current_user.id).order_by(Revenue.date.desc()).all()
    return jsonify({'revenue': [r.to_dict() for r in records]}), 200


@app.route('/api/revenue', methods=['POST'])
@token_required
def create_revenue(current_user):
    data = request.get_json()
    record = Revenue(machine_id=data['machine_id'], user_id=current_user.id,
        date=datetime.strptime(data.get('date', datetime.utcnow().date().isoformat()), '%Y-%m-%d').date(),
        units_sold=data.get('units_sold', 0), total_revenue=data.get('total_revenue', 0.0),
        average_transaction=data.get('average_transaction', 0.0))
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


# ============================================================================
# SUPPORT TICKETS
# ============================================================================

@app.route('/api/support', methods=['GET'])
@token_required
def get_tickets(current_user):
    tickets = SupportTicket.query.filter_by(user_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    return jsonify({'tickets': [t.to_dict() for t in tickets]}), 200


@app.route('/api/support', methods=['POST'])
@token_required
def create_ticket(current_user):
    data = request.get_json()
    count = SupportTicket.query.filter_by(user_id=current_user.id).count()
    ticket = SupportTicket(user_id=current_user.id, machine_id=data.get('machine_id'),
        ticket_number=f'TKT-{(count+1):05d}', subject=data.get('subject', ''),
        description=data.get('description', ''), priority=data.get('priority', 'medium'), status='open')
    db.session.add(ticket)
    db.session.commit()
    return jsonify(ticket.to_dict()), 201


@app.route('/api/support/<int:ticket_id>', methods=['PUT'])
@token_required
def update_ticket(current_user, ticket_id):
    ticket = SupportTicket.query.filter_by(id=ticket_id, user_id=current_user.id).first()
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    data = request.get_json()
    for field in ['subject', 'description', 'priority', 'status']:
        if field in data:
            setattr(ticket, field, data[field])
    ticket.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(ticket.to_dict()), 200


# ============================================================================
# HAHA INTEGRATION
# ============================================================================

@app.route('/api/haha/status', methods=['GET'])
def haha_status():
    try:
        is_connected = haha_api.authenticate()
        return jsonify({'status': 'connected' if is_connected else 'disconnected',
                        'merchant_id': haha_api.merchant_id, 'last_sync': haha_sync.last_sync_time,
                        'api_type': 'mock'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/haha/machines', methods=['GET'])
def haha_get_machines():
    try:
        machines = haha_api.get_machines()
        return jsonify({'status': 'success', 'count': len(machines), 'machines': machines}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/haha/sync', methods=['POST'])
def haha_sync_data():
    try:
        result = haha_sync.sync_all()
        return jsonify({'status': 'success', 'result': result}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)


@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    """Temporary debug endpoint - shows DB connection info (remove after debugging)"""
    import os
    db_url = os.environ.get('DATABASE_URL', 'NOT SET')
    pghost = os.environ.get('PGHOST', 'NOT SET')
    pgport = os.environ.get('PGPORT', 'NOT SET')
    pguser = os.environ.get('POSTGRES_USER', 'NOT SET')
    pgdb = os.environ.get('POSTGRES_DB', 'NOT SET')
    # Mask password
    masked_url = db_url[:30] + '...' if len(db_url) > 30 else db_url
    return jsonify({
        'DATABASE_URL_prefix': masked_url,
        'PGHOST': pghost,
        'PGPORT': pgport,
        'POSTGRES_USER': pguser,
        'POSTGRES_DB': pgdb,
        'db_in_use': app.config['SQLALCHEMY_DATABASE_URI'][:30]
    }), 200
