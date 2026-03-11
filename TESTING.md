# Courier Management System - Testing Guide

## Testing Overview

This guide provides instructions for testing the Courier Management System backend and frontend.

## Backend Testing

### Unit Tests

Create `tests/` directory in the project root:

```bash
mkdir -p tests
```

#### Test Models

Create `tests/test_models.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.branches.models import Branch
from apps.parcels.models import Parcel
from apps.customers.models import CustomerProfile
from apps.drivers.models import DriverProfile
from apps.staff.models import StaffProfile
from utils.pricing import PricingEngine

User = get_user_model()

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)

class BranchModelTest(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(
            name='Main Branch',
            city='Nairobi',
            address='123 Main St',
            latitude=-1.2921,
            longitude=36.8219
        )

    def test_branch_creation(self):
        self.assertEqual(self.branch.name, 'Main Branch')
        self.assertEqual(self.branch.city, 'Nairobi')
        self.assertTrue(self.branch.is_active)

class ParcelModelTest(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(
            name='Test Branch',
            city='Nairobi',
            address='123 Test St'
        )

        self.customer = User.objects.create_user(
            username='customer',
            password='pass123'
        )
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer
        )

        self.parcel = Parcel.objects.create(
            sender=self.customer_profile,
            receiver_name='John Doe',
            receiver_phone='254712345678',
            receiver_city='Mombasa',
            origin_branch=self.branch,
            destination_branch=self.branch,
            current_branch=self.branch,
            weight_kg=2.5,
            declared_value=5000
        )

    def test_parcel_creation(self):
        self.assertEqual(self.parcel.status, 'REGISTERED')
        self.assertIsNotNone(self.parcel.tracking_number)
        self.assertIsNotNone(self.parcel.delivery_price)

    def test_parcel_qr_code_generation(self):
        self.assertFalse(self.parcel.qr_code == '')

    def test_parcel_status_transition(self):
        old_status = self.parcel.status
        self.parcel.transition_to_status('RECEIVED')
        self.assertEqual(self.parcel.status, 'RECEIVED')
        self.assertNotEqual(old_status, self.parcel.status)

class PricingEngineTest(TestCase):
    def test_pricing_calculation_base_fee(self):
        engine = PricingEngine()
        price = engine.calculate_delivery_price(
            weight_kg=1.0,
            distance_km=10,
            declared_value=1000
        )
        self.assertGreater(price, 0)

    def test_pricing_with_different_distances(self):
        engine = PricingEngine()
        prices = []
        for distance in [50, 100, 200, 500]:
            price = engine.calculate_delivery_price(
                weight_kg=1.0,
                distance_km=distance,
                declared_value=1000
            )
            prices.append(price)

        # Prices should increase with distance
        for i in range(len(prices) - 1):
            self.assertLess(prices[i], prices[i + 1])
```

#### Test API Views

Create `tests/test_views.py`:

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.authentication.models import Role
from apps.branches.models import Branch

User = get_user_model()

class AuthenticationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_user_login(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class BranchAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.branch = Branch.objects.create(
            name='Test Branch',
            city='Nairobi',
            address='123 Test St'
        )

    def test_list_branches(self):
        response = self.client.get('/api/branches/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)

    def test_create_branch(self):
        response = self.client.post('/api/branches/', {
            'name': 'New Branch',
            'city': 'Mombasa',
            'address': '456 New St',
            'latitude': -4.0435,
            'longitude': 39.6682
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filter_branches_by_city(self):
        response = self.client.get('/api/branches/?city=Nairobi')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test tests.test_models.CustomUserModelTest

# Run specific test method
python manage.py test tests.test_models.CustomUserModelTest.test_user_creation

# Verbose output
python manage.py test -v 2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Integration Testing with Postman

### Import Collection

1. Download the Postman collection from the project
2. In Postman, click "Import" → Select the collection file
3. Set the environment variable `BASE_URL` to `http://localhost:8000/api`

### Test Workflow

#### 1. User Registration and Login

```bash
# Register new user
POST /api/auth/register/
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "securepass123",
  "first_name": "Test",
  "last_name": "User"
}

# Login
POST /api/auth/login/
{
  "username": "testuser",
  "password": "securepass123"
}
```

#### 2. Branch Management

```bash
# List branches
GET /api/branches/

# Create branch
POST /api/branches/
{
  "name": "Test Branch",
  "city": "Nairobi",
  "address": "123 Test St",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "contact_phone": "254712345678",
  "contact_email": "branch@example.com"
}

# Filter branches
GET /api/branches/?city=Nairobi&is_active=true
```

#### 3. Parcel Management

```bash
# Create parcel
POST /api/parcels/
{
  "receiver_name": "John Doe",
  "receiver_phone": "254712345678",
  "receiver_city": "Mombasa",
  "receiver_postal_code": "80100",
  "origin_branch": 1,
  "destination_branch": 2,
  "weight_kg": 2.5,
  "declared_value": 5000,
  "notes": "Fragile - Handle with care"
}

# Update parcel status
PUT /api/parcels/{id}/update_status/
{
  "status": "RECEIVED"
}

# Track parcel
GET /api/parcels/{id}/tracking/

# Search parcels
GET /api/parcels/?search=TRK-20240115-ABC123

# Filter by status
GET /api/parcels/?status=IN_TRANSIT
```

#### 4. Parcel Images

```bash
# Upload parcel image
POST /api/parcel-images/
Headers: Content-Type: multipart/form-data
{
  "parcel": 1,
  "image_type": "receipt",
  "image": <file>
}
```

#### 5. Audit Logs

```bash
# View audit logs
GET /api/audit-logs/

# Filter by user
GET /api/audit-logs/?user={user_id}

# Filter by action
GET /api/audit-logs/?action=PARCEL_STATUS_CHANGE

# Search audit logs
GET /api/audit-logs/?search=TRK-20240115-ABC123
```

## Frontend Testing

### Manual Testing Checklist

#### Authentication
- [ ] User can register with valid credentials
- [ ] User receives error on invalid registration
- [ ] User can login with valid credentials
- [ ] User cannot login with invalid credentials
- [ ] Token is stored in localStorage after login
- [ ] User is redirected to login on logout
- [ ] Expired tokens are refreshed automatically

#### Role-Based Access
- [ ] Manager sees manager dashboard with stats
- [ ] Staff sees staff dashboard with parcel list
- [ ] Driver sees driver dashboard with assigned parcels
- [ ] Customer sees customer portal with tracking
- [ ] Unauthorized users are redirected to login

#### Parcel Management
- [ ] Staff can create new parcels
- [ ] System calculates delivery price automatically
- [ ] Staff can upload multiple images per parcel
- [ ] Driver can update parcel status
- [ ] Customer can track parcel by tracking number
- [ ] Tracking timeline displays status changes

### Automated Frontend Testing

#### Install Testing Libraries

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom jest
```

#### Test Authentication Hook

Create `src/__tests__/useAuth.test.js`:

```javascript
import { renderHook, act } from '@testing-library/react';
import useAuth from '../hooks/useAuth';
import AuthProvider from '../context/AuthContext';

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

describe('useAuth Hook', () => {
  test('initializes with unauthenticated state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  test('login sets user and token', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      await result.current.login('testuser', 'password123');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toBeDefined();
  });

  test('logout clears user and token', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    // First login
    await act(async () => {
      await result.current.login('testuser', 'password123');
    });
    
    // Then logout
    await act(async () => {
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
  });
});
```

#### Test Components

Create `src/__tests__/LoginPage.test.js`:

```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginPage from '../pages/LoginPage';
import { BrowserRouter } from 'react-router-dom';

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('LoginPage', () => {
  test('renders login form', () => {
    renderWithRouter(<LoginPage />);
    expect(screen.getByText(/login/i)).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: /username/i })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: /password/i })).toBeInTheDocument();
  });

  test('submits login form', async () => {
    renderWithRouter(<LoginPage />);
    
    fireEvent.change(screen.getByRole('textbox', { name: /username/i }), {
      target: { value: 'testuser' }
    });
    
    fireEvent.change(screen.getByRole('textbox', { name: /password/i }), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(screen.queryByText(/login/i)).not.toBeInTheDocument();
    });
  });
});
```

### Run Frontend Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## Performance Testing

### Load Testing with Apache JMeter

1. Install JMeter
2. Create test plan with:
   - 100 concurrent users
   - 10 iterations per user
   - Endpoints: /api/parcels, /api/audit-logs, /api/branches

```bash
jmeter -n -t test_plan.jmx -l results.jtl -j jmeter.log
```

### Database Query Analysis

```python
# In Django shell
from django.db import connection
from django.test.utils import override_settings

with override_settings(DEBUG=True):
    from apps.parcels.models import Parcel
    parcels = Parcel.objects.select_related('sender', 'origin_branch', 'destination_branch').all()
    
    # View SQL queries
    print(connection.queries)
    print(f"Number of queries: {len(connection.queries)}")
```

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: courier_test
          POSTGRES_USER: courier
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage

    - name: Run tests
      run: |
        coverage run --source='.' manage.py test
        coverage report

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Test Coverage Goals

- Models: 90%+ coverage
- Views/Viewsets: 85%+ coverage
- Serializers: 80%+ coverage
- Business Logic: 90%+ coverage
- Overall: 85%+ coverage

## Debugging Tests

```bash
# Run test with debugging
python manage.py test --pdb tests.test_models

# Run with verbose output
python manage.py test -v 2

# Drop into shell after test failure
python -m pdb manage.py test

# Run single test
python manage.py test tests.test_views.AuthenticationAPITest.test_user_login
```

## Test Data Management

### Create Fixtures

```bash
# Django can dump current database as fixture
python manage.py dumpdata > test_data.json

# Load fixtures in tests
class MyTestCase(TestCase):
    fixtures = ['test_data.json']
```

### Factory Boy (Alternative)

Install:
```bash
pip install factory-boy
```

Create factories in `tests/factories.py`:

```python
import factory
from django.contrib.auth import get_user_model
from apps.branches.models import Branch

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class BranchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Branch

    name = factory.Faker('company')
    city = factory.Faker('city')
    address = factory.Faker('address')
```

Use in tests:

```python
def test_something():
    user = UserFactory()
    branch = BranchFactory()
```
