# Snaxology Customer Portal - Frontend

A modern React-based customer portal for managing Snaxology vending machines, tracking inventory, viewing revenue reports, and managing support tickets.

## Features

- **Authentication**: Secure login and registration with JWT tokens
- **Dashboard**: Real-time metrics, revenue charts, and machine status
- **Machine Management**: View and manage vending machines
- **Inventory Tracking**: Monitor product inventory with low-stock alerts
- **Revenue Reports**: Detailed revenue analytics and trends
- **Support Tickets**: Create and track support requests
- **Responsive Design**: Mobile-first design that works on all devices
- **Dark Theme**: Professional dark interface with Snaxology red accents

## Tech Stack

- **React 19**: Latest React with hooks and functional components
- **TypeScript**: Type-safe development
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API communication
- **Recharts**: React charting library for data visualization
- **React Router**: Client-side routing
- **Lucide React**: Beautiful icon library

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── Layout.tsx       # Main layout with navigation
│   │   └── ProtectedRoute.tsx # Route guard for auth
│   ├── pages/               # Page components
│   │   ├── LoginPage.tsx
│   │   ├── SignupPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── MachinesPage.tsx
│   │   ├── InventoryPage.tsx
│   │   ├── RevenueReportsPage.tsx
│   │   ├── SupportTicketsPage.tsx
│   │   ├── ProfilePage.tsx
│   │   └── NotFoundPage.tsx
│   ├── services/            # API and external services
│   │   └── api.ts           # Axios API client
│   ├── stores/              # Zustand state management
│   │   └── authStore.ts     # Authentication state
│   ├── types/               # TypeScript interfaces
│   │   └── index.ts         # All type definitions
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # React entry point
│   └── index.css            # Global styles
├── index.html               # HTML entry point
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
├── tailwind.config.js       # Tailwind config
└── postcss.config.js        # PostCSS config
```

## Installation

### Prerequisites

- Node.js 16+ and npm/yarn/pnpm
- Backend API running on `http://localhost:5000`

### Setup Steps

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

4. **Build for production**
   ```bash
   npm run build
   ```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run type-check` - Check TypeScript types

## Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
VITE_API_URL=http://localhost:5000/api
```

### API Integration

The frontend communicates with the backend API through the `apiClient` service:

```typescript
import { apiClient } from '@/services/api'

// Set token after login
apiClient.setToken(token)

// Make API calls
const machines = await apiClient.getMachines()
```

## Authentication Flow

1. User enters credentials on login page
2. Frontend sends request to `/api/auth/login`
3. Backend returns JWT token and user data
4. Token is stored in localStorage
5. Token is automatically added to all API requests
6. Protected routes check for valid token
7. Expired tokens trigger redirect to login

## Pages Overview

### Login Page
- Email and password input
- Error handling
- Link to signup
- Demo credentials display

### Signup Page
- User registration form
- Company information
- Password validation
- Email verification

### Dashboard
- Key metrics cards (machines, revenue, alerts, tickets)
- 30-day revenue trend chart
- Machine status overview
- Recent activities feed

### Machine Management
- List all machines
- Add new machines
- View machine details
- Update machine info
- Delete machines

### Inventory Management
- View inventory across machines
- Low stock alerts
- Update quantities
- Track product SKUs

### Revenue Reports
- Revenue trends and charts
- Machine-by-machine breakdown
- Daily revenue data
- Export capabilities

### Support Tickets
- Create new tickets
- View ticket history
- Update ticket status
- Filter by priority/status

### Profile Settings
- Edit user information
- Update company details
- Change password
- Account preferences

## Styling

### Color Scheme

- **Primary Red**: `#E31E24` (Snaxology brand)
- **Dark Background**: `#1a1a1a`
- **Light Text**: `#f5f5f5`
- **Gray Accents**: Various shades for UI elements

### Typography

- **Display Font**: Playfair Display (headings)
- **Body Font**: Inter (content)

### Components

Pre-built Tailwind classes for common components:

```css
.btn-primary      /* Primary red button */
.btn-secondary    /* Gray button */
.btn-outline      /* Outlined button */
.card             /* Card container */
.card-hover       /* Card with hover effect */
.input            /* Form input */
.label            /* Form label */
.badge-*          /* Status badges */
```

## State Management

### Auth Store (Zustand)

```typescript
const { user, isAuthenticated, login, logout } = useAuthStore()
```

Available actions:
- `login(email, password)` - Authenticate user
- `signup(data)` - Register new user
- `logout()` - Clear authentication
- `getProfile()` - Fetch user profile
- `updateProfile(data)` - Update user info

## API Client

The `apiClient` provides methods for all backend endpoints:

```typescript
// Auth
await apiClient.login({ email, password })
await apiClient.signup(data)
await apiClient.getProfile()

// Dashboard
await apiClient.getDashboardOverview()
await apiClient.getRevenueSummary()

// Machines
await apiClient.getMachines()
await apiClient.createMachine(data)
await apiClient.updateMachine(id, data)

// Inventory
await apiClient.getInventory()
await apiClient.getLowStockItems()

// Revenue
await apiClient.getRevenue()
await apiClient.getRevenueSummaryByMachine()

// Support
await apiClient.getSupportTickets()
await apiClient.createSupportTicket(data)
```

## Error Handling

The API client automatically handles:
- 401 Unauthorized (redirects to login)
- Network errors
- Timeout errors
- Invalid JSON responses

Errors are caught and displayed to users with helpful messages.

## Performance Optimization

- Code splitting with React Router
- Lazy loading of pages
- Image optimization
- CSS minification
- JavaScript bundling and minification

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Tips

### Hot Module Replacement

Vite provides instant HMR for fast development:
- Save a file → changes appear immediately
- State is preserved during updates

### TypeScript

All components use TypeScript for type safety:
- Catch errors at compile time
- Better IDE autocomplete
- Self-documenting code

### Debugging

Use React Developer Tools browser extension:
- Inspect component hierarchy
- View props and state
- Profile performance

## Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

### Environment Variables for Production

Set these in your deployment platform:
- `VITE_API_URL` - Production API URL

## Troubleshooting

### API Connection Issues

If you see CORS errors:
1. Ensure backend is running on `http://localhost:5000`
2. Check `VITE_API_URL` environment variable
3. Verify backend CORS configuration

### Login Issues

- Clear localStorage: `localStorage.clear()`
- Check browser console for errors
- Verify backend is responding to `/api/auth/login`

### Build Errors

- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Check Node.js version (should be 16+)

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Proprietary - Snaxology Inc.
