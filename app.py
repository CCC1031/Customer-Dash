from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
from haha_integration import HAHAVendingAPIMock, HAHADataSyncManager

app = Flask(__name__)
CORS(app)

# Initialize HAHA API (using mock for demo)
haha_api = HAHAVendingAPIMock(merchant_id="snaxology_demo")
haha_sync = HAHADataSyncManager(haha_api)

# In-memory data store for testing
data_store = {
    'users': {},
    'customers': {},
    'machines': {},
    'inventory': {},
    'revenue': {},
    'tickets': {},
    'haha_sync_log': []
}

# Demo user
demo_user = {
    'id': 1,
    'email': 'demo@snaxology.com',
    'password': 'demo123',
    'first_name': 'Demo',
    'last_name': 'User',
    'phone': '555-0000',
    'created_at': datetime.utcnow().isoformat()
}

demo_customer = {
    'id': 1,
    'user_id': 1,
    'company_name': 'Snaxology Demo',
    'address': '123 Main St',
    'city': 'San Francisco',
    'state': 'CA',
    'zip_code': '94105',
    'created_at': datetime.utcnow().isoformat()
}

data_store['users'][1] = demo_user
data_store['customers'][1] = demo_customer

# ============================================================================
# BASIC ENDPOINTS (from previous implementation)
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('email') == 'demo@snaxology.com' and data.get('password') == 'demo123':
        return jsonify({
            'access_token': 'demo-token-123',
            'user': demo_user,
            'customer': demo_customer
        }), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    user_id = len(data_store['users']) + 1
    new_user = {
        'id': user_id,
        'email': data.get('email'),
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'phone': data.get('phone', ''),
        'created_at': datetime.utcnow().isoformat()
    }
    new_customer = {
        'id': user_id,
        'user_id': user_id,
        'company_name': data.get('company_name'),
        'address': data.get('address', ''),
        'city': data.get('city', ''),
        'state': data.get('state', ''),
        'zip_code': data.get('zip_code', ''),
        'created_at': datetime.utcnow().isoformat()
    }
    data_store['users'][user_id] = new_user
    data_store['customers'][user_id] = new_customer
    return jsonify({
        'access_token': f'token-{user_id}',
        'user': new_user,
        'customer': new_customer
    }), 201

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    return jsonify({
        'user': demo_user,
        'customer': demo_customer
    }), 200

# ============================================================================
# HAHA INTEGRATION ENDPOINTS
# ============================================================================

@app.route('/api/haha/status', methods=['GET'])
def haha_status():
    """Get HAHA API connection status"""
    try:
        is_connected = haha_api.authenticate()
        return jsonify({
            'status': 'connected' if is_connected else 'disconnected',
            'merchant_id': haha_api.merchant_id,
            'last_sync': haha_sync.last_sync_time,
            'api_type': 'mock' if isinstance(haha_api, HAHAVendingAPIMock) else 'production'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/haha/machines', methods=['GET'])
def haha_get_machines():
    """Get machines from HAHA API"""
    try:
        force_refresh = request.args.get('force', 'false').lower() == 'true'
        machines = haha_api.get_machines(force_refresh=force_refresh)
        
        return jsonify({
            'status': 'success',
            'count': len(machines),
            'machines': machines,
            'last_sync': haha_sync.last_sync_time.get('machines')
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/haha/machines/<device_id>/status', methods=['GET'])
def haha_machine_status(device_id):
    """Get real-time status of a specific machine"""
    try:
        status = haha_api.get_machine_status(device_id)
        return jsonify({
            'status': 'success',
            'device_id': device_id,
            'data': status
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/haha/machines/<device_id>/inventory', methods=['GET'])
def haha_machine_inventory(device_id):
    """Get inventory for a specific machine"""
    try:
        inventory = haha_api.get_machine_inventory(device_id)
        
        # Calculate stock status
        low_stock_count = sum(1 for item in inventory if item.get('quantity', 0) < 10)
        
        return jsonify({
            'status': 'success',
            'device_id': device_id,
            'items': inventory,
            'total_items': len(inventory),
            'low_stock_count': low_stock_count
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/haha/machines/<device_id>/revenue', methods=['GET'])
def haha_machine_revenue(device_id):
    """Get revenue data for a specific machine"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        revenue = haha_api.get_machine_revenue(device_id, start_date, end_date)
        
        # Calculate totals
        total_revenue = sum(r.get('total_revenue', 0) for r in revenue)
        total_units = sum(r.get('units_sold', 0) for r in revenue)
        
        return jsonify({
            'status': 'success',
            'device_id': device_id,
            'records': revenue,
            'total_revenue': total_revenue,
            'total_units_sold': total_units,
            'average_daily_revenue': total_revenue / len(revenue) if revenue else 0
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/haha/revenue', methods=['GET'])
def haha_all_revenue():
    """Get aggregated revenue for all machines"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        revenue = haha_api.get_all_revenue(start_date, end_date)
        
        # Calculate totals
        total_revenue = sum(r.get('total_revenue', 0) for r in revenue)
        total_units = sum(r.get('units_sold', 0) for r in revenue)
        
        return jsonify({
            'status': 'success',
            'records': revenue,
            'total_revenue': total_revenue,
            'total_units_sold': total_units,
            'average_daily_revenue': total_revenue / len(revenue) if revenue else 0
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/haha/sync', methods=['POST'])
def haha_sync_now():
    """Trigger manual data synchronization"""
    try:
        sync_type = request.json.get('sync_type', 'all') if request.json else 'all'
        force = request.json.get('force', False) if request.json else False
        
        if sync_type == 'all':
            results = haha_sync.sync_all(force=force)
        elif sync_type == 'machines':
            success, msg = haha_sync.sync_machines(force=force)
            results = {'machines': (success, msg)}
        else:
            return jsonify({'status': 'error', 'error': 'Invalid sync_type'}), 400
        
        # Log sync
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'sync_type': sync_type,
            'results': {k: {'success': v[0], 'message': v[1]} for k, v in results.items()}
        }
        data_store['haha_sync_log'].append(log_entry)
        
        return jsonify({
            'status': 'success',
            'sync_type': sync_type,
            'results': {k: {'success': v[0], 'message': v[1]} for k, v in results.items()}
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/haha/sync-log', methods=['GET'])
def haha_sync_log():
    """Get sync history"""
    try:
        limit = int(request.args.get('limit', 50))
        log = data_store['haha_sync_log'][-limit:]
        
        return jsonify({
            'status': 'success',
            'count': len(log),
            'log': log
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/haha/dashboard', methods=['GET'])
def haha_dashboard():
    """Get HAHA integration dashboard data"""
    try:
        machines = haha_api.get_machines()
        all_revenue = haha_api.get_all_revenue()
        
        # Calculate metrics
        total_machines = len(machines)
        online_machines = sum(1 for m in machines if m.get('status') == 'online')
        total_revenue = sum(r.get('total_revenue', 0) for r in all_revenue)
        total_units = sum(r.get('units_sold', 0) for r in all_revenue)
        
        # Get inventory status
        total_low_stock = 0
        for machine in machines:
            device_id = machine.get('device_id')
            inventory = haha_api.get_machine_inventory(device_id)
            total_low_stock += sum(1 for item in inventory if item.get('quantity', 0) < 10)
        
        return jsonify({
            'status': 'success',
            'metrics': {
                'total_machines': total_machines,
                'online_machines': online_machines,
                'offline_machines': total_machines - online_machines,
                'total_revenue': total_revenue,
                'total_units_sold': total_units,
                'low_stock_items': total_low_stock,
                'average_revenue_per_machine': total_revenue / total_machines if total_machines > 0 else 0
            },
            'machines': machines,
            'last_sync': haha_sync.last_sync_time
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# ============================================================================
# MACHINES ENDPOINTS
# ============================================================================

@app.route('/api/machines', methods=['GET'])
def get_machines():
    machines = list(data_store['machines'].values())
    return jsonify({'machines': machines}), 200

@app.route('/api/machines', methods=['POST'])
def create_machine():
    data = request.get_json()
    machine_id = len(data_store['machines']) + 1
    new_machine = {
        'id': machine_id,
        'machine_id': data.get('machine_id'),
        'location': data.get('location'),
        'status': data.get('status', 'online'),
        'inventory_percentage': 100.0,
        'monthly_revenue': 0.0,
        'last_restock': None,
        'created_at': datetime.utcnow().isoformat()
    }
    data_store['machines'][machine_id] = new_machine
    return jsonify(new_machine), 201

@app.route('/api/machines/<int:machine_id>', methods=['GET'])
def get_machine(machine_id):
    machine = data_store['machines'].get(machine_id)
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    return jsonify(machine), 200

@app.route('/api/machines/<int:machine_id>', methods=['PUT'])
def update_machine(machine_id):
    data = request.get_json()
    machine = data_store['machines'].get(machine_id)
    if not machine:
        return jsonify({'error': 'Machine not found'}), 404
    machine.update(data)
    return jsonify(machine), 200

@app.route('/api/machines/<int:machine_id>', methods=['DELETE'])
def delete_machine(machine_id):
    if machine_id in data_store['machines']:
        del data_store['machines'][machine_id]
        return jsonify({'message': 'Machine deleted'}), 200
    return jsonify({'error': 'Machine not found'}), 404

# ============================================================================
# INVENTORY ENDPOINTS
# ============================================================================

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    inventory = list(data_store['inventory'].values())
    return jsonify({'inventory': inventory}), 200

@app.route('/api/inventory', methods=['POST'])
def create_inventory():
    data = request.get_json()
    item_id = len(data_store['inventory']) + 1
    new_item = {
        'id': item_id,
        'machine_id': data.get('machine_id'),
        'product_name': data.get('product_name'),
        'sku': data.get('sku', ''),
        'quantity': data.get('quantity', 0),
        'low_stock_threshold': data.get('low_stock_threshold', 10),
        'status': 'in_stock' if data.get('quantity', 0) > data.get('low_stock_threshold', 10) else 'low_stock',
        'last_updated': datetime.utcnow().isoformat()
    }
    data_store['inventory'][item_id] = new_item
    return jsonify(new_item), 201

# ============================================================================
# REVENUE ENDPOINTS
# ============================================================================

@app.route('/api/revenue', methods=['GET'])
def get_revenue():
    revenue = list(data_store['revenue'].values())
    return jsonify({'revenue': revenue}), 200

@app.route('/api/revenue', methods=['POST'])
def create_revenue():
    data = request.get_json()
    record_id = len(data_store['revenue']) + 1
    new_record = {
        'id': record_id,
        'machine_id': data.get('machine_id'),
        'date': data.get('date', datetime.utcnow().date().isoformat()),
        'units_sold': data.get('units_sold', 0),
        'total_revenue': data.get('total_revenue', 0.0),
        'average_transaction': data.get('average_transaction', 0.0),
        'created_at': datetime.utcnow().isoformat()
    }
    data_store['revenue'][record_id] = new_record
    return jsonify(new_record), 201

# ============================================================================
# SUPPORT ENDPOINTS
# ============================================================================

@app.route('/api/support', methods=['GET'])
def get_tickets():
    tickets = list(data_store['tickets'].values())
    return jsonify({'tickets': tickets}), 200

@app.route('/api/support', methods=['POST'])
def create_ticket():
    data = request.get_json()
    ticket_id = len(data_store['tickets']) + 1
    new_ticket = {
        'id': ticket_id,
        'ticket_number': f'TKT-{ticket_id:05d}',
        'subject': data.get('subject'),
        'description': data.get('description'),
        'priority': data.get('priority', 'medium'),
        'status': 'open',
        'machine_id': data.get('machine_id'),
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    data_store['tickets'][ticket_id] = new_ticket
    return jsonify(new_ticket), 201

@app.route('/api/support/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    data = request.get_json()
    ticket = data_store['tickets'].get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    ticket.update(data)
    ticket['updated_at'] = datetime.utcnow().isoformat()
    return jsonify(ticket), 200

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.route('/api/dashboard/overview', methods=['GET'])
def dashboard_overview():
    return jsonify({
        'total_machines': len(data_store['machines']),
        'online_machines': sum(1 for m in data_store['machines'].values() if m['status'] == 'online'),
        'revenue_30_days': 1250.50,
        'low_stock_alerts': 3,
        'open_tickets': 2,
        'recent_activities': []
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
