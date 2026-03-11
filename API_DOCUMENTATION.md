# API Documentation

## Authentication

All API requests require JWT authentication token in the `Authorization` header:

```
Authorization: Bearer {access_token}
```

### Obtain Token

```http
POST /api/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

Response:
```json
{
  "refresh": "eyJ...",
  "access": "eyJ...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "manager",
    "role_display": "Manager"
  }
}
```

## Response Format

All responses follow this structure:

### Success Response (200, 201, 204)
```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2"
}
```

### Paginated Response
```json
{
  "count": 100,
  "next": "http://api.example.com/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Parcel Workflow Example

### 1. Create Parcel (Customer)

```http
POST /api/parcels/parcels/
Content-Type: application/json

{
  "receiver_name": "John Smith",
  "receiver_phone": "+234901234567",
  "receiver_address": "123 Main St",
  "receiver_city": "Lagos",
  "receiver_postal_code": "100001",
  "destination_branch": "uuid",
  "weight_kg": "2.5",
  "declared_value": "50000"
}
```

### 2. Upload Parcel Images (Staff)

```http
POST /api/parcels/parcel-images/
Content-Type: multipart/form-data

{
  "parcel": "uuid",
  "image": <file>,
  "image_type": "receipt",
  "description": "Parcel receipt photo"
}
```

### 3. Update Parcel Status (Staff)

```http
POST /api/parcels/parcels/{parcel_id}/update_status/
Content-Type: application/json

{
  "status": "DISPATCHED",
  "notes": "Parcel dispatched to driver"
}
```

### 4. Assign Driver (Manager/Staff)

```http
POST /api/parcels/parcels/{parcel_id}/assign_driver/
Content-Type: application/json

{
  "driver_id": "uuid"
}
```

### 5. Transit Update (Driver)

```http
POST /api/parcels/transit-updates/
Content-Type: application/json

{
  "parcel": "uuid",
  "driver": "uuid",
  "location_name": "Abuja Branch",
  "latitude": "9.0765",
  "longitude": "7.3986",
  "transit_status": "in_transit",
  "notes": "Parcel in transit to destination"
}
```

### 6. Delivery Proof (Driver)

```http
POST /api/parcels/delivery-proofs/
Content-Type: multipart/form-data

{
  "parcel": "uuid",
  "proof_image": <file>,
  "delivery_notes": "Delivered successfully",
  "signature_required": true,
  "signature_image": <file>
}
```

### 7. Track Parcel (Customer)

```http
GET /api/parcels/parcels/{parcel_id}/tracking/
```

Response:
```json
{
  "id": "uuid",
  "tracking_number": "TRK20240101000123ABC",
  "receiver_name": "John Smith",
  "status": "IN_TRANSIT",
  "status_display": "In Transit",
  "transit_updates": [
    {
      "id": "uuid",
      "location_name": "Enugu Branch",
      "latitude": "6.4550",
      "longitude": "7.5245",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Filtering, Searching, and Sorting

### Filtering
```
GET /api/staff/?branch={branch_id}&position=operations_manager&is_active=true
```

### Searching
```
GET /api/parcels/parcels/?search=tracking_number
```

### Sorting
```
GET /api/parcels/parcels/?ordering=-created_at
```

### Pagination
```
GET /api/parcels/parcels/?page=1&limit=20
```

## Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Successful but no content |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Server Error - Internal server error |

## Rate Limiting

API requests are rate-limited to prevent abuse. Check response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

## Error Handling

Always check for errors in responses:

```javascript
try {
  const response = await api.get('/endpoint/');
} catch (error) {
  if (error.response?.status === 401) {
    // Handle authentication error
  } else if (error.response?.status === 403) {
    // Handle permission error
  } else if (error.response?.status === 404) {
    // Handle not found error
  }
}
```

## Permissions

Different roles have different permissions:

- **Manager**: Full access to all operations
- **Staff**: Can manage parcels at their branch
- **Driver**: Can view assigned parcels and update status
- **Customer**: Can only access their own parcels

Permission errors return `403 Forbidden`.
