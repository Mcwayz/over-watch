# Quick Start Guide - Courier Management System

Get the Courier Management System up and running in 5 minutes.

## Prerequisites

- Python 3.9+ (`python --version`)
- Node.js 16+ (`node --version`)
- PostgreSQL 12+ (or use SQLite for development)
- Git

## Option 1: Quick Start (5 minutes)

### Backend Setup

```bash
# Clone repository
git clone <repository-url> courier-system
cd courier-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Follow prompts: username, email, password

# Start development server
python manage.py runserver
```

Backend is now running at `http://localhost:8000`

### Frontend Setup (in new terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# REACT_APP_API_URL=http://localhost:8000/api

# Start development server
npm start
```

Frontend is now running at `http://localhost:3000`

## Option 2: Docker Setup (even faster)

### Using Docker Compose

```bash
# Clone repository
git clone <repository-url> courier-system
cd courier-system

# Start all services
docker-compose up -d

# Create superuser (in another terminal)
docker-compose exec backend python manage.py createsuperuser

# Check services
docker-compose ps
```

Services are now running:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Database: `localhost:5432`
- Redis: `localhost:6379`

## First Steps After Setup

### 1. Access Django Admin

1. Go to `http://localhost:8000/admin`
2. Login with your superuser credentials
3. Create initial data:
   - **Branches**: Add courier branches (branch admin)
   - **Roles**: Add 4 roles: Manager, Staff, Driver, Customer
   - **Staff**: Add staff members (operations_manager, parcel_clerk, loader, dispatcher)
   - **Drivers**: Add drivers with vehicle info
   - **Customers**: Add customer accounts

### 2. Test with Sample Data

In Django shell:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from apps.branches.models import Branch
from apps.parcels.models import Parcel
from apps.customers.models import CustomerProfile

User = get_user_model()

# Create test customer
customer_user = User.objects.create_user(
    username='customer1',
    password='password123',
    email='customer@example.com'
)
customer_profile = CustomerProfile.objects.create(user=customer_user)

# Create test branch
branch = Branch.objects.create(
    name='Main Branch',
    city='Nairobi',
    address='123 Main St',
    latitude=-1.2921,
    longitude=36.8219
)

# Create test parcel
parcel = Parcel.objects.create(
    sender=customer_profile,
    receiver_name='Jane Smith',
    receiver_phone='254712345678',
    receiver_city='Mombasa',
    origin_branch=branch,
    destination_branch=branch,
    current_branch=branch,
    weight_kg=2.5,
    declared_value=5000
)

print(f"Created parcel: {parcel.tracking_number}")
exit()
```

### 3. Test API Endpoints

Using curl or Postman:

```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'

# List branches
curl http://localhost:8000/api/branches/

# Create parcel (authenticated)
curl -X POST http://localhost:8000/api/parcels/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_name": "John Doe",
    "receiver_phone": "254712345678",
    "receiver_city": "Mombasa",
    "weight_kg": 2.5,
    "declared_value": 5000,
    "origin_branch": 1,
    "destination_branch": 1
  }'
```

### 4. Access Frontend

1. Go to `http://localhost:3000`
2. Click "Login"
3. Use credentials from your test account
4. Explore role-based dashboards:
   - **Manager**: Overview and statistics
   - **Staff**: Parcel management
   - **Driver**: Assigned deliveries
   - **Customer**: Track parcels

## Project Structure

```
courier-system/
├── manage.py                 # Django management
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Container orchestration
├── over_watch/              # Django project config
│   ├── settings.py          # Main settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI entry point
├── apps/                     # Django apps
│   ├── authentication/      # User & auth
│   ├── branches/            # Locations
│   ├── staff/               # Staff management
│   ├── drivers/             # Driver management
│   ├── customers/           # Customer accounts
│   ├── parcels/             # Parcel tracking
│   └── audit/               # Audit trail
├── utils/                    # Utilities
│   ├── pricing.py           # Pricing engine
│   ├── qr_code.py           # QR generation
│   ├── audit.py             # Audit logging
│   └── helpers.py           # Helper functions
├── frontend/                 # React app
│   ├── public/              # Static files
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── context/         # Auth context
│   │   ├── services/        # API services
│   │   └── App.js           # Main app
│   └── package.json         # Node dependencies
├── README.md                # Project overview
├── API_DOCUMENTATION.md     # API reference
├── DEPLOYMENT.md            # Deployment guide
├── TESTING.md               # Testing guide
└── QUICK_START.md          # This file
```

## Common Commands

### Backend

```bash
# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access shell
python manage.py shell

# Clear database
python manage.py flush

# Generate seed data
python manage.py seed_data  # (if implemented)
```

### Frontend

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject configuration (not recommended)
npm eject
```

### Docker

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Access backend shell
docker-compose exec backend python manage.py shell

# Run migrations in container
docker-compose exec backend python manage.py migrate
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>

# Use different port
python manage.py runserver 8001
```

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Reset database
python manage.py flush
python manage.py migrate
```

### Frontend Can't Connect to API

- Check backend is running: `curl http://localhost:8000/api/auth/`
- Check `.env` file has correct `REACT_APP_API_URL`
- Check CORS settings in Django settings.py
- Clear browser cache and try again

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# For Node modules
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. **Read Full Documentation**:
   - [README.md](README.md) - Project overview and features
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
   - [TESTING.md](TESTING.md) - Testing strategies and examples

2. **Development**:
   - Create more test data in Django admin
   - Explore API endpoints with Postman
   - Customize frontend styling with Material-UI or Tailwind
   - Implement additional features

3. **Deployment**:
   - Configure PostgreSQL for production
   - Set up Redis for caching
   - Configure environment variables
   - Deploy with Docker or traditional server
   - Set up monitoring and logging

## Support

For issues or questions:
1. Check the documentation files
2. Review API errors in Django logs
3. Check network requests in browser DevTools
4. Review Git issues on repository

## Default Credentials (Remove After Setup)

**Admin Panel** (`/admin/`):
- Use superuser credentials you created

**Test Accounts** (create as needed):
- Manager: manager@test.com / password123
- Staff: staff@test.com / password123
- Driver: driver@test.com / password123
- Customer: customer@test.com / password123

**⚠️ Change all passwords in production!**

---

**Ready to code?** Start with the [README.md](README.md) or jump straight into the [API_DOCUMENTATION.md](API_DOCUMENTATION.md).
