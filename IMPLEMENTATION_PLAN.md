# Courier Management System - Implementation Plan

## 📊 Current Status Analysis

### ✅ Already Implemented (Backend)
1. Parcel model with full status workflow (REGISTERED → RECEIVED → LOADED → DISPATCHED → IN_TRANSIT → ARRIVED → OUT_FOR_DELIVERY → DELIVERED)
2. Submission types (BRANCH_DROPOFF, PICKUP)
3. Parcel workflow transitions (load, dispatch, mark_in_transit, mark_arrived, out_for_delivery, confirm_delivery)
4. Bulk operations (bulk_in_transit, bulk_load, bulk_dispatch)
5. PickupRequest model with status workflow
6. Pickup fee calculation (PricingEngine)
7. Delivery price calculation
8. QR code generation
9. Parcel images (ParcelImage)
10. Transit updates (ParcelTransitUpdate)
11. Delivery proof (DeliveryProof)
12. Audit logging
13. Vehicle model with GPS tracking

### ✅ Already Implemented (Frontend)
1. API service with all endpoints
2. Basic dashboard skeletons
3. Basic customer tracking

### ❌ Missing Features to Implement

---

## 🎯 PHASE 1: Backend Enhancements

### 1.1 Pickup Request Workflow Extensions
**Priority:** HIGH

**Tasks:**
- [ ] Add `schedule_pickup()` action to PickupRequestViewSet - assign driver and set pickup date
- [ ] Add `confirm_pickup()` action to PickupRequestViewSet - driver confirms pickup
- [ ] Add `create_parcel_from_pickup()` to create actual parcel after pickup confirmation
- [ ] Add method to calculate pickup fee based on address/distance

**Files to modify:**
- `apps/parcels/views.py` - Add pickup workflow actions

### 1.2 Distance Calculation Service
**Priority:** MEDIUM

**Tasks:**
- [ ] Create `utils/distance.py` for distance calculation between coordinates
- [ ] Integrate with pickup fee calculation
- [ ] Fallback to Haversine formula if no API

**Files to create:**
- `utils/distance.py`

### 1.3 QR Code Scanning Endpoint
**Priority:** HIGH

**Tasks:**
- [ ] Add `scan_qr()` endpoint to retrieve parcel by QR tracking number
- [ ] Log QR scan events

**Files to modify:**
- `apps/parcels/views.py`

### 1.4 Driver Parcel Assignment
**Priority:** HIGH

**Tasks:**
- [ ] Add `get_assigned_parcels()` to DriverViewSet - get parcels assigned to driver's vehicle
- [ ] Add `get_vehicle_parcels()` to VehicleViewSet - get all parcels on a vehicle

**Files to modify:**
- `apps/drivers/views.py`
- `apps/vehicles/views.py`

### 1.5 Staff Management Endpoints
**Priority:** HIGH

**Tasks:**
- [ ] Add staff CRUD endpoints
- [ ] Add staff activation/deactivation
- [ ] Add manager-only permissions

**Files to modify:**
- `apps/staff/views.py`

### 1.6 Dashboard Statistics APIs
**Priority:** HIGH

**Tasks:**
- [ ] Add `dashboard_stats` endpoint for manager - total parcels by status, revenue, etc.
- [ ] Add `staff_dashboard_stats` for staff - incoming parcels, pending pickups
- [ ] Add `driver_dashboard_stats` for driver - assigned parcels, deliveries today

**Files to modify:**
- `apps/parcels/views.py`
- `apps/drivers/views.py`

---

## 🎯 PHASE 2: Frontend Enhancements

### 2.1 Staff Dashboard Full Implementation
**Priority:** HIGH

**Tasks:**
- [ ] Register new parcel form (walk-in)
- [ ] View/manage pickup requests
- [ ] Bulk parcel loading interface
- [ ] Bulk dispatch interface
- [ ] Parcel image upload
- [ ] View incoming parcels at branch
- [ ] Schedule pickup for customers

**Files to modify:**
- `frontend/src/pages/StaffDashboard.js`

### 2.2 Driver Dashboard Full Implementation
**Priority:** HIGH

**Tasks:**
- [ ] View assigned parcels (by vehicle)
- [ ] Bulk in-transit update with location
- [ ] QR code scanner interface (camera)
- [ ] Individual parcel delivery confirmation
- [ ] Delivery proof upload with camera
- [ ] Transit location updates

**Files to modify:**
- `frontend/src/pages/DriverDashboard.js`

### 2.3 Customer Portal Full Implementation
**Priority:** HIGH

**Tasks:**
- [ ] Request pickup form
- [ ] View my pickup requests
- [ ] Improved tracking timeline
- [ ] Parcel history view
- [ ] Report issue / upload proof

**Files to modify:**
- `frontend/src/pages/CustomerPortal.js`

### 2.4 Manager Dashboard Full Implementation
**Priority:** HIGH

**Tasks:**
- [ ] Branch performance metrics
- [ ] Staff management interface
- [ ] Driver management interface
- [ ] Parcel status distribution chart
- [ ] Audit logs viewer
- [ ] Reports generation

**Files to modify:**
- `frontend/src/pages/ManagerDashboard.js`

---

## 🎯 PHASE 3: Additional Features

### 3.1 Notifications System
**Priority:** MEDIUM

**Tasks:**
- [ ] Create notification models
- [ ] Add notification preferences
- [ ] Implement in-app notifications
- [ ] (Optional) Email/SMS integration

**Files to create:**
- `apps/notifications/` app

### 3.2 Reports Generation
**Priority:** MEDIUM

**Tasks:**
- [ ] Parcel delivery reports
- [ ] Revenue reports
- [ ] Driver performance reports
- [ ] Branch performance reports

**Files to modify:**
- Add reports endpoints

---

## 📝 Implementation Order

### Step 1: Backend Core (Priority 1)
1. Pickup scheduling and confirmation
2. Dashboard statistics APIs
3. QR scanning endpoint

### Step 2: Frontend Dashboards (Priority 2)
1. Manager Dashboard
2. Staff Dashboard
3. Driver Dashboard
4. Customer Portal

### Step 3: Advanced Features (Priority 3)
1. Notifications
2. Reports
3. Distance calculation

---

## 🔧 Key Files Reference

### Backend
- `apps/parcels/models.py` - Parcel, PickupRequest, DeliveryProof models
- `apps/parcels/views.py` - ParcelViewSet, PickupRequestViewSet
- `apps/parcels/serializers.py` - Serializers
- `apps/drivers/views.py` - DriverViewSet
- `apps/staff/views.py` - StaffViewSet
- `apps/vehicles/views.py` - VehicleViewSet
- `utils/pricing.py` - PricingEngine

### Frontend
- `frontend/src/pages/ManagerDashboard.js`
- `frontend/src/pages/StaffDashboard.js`
- `frontend/src/pages/DriverDashboard.js`
- `frontend/src/pages/CustomerPortal.js`
- `frontend/src/services/api.js`

---

## ⚠️ Notes

- All status transitions must be validated
- All actions must be audit logged
- Role-based access control must be enforced
- Bulk operations should handle partial failures gracefully

