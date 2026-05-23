# Snaxology Customer Portal

A comprehensive customer-facing CRM portal for managing Snaxology vending machines, tracking inventory, viewing revenue reports, and submitting support tickets.

## Features

- **Customer Authentication**: Secure login and registration with JWT tokens
- **Machine Management**: Add, view, and manage vending machines
- **Inventory Tracking**: Real-time inventory monitoring with low-stock alerts
- **Revenue Reports**: Detailed revenue analytics and performance metrics
- **Support Tickets**: Create and track support requests
- **Dashboard**: Real-time overview of key metrics and machine status
- **HAHA API Integration**: Real-time data synchronization with HAHA vending machines

## Tech Stack

### Backend
- **Framework**: Flask 2.3.3
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (Flask-JWT-Extended)
- **API**: RESTful API with CORS support

### Frontend (Coming Soon)
- **Framework**: React 19
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios

## Project Structure

```
snaxology-customer-portal/
├── app.py                 # Flask application entry point
├── models.py              # SQLAlchemy database models
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints
│   ├── dashboard.py      # Dashboard metrics endpoints
│   ├── machines.py       # Machine management endpoints
│   ├── inventory.py      # Inventory tracking endpoints
│   ├── revenue.py        # Revenue reporting endpoints
│   └── support.py        # Support ticket endpoints
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip or conda

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd snaxology-customer-portal
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

6. **Run the development server**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register a new customer
- `POST /api/auth/login` - Login with email and password
- `GET /api/auth/profile` - Get current user profile (requires JWT)
- `PUT /api/auth/profile` - Update user profile (requires JWT)
- `POST /api/auth/logout` - Logout (requires JWT)

### Dashboard
- `GET /api/dashboard/overview` - Get dashboard overview with key metrics
- `GET /api/dashboard/revenue-summary` - Get 30-day revenue summary
- `GET /api/dashboard/machine-status` - Get status of all machines

### Machines
- `GET /api/machines` - Get all machines for the customer
- `POST /api/machines` - Create a new machine
- `GET /api/machines/<id>` - Get machine details
- `PUT /api/machines/<id>` - Update machine details
- `DELETE /api/machines/<id>` - Delete a machine

### Inventory
- `GET /api/inventory` - Get all inventory across all machines
- `GET /api/inventory/machine/<id>` - Get inventory for a specific machine
- `POST /api/inventory` - Add a new inventory item
- `GET /api/inventory/<id>` - Get inventory item details
- `PUT /api/inventory/<id>` - Update inventory item
- `DELETE /api/inventory/<id>` - Delete inventory item
- `GET /api/inventory/low-stock` - Get low stock items

### Revenue
- `GET /api/revenue` - Get aggregated revenue for all machines
- `GET /api/revenue/machine/<id>` - Get revenue for a specific machine
- `POST /api/revenue` - Create a revenue record
- `GET /api/revenue/summary` - Get revenue summary by machine

### Support
- `GET /api/support` - Get all support tickets
- `POST /api/support` - Create a new support ticket
- `GET /api/support/<id>` - Get ticket details
- `PUT /api/support/<id>` - Update a ticket
- `DELETE /api/support/<id>` - Delete a ticket
- `GET /api/support/status/<status>` - Get tickets by status
- `GET /api/support/priority/<priority>` - Get tickets by priority

## Database Schema

### Users
- id (Primary Key)
- email (Unique)
- password_hash
- first_name
- last_name
- phone
- created_at
- updated_at

### Customers
- id (Primary Key)
- user_id (Foreign Key)
- company_name
- haha_merchant_id
- haha_api_key
- address
- city
- state
- zip_code
- created_at
- updated_at

### Machines
- id (Primary Key)
- customer_id (Foreign Key)
- machine_id
- haha_device_id
- location
- status (online, offline, maintenance)
- last_restock
- inventory_percentage
- monthly_revenue
- created_at
- updated_at

### Inventory
- id (Primary Key)
- machine_id (Foreign Key)
- product_name
- sku
- quantity
- low_stock_threshold
- status (in_stock, low_stock, out_of_stock)
- last_updated

### Revenue
- id (Primary Key)
- machine_id (Foreign Key)
- date
- units_sold
- total_revenue
- average_transaction
- created_at

### SupportTickets
- id (Primary Key)
- customer_id (Foreign Key)
- machine_id (Foreign Key, optional)
- ticket_number (Unique)
- subject
- description
- status (open, in_progress, resolved, closed)
- priority (low, medium, high, urgent)
- created_at
- updated_at
- resolved_at

### Activities
- id (Primary Key)
- machine_id (Foreign Key)
- activity_type
- description
- created_at

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://user:password@localhost:5432/snaxology_customer |
| JWT_SECRET_KEY | Secret key for JWT tokens | your-secret-key-change-in-production |
| FLASK_ENV | Flask environment | development |
| FLASK_DEBUG | Enable debug mode | True |
| HAHA_API_BASE_URL | HAHA API base URL | https://thor-openapi.hahavending.com |
| HAHA_API_KEY | HAHA API key | your-haha-api-key |
| SERVER_HOST | Server host | 0.0.0.0 |
| SERVER_PORT | Server port | 5000 |

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black .
flake8 .
```

## Deployment

### Production Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Generate a strong `JWT_SECRET_KEY`
- [ ] Configure PostgreSQL with SSL
- [ ] Set up environment variables on the server
- [ ] Use a production WSGI server (Gunicorn, uWSGI)
- [ ] Configure CORS for frontend domain
- [ ] Set up logging and monitoring
- [ ] Enable HTTPS

### Deployment with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Support

For issues or questions, please contact the Snaxology team or submit a support ticket through the portal.

## License

Proprietary - Snaxology Inc.
# Customer-Dashboard-Page
