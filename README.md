# Overwatch Courier Management System

## Project Overview

A comprehensive courier management system built with Django REST Framework and React, designed to manage parcel operations, driver tracking, staff workflows, and customer interactions.

## Technology Stack

### Backend
- **Django 6.0** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database (SQLite for development)
- **JWT** - Authentication
- **Redis** - Caching and task queue
- **Celery** - Async task processing
- **QRCode** - Parcel tracking QR codes

### Frontend
- **React 18** - UI library
- **React Router** - Navigation
- **Axios** - HTTP requests
- **React Toastify** - Notifications

## Installation & Setup

### Backend Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env with API URL
   ```

4. **Run Development Server**
   ```bash
   npm start
   ```

## Project Structure

```
over_watch/
├── manage.py
├── requirements.txt
├── .env.example
├── over_watch/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── authentication/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── branches/
│   ├── staff/
│   ├── drivers/
│   ├── customers/
│   ├── parcels/
│   └── audit/
├── utils/
│   ├── pricing.py
│   ├── qr_code.py
│   ├── audit.py
│   └── helpers.py
└── frontend/
    ├── public/
    └── src/
        ├── components/
        ├── pages/
        ├── services/
        ├── context/
        ├── hooks/
        └── styles/
```

## Database Models

### Authentication Module
- **CustomUser**: Extended user model with roles
- **Role**: User roles (Manager, Staff, Driver, Customer)
- **Permission**: Granular permissions
- **RolePermission**: Role-permission mapping

### Core Modules
- **Branch**: Courier branch locations
- **StaffProfile**: Branch staff members
- **DriverProfile**: Delivery drivers
- **CustomerProfile**: Customer accounts

### Parcel Management
- **Parcel**: Main parcel entity with status workflow
- **ParcelImage**: Multiple images per parcel
- **ParcelTrackingHistory**: Status change history
- **ParcelTransitUpdate**: Real-time location updates
- **PickupRequest**: Customer pickup requests
- **DeliveryProof**: Delivery confirmation

### Audit Trail
- **AuditLog**: Complete system audit trail

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `GET /api/auth/users/current_user/` - Current user info
- `POST /api/auth/users/change_password/` - Change password

### Branches
- `GET /api/branches/` - List branches
- `POST /api/branches/` - Create branch
- `GET /api/branches/{id}/` - Retrieve branch
- `PUT /api/branches/{id}/` - Update branch
- `DELETE /api/branches/{id}/` - Delete branch

### Staff
- `GET /api/staff/` - List staff
- `POST /api/staff/` - Create staff
- `GET /api/staff/{id}/` - Retrieve staff
- `PUT /api/staff/{id}/` - Update staff
- `POST /api/staff/{id}/deactivate/` - Deactivate staff

### Drivers
- `GET /api/drivers/` - List drivers
- `POST /api/drivers/` - Create driver
- `GET /api/drivers/{id}/` - Retrieve driver
- `PUT /api/drivers/{id}/` - Update driver
- `POST /api/drivers/{id}/deactivate/` - Deactivate driver
- `GET /api/drivers/my_deliveries/` - Current driver's deliveries

### Customers
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}/` - Retrieve customer
- `PUT /api/customers/{id}/` - Update customer
- `GET /api/customers/my_profile/` - Current customer's profile

### Parcels
- `GET /api/parcels/parcels/` - List parcels
- `POST /api/parcels/parcels/` - Create parcel
- `GET /api/parcels/parcels/{id}/` - Retrieve parcel
- `POST /api/parcels/parcels/{id}/update_status/` - Update status
- `GET /api/parcels/parcels/{id}/download_qr/` - Download QR code
- `POST /api/parcels/parcels/{id}/assign_driver/` - Assign driver
- `GET /api/parcels/parcels/{id}/tracking/` - Get tracking info

### Images
- `GET /api/parcels/parcel-images/` - List images
- `POST /api/parcels/parcel-images/` - Upload image
- `DELETE /api/parcels/parcel-images/{id}/` - Delete image

### Transit Updates
- `GET /api/parcels/transit-updates/` - List updates
- `POST /api/parcels/transit-updates/` - Create update

### Pickup Requests
- `GET /api/parcels/pickup-requests/` - List requests
- `POST /api/parcels/pickup-requests/` - Create request
- `POST /api/parcels/pickup-requests/{id}/approve/` - Approve
- `POST /api/parcels/pickup-requests/{id}/reject/` - Reject

### Delivery Proof
- `GET /api/parcels/delivery-proofs/` - List proofs
- `POST /api/parcels/delivery-proofs/` - Create proof

### Audit Logs
- `GET /api/audit/` - List audit logs

## Features

### Manager Dashboard
- View branch performance metrics
- Monitor parcel flow across branches
- Manage staff accounts
- Manage driver accounts
- View operational reports

### Staff Dashboard
- Register customers
- Register parcels
- Upload parcel images
- Load parcels onto vehicles
- Dispatch parcels
- Update parcel status

### Driver Dashboard
- View assigned deliveries
- Scan parcel QR codes
- Update transit locations with GPS
- Confirm delivery with proof
- Track parcel status

### Customer Portal
- Create account
- Send parcels
- Track parcels with tracking number
- Request parcel pickup
- Upload proof for disputes
- View parcel history

## Pricing Calculation

The system uses a tiered pricing model:

```
Total Price = Base Fee + (Weight × Rate per KG) + Distance Fee + Insurance Fee

Where:
- Base Fee: 500 currency units
- Rate per KG: 50 currency units
- Distance Fee: Calculated based on distance tiers
- Insurance Fee: 1% of declared value
```

## Parcel Status Workflow

```
REGISTERED → RECEIVED → LOADED → DISPATCHED → IN_TRANSIT → ARRIVED → OUT_FOR_DELIVERY → DELIVERED
```

## Deployment

### Production Checklist
1. Set `DEBUG=False`
2. Configure `ALLOWED_HOSTS`
3. Use PostgreSQL database
4. Set secure `SECRET_KEY`
5. Configure HTTPS
6. Set up Redis for caching
7. Configure email backend
8. Run migrations
9. Collect static files

### Docker Deployment (Optional)
```bash
docker-compose up -d
```

## Testing

### Run Tests
```bash
python manage.py test
```

## Contributing

1. Create feature branch: `git checkout -b feature/feature-name`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/feature-name`
4. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For support, email mcwayzj@gmail.com or open an issue on GitHub.
