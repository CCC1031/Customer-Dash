# Snaxology Customer Portal - Project Overview

## Project Summary

The Snaxology Customer Portal is a comprehensive web-based platform that enables customers to manage their vending machine networks, track inventory, monitor revenue, and submit support requests. The system is built with a modern tech stack featuring a Flask backend, React frontend, and PostgreSQL database.

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer (React)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Dashboard  │  │   Machines   │  │  Inventory   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Revenue    │  │   Support    │  │   Profile    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP/REST API
┌──────────────────────────▼───────────────────────────────────┐
│                   API Layer (Flask)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Auth      │  │  Dashboard   │  │   Machines   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Inventory   │  │   Revenue    │  │   Support    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬───────────────────────────────────┘
                           │ SQL
┌──────────────────────────▼───────────────────────────────────┐
│              Database Layer (PostgreSQL)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Users     │  │  Customers   │  │   Machines   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Inventory   │  │   Revenue    │  │   Tickets    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│           External Services (HAHA Vending API)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Devices    │  │  Inventory   │  │   Revenue    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: Flask 2.3.3
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: JWT (Flask-JWT-Extended)
- **API**: RESTful with CORS support
- **Python Version**: 3.8+

### Frontend
- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Routing**: React Router
- **Charts**: Recharts
- **Icons**: Lucide React

### Database
- **DBMS**: PostgreSQL 12+
- **Connection Pool**: SQLAlchemy with psycopg2

### External Integrations
- **HAHA Vending API**: Real-time machine data and metrics

## Project Structure

### Backend (`/`)

```
snaxology-customer-portal/
├── app.py                    # Flask application entry point
├── models.py                 # SQLAlchemy database models
├── haha_integration.py       # HAHA API client and sync service
├── init_db.py               # Database initialization script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # Backend documentation
└── routes/
    ├── __init__.py
    ├── auth.py             # Authentication endpoints
    ├── dashboard.py        # Dashboard metrics endpoints
    ├── machines.py         # Machine management endpoints
    ├── inventory.py        # Inventory tracking endpoints
    ├── revenue.py          # Revenue reporting endpoints
    └── support.py          # Support ticket endpoints
```

### Frontend (`/frontend`)

```
frontend/
├── src/
│   ├── components/         # Reusable components
│   │   ├── Layout.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/             # Page components
│   │   ├── LoginPage.tsx
│   │   ├── SignupPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── MachinesPage.tsx
│   │   ├── InventoryPage.tsx
│   │   ├── RevenueReportsPage.tsx
│   │   ├── SupportTicketsPage.tsx
│   │   ├── ProfilePage.tsx
│   │   └── NotFoundPage.tsx
│   ├── services/          # API and services
│   │   └── api.ts
│   ├── stores/            # State management
│   │   └── authStore.ts
│   ├── types/             # TypeScript types
│   │   └── index.ts
│   ├── App.tsx            # Main app component
│   ├── main.tsx           # React entry point
│   └── index.css          # Global styles
├── index.html             # HTML entry point
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite config
├── tailwind.config.js     # Tailwind config
└── postcss.config.js      # PostCSS config
```

## Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- password_hash
- first_name, last_name
- phone
- created_at, updated_at

### Customers Table
- id (Primary Key)
- user_id (Foreign Key)
- company_name
- haha_merchant_id
- address, city, state, zip_code
- created_at, updated_at

### Machines Table
- id (Primary Key)
- customer_id (Foreign Key)
- machine_id, haha_device_id
- location, status
- inventory_percentage, monthly_revenue
- last_restock
- created_at, updated_at

### Inventory Table
- id (Primary Key)
- machine_id (Foreign Key)
- product_name, sku
- quantity, low_stock_threshold
- status
- last_updated

### Revenue Table
- id (Primary Key)
- machine_id (Foreign Key)
- date
- units_sold, total_revenue, average_transaction
- created_at

### SupportTickets Table
- id (Primary Key)
- customer_id, machine_id (Foreign Keys)
- ticket_number (Unique)
- subject, description
- status, priority
- created_at, updated_at, resolved_at

### Activities Table
- id (Primary Key)
- machine_id (Foreign Key)
- activity_type, description
- created_at

## API Endpoints

### Authentication (40+ endpoints total)

#### Auth Routes
- `POST /api/auth/signup` - Register new customer
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile
- `POST /api/auth/logout` - Logout

#### Dashboard Routes
- `GET /api/dashboard/overview` - Dashboard metrics
- `GET /api/dashboard/revenue-summary` - Revenue data
- `GET /api/dashboard/machine-status` - Machine statuses

#### Machine Routes
- `GET /api/machines` - List all machines
- `POST /api/machines` - Create machine
- `GET /api/machines/<id>` - Get machine details
- `PUT /api/machines/<id>` - Update machine
- `DELETE /api/machines/<id>` - Delete machine

#### Inventory Routes
- `GET /api/inventory` - List all inventory
- `GET /api/inventory/machine/<id>` - Machine inventory
- `POST /api/inventory` - Add inventory item
- `GET /api/inventory/<id>` - Get item details
- `PUT /api/inventory/<id>` - Update item
- `DELETE /api/inventory/<id>` - Delete item
- `GET /api/inventory/low-stock` - Low stock items

#### Revenue Routes
- `GET /api/revenue` - Aggregated revenue
- `GET /api/revenue/machine/<id>` - Machine revenue
- `POST /api/revenue` - Create revenue record
- `GET /api/revenue/summary` - Revenue by machine

#### Support Routes
- `GET /api/support` - List tickets
- `POST /api/support` - Create ticket
- `GET /api/support/<id>` - Get ticket
- `PUT /api/support/<id>` - Update ticket
- `DELETE /api/support/<id>` - Delete ticket
- `GET /api/support/status/<status>` - Filter by status
- `GET /api/support/priority/<priority>` - Filter by priority

## Key Features

### Authentication & Security
- JWT token-based authentication
- Secure password hashing (Werkzeug)
- Token expiration and refresh
- Protected API endpoints
- CORS support for frontend

### Dashboard
- Real-time metrics display
- Revenue trend charts
- Machine status overview
- Low stock alerts
- Recent activity feed

### Machine Management
- Add/edit/delete machines
- Real-time status tracking
- Inventory percentage display
- Monthly revenue tracking
- Last restock date

### Inventory Tracking
- Product-level inventory
- Low stock threshold alerts
- Stock status (in_stock, low_stock, out_of_stock)
- Inventory history
- SKU tracking

### Revenue Reporting
- Daily revenue tracking
- 30-day trend analysis
- Machine-by-machine breakdown
- Units sold metrics
- Average transaction value

### Support Ticketing
- Create support tickets
- Track ticket status
- Priority levels
- Ticket history
- Activity logging

### HAHA API Integration
- Real-time device sync
- Inventory synchronization
- Revenue data import
- Alert management
- Network summary statistics

## Installation & Setup

### Backend Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   python init_db.py --seed
   ```

5. **Run development server**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Access the application**
   - Frontend: `http://localhost:5173`
   - Backend: `http://localhost:5000`

## Development Workflow

### Backend Development
1. Create feature branch
2. Implement API endpoints
3. Add database models if needed
4. Test with Postman or curl
5. Create pull request

### Frontend Development
1. Create feature branch
2. Implement React components
3. Integrate with API client
4. Test with dev server
5. Create pull request

### Testing
- Backend: Use pytest or unittest
- Frontend: Use Jest and React Testing Library
- Integration: Test full flow end-to-end

## Deployment

### Backend Deployment
- Use Gunicorn for WSGI server
- Configure PostgreSQL on production
- Set environment variables
- Use SSL/TLS for HTTPS
- Configure reverse proxy (Nginx)

### Frontend Deployment
- Build with `npm run build`
- Deploy `dist/` folder to CDN or static host
- Configure API URL for production
- Enable gzip compression
- Set cache headers

## Performance Considerations

### Backend
- Database query optimization
- Connection pooling
- Caching strategies
- API response pagination
- Rate limiting

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- CSS minification
- JavaScript bundling

## Security

### Backend
- Input validation
- SQL injection prevention (SQLAlchemy)
- CORS configuration
- JWT token validation
- Password hashing

### Frontend
- XSS prevention
- CSRF protection
- Secure token storage
- HTTPS enforcement
- Content Security Policy

## Monitoring & Logging

### Backend
- Application logs
- Database query logs
- API request/response logs
- Error tracking
- Performance metrics

### Frontend
- Console errors
- User interaction tracking
- Performance monitoring
- Error reporting

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live data
2. **Mobile App**: Native iOS/Android applications
3. **Advanced Analytics**: Machine learning insights
4. **Automated Alerts**: Email/SMS notifications
5. **Payment Integration**: Stripe for commission payments
6. **Multi-language Support**: i18n implementation
7. **API Documentation**: Swagger/OpenAPI
8. **Admin Dashboard**: Internal management panel

## Support & Maintenance

### Regular Tasks
- Database backups
- Security updates
- Dependency updates
- Performance monitoring
- User support

### Troubleshooting
- Check logs for errors
- Verify database connectivity
- Test API endpoints
- Clear browser cache
- Restart services

## Contact & Documentation

- Backend Documentation: `README.md`
- Frontend Documentation: `FRONTEND_README.md`
- API Endpoints: See backend README
- Database Schema: See models.py

## License

Proprietary - Snaxology Inc.

---

**Last Updated**: May 2026
**Version**: 1.0.0
**Status**: Development Complete
