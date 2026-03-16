# Overwatch Courier Management System (Backend API)

## Project Overview

Comprehensive courier management API built with Django REST Framework. Manage parcel operations, driver tracking, staff workflows, and customer interactions via REST API.

**Swagger UI:** http://localhost:8000/api/docs/
**ReDoc:** http://localhost:8000/api/redoc/

## Technology Stack

- **Django 6.0** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database
- **JWT** - Authentication
- **Redis** - Caching/task queue
- **Celery** - Async tasks
- **drf-spectacular** - OpenAPI/Swagger docs
- **QRCode** - Parcel tracking

## Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment File**
   ```bash
   copy .env.example .env
   REM Edit .env (DB_NAME, DB_PASSWORD etc.)
   ```

3. **Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Collect Static**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Run Server**
   ```bash
   python manage.py runserver
   ```

   Visit http://localhost:8000/api/docs/

## Project Structure

```
over_watch/
├── manage.py
├── requirements.txt
├── over_watch/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/
│   ├── branches/
│   ├── staff/
│   ├── drivers/
│   ├── customers/
│   ├── parcels/
│   ├── vehicles/
│   ├── audit/
│   └── notifications/
└── utils/
    ├── pricing.py
    ├── qr_code.py
    ├── distance.py
    └── ...
```

## Key Features (via API)

- JWT Authentication
- Role-based permissions
- Parcel lifecycle management
- Driver assignment & tracking
- QR code generation
- Image upload for parcels
- Full audit trail
- Dynamic pricing

## API Endpoints

See Swagger /api/docs/ for full schema.

**Authentication:**
- POST /api/auth/token/
- POST /api/auth/login/
- GET /api/auth/users/current_user/

**Parcels:**
- POST /api/parcels/parcels/ (create)
- GET /api/parcels/parcels/{id}/tracking/
- POST /api/parcels/parcels/{id}/update_status/

**Admin Django:** /admin/

## Parcel Status Workflow

```
REGISTERED → RECEIVED → LOADED → DISPATCHED → IN_TRANSIT → ARRIVED → OUT_FOR_DELIVERY → DELIVERED
```

## Pricing

```
Total = Base (500) + Weight*50 + Distance + 1% Insurance
```

## Deployment

1. DEBUG=False
2. ALLOWED_HOSTS=*
3. PostgreSQL prod DB
4. Gunicorn + Nginx
5. Redis/Celery setup

## Testing

```bash
python manage.py test
```

## License

MIT
