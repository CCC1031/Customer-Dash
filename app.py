from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize extensions without app
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///snaxology_customer.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Create models after db initialization
    from models import create_models
    models = create_models(db)
    
    # Make models available globally
    app.User = models['User']
    app.Customer = models['Customer']
    app.Machine = models['Machine']
    app.Inventory = models['Inventory']
    app.Revenue = models['Revenue']
    app.SupportTicket = models['SupportTicket']
    app.Activity = models['Activity']
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.machines import machines_bp
    from routes.inventory import inventory_bp
    from routes.revenue import revenue_bp
    from routes.support import support_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(machines_bp, url_prefix='/api/machines')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(revenue_bp, url_prefix='/api/revenue')
    app.register_blueprint(support_bp, url_prefix='/api/support')
    
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create app instance for direct execution
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
