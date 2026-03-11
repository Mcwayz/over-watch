/**
 * API Service - Axios configuration and API calls
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${API_BASE_URL}/auth/token/refresh/`,
          { refresh: refreshToken }
        );
        localStorage.setItem('access_token', response.data.access);
        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (e) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ===== Authentication Endpoints =====
export const authService = {
  login: (username, password) => api.post('/auth/login/', { username, password }),
  register: (userData) => api.post('/auth/register/', userData),
  getCurrentUser: () => api.get('/auth/users/current_user/'),
  changePassword: (oldPassword, newPassword, newPasswordConfirm) =>
    api.post('/auth/users/change_password/', { old_password: oldPassword, new_password: newPassword, new_password_confirm: newPasswordConfirm }),
};

// ===== Branch Endpoints =====
export const branchService = {
  list: (params) => api.get('/branches/', { params }),
  create: (data) => api.post('/branches/', data),
  retrieve: (id) => api.get(`/branches/${id}/`),
  update: (id, data) => api.put(`/branches/${id}/`, data),
  delete: (id) => api.delete(`/branches/${id}/`),
};

// ===== Staff Endpoints =====
export const staffService = {
  list: (params) => api.get('/staff/', { params }),
  create: (data) => api.post('/staff/', data),
  retrieve: (id) => api.get(`/staff/${id}/`),
  update: (id, data) => api.put(`/staff/${id}/`, data),
  deactivate: (id) => api.post(`/staff/${id}/deactivate/`),
};

// ===== Driver Endpoints =====
export const driverService = {
  list: (params) => api.get('/drivers/', { params }),
  create: (data) => api.post('/drivers/', data),
  retrieve: (id) => api.get(`/drivers/${id}/`),
  update: (id, data) => api.put(`/drivers/${id}/`, data),
  deactivate: (id) => api.post(`/drivers/${id}/deactivate/`),
  myDeliveries: () => api.get('/drivers/my_deliveries/'),
  myVehicleParcels: () => api.get('/drivers/my_vehicle_parcels/'),
  myPendingPickups: () => api.get('/drivers/my_pending_pickups/'),
};

// ===== Customer Endpoints =====
export const customerService = {
  list: (params) => api.get('/customers/', { params }),
  create: (data) => api.post('/customers/', data),
  retrieve: (id) => api.get(`/customers/${id}/`),
  update: (id, data) => api.put(`/customers/${id}/`, data),
  myProfile: () => api.get('/customers/my_profile/'),
};

// ===== Parcel Endpoints =====
export const parcelService = {
  list: (params) => api.get('/parcels/parcels/', { params }),
  create: (data) => api.post('/parcels/parcels/', data),
  retrieve: (id) => api.get(`/parcels/parcels/${id}/`),
  updateStatus: (id, status, notes) =>
    api.post(`/parcels/parcels/${id}/update_status/`, { status, notes }),
  downloadQR: (id) => api.get(`/parcels/parcels/${id}/download_qr/`),
  tracking: (id) => api.get(`/parcels/parcels/${id}/tracking/`),
  assignDriver: (id, driverId) =>
    api.post(`/parcels/parcels/${id}/assign_driver/`, { driver_id: driverId }),
  assignVehicle: (id, vehicleId) =>
    api.post(`/parcels/parcels/${id}/assign_vehicle/`, { vehicle_id: vehicleId }),
  // Workflow actions
  load: (id, vehicleId, notes) =>
    api.post(`/parcels/parcels/${id}/load/`, { vehicle_id: vehicleId, notes }),
  dispatch: (id, notes) =>
    api.post(`/parcels/parcels/${id}/dispatch/`, { notes }),
  markInTransit: (id, locationName, latitude, longitude, notes) =>
    api.post(`/parcels/parcels/${id}/mark_in_transit/`, { 
      location_name: locationName, latitude, longitude, notes 
    }),
  markArrived: (id, notes) =>
    api.post(`/parcels/parcels/${id}/mark_arrived/`, { notes }),
  outForDelivery: (id, notes) =>
    api.post(`/parcels/parcels/${id}/out_for_delivery/`, { notes }),
  confirmDelivery: (id, proofImage, deliveryNotes) => {
    const formData = new FormData();
    if (proofImage) formData.append('proof_image', proofImage);
    if (deliveryNotes) formData.append('delivery_notes', deliveryNotes);
    return api.post(`/parcels/parcels/${id}/confirm_delivery/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  // Bulk operations
  bulkInTransit: (parcelIds, locationName, latitude, longitude) =>
    api.post('/parcels/parcels/bulk_in_transit/', {
      parcel_ids: parcelIds,
      location_name: locationName,
      latitude,
      longitude,
    }),
  bulkLoad: (parcelIds, vehicleId) =>
    api.post('/parcels/parcels/bulk_load/', {
      parcel_ids: parcelIds,
      vehicle_id: vehicleId,
    }),
  bulkDispatch: (parcelIds) =>
    api.post('/parcels/parcels/bulk_dispatch/', {
      parcel_ids: parcelIds,
    }),
  // Pricing
  calculatePickupFee: (distanceKm, isPriority) =>
    api.get('/parcels/parcels/calculate_pickup_fee/', {
      params: { distance_km: distanceKm, is_priority: isPriority },
    }),
  calculatePickupFeeWithDistance: (customerLat, customerLon, branchId, isPriority) =>
    api.get('/parcels/parcels/calculate_pickup_fee_with_distance/', {
      params: { 
        customer_lat: customerLat, 
        customer_lon: customerLon,
        branch_id: branchId,
        is_priority: isPriority 
      },
    }),
  // Public tracking
  track: (trackingNumber) =>
    api.get('/parcels/parcels/track/', {
      params: { tracking_number: trackingNumber },
    }),
  // QR Code scanning
  scanQR: (trackingNumber) =>
    api.get('/parcels/parcels/scan_qr/', {
      params: { tracking_number: trackingNumber },
    }),
  // Dashboard stats
  getDashboardStats: () => api.get('/parcels/parcels/dashboard_stats/'),
  getStaffDashboardStats: () => api.get('/parcels/parcels/staff_dashboard_stats/'),
  getDriverDashboardStats: () => api.get('/parcels/parcels/driver_dashboard_stats/'),
};

// ===== Parcel Image Endpoints =====
export const parcelImageService = {
  list: (params) => api.get('/parcels/parcel-images/', { params }),
  create: (data) => {
    const formData = new FormData();
    formData.append('parcel', data.parcel);
    formData.append('image', data.image);
    formData.append('image_type', data.imageType);
    if (data.description) formData.append('description', data.description);
    return api.post('/parcels/parcel-images/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id) => api.delete(`/parcels/parcel-images/${id}/`),
};

// ===== Transit Update Endpoints =====
export const transitUpdateService = {
  list: (params) => api.get('/parcels/transit-updates/', { params }),
  create: (data) => api.post('/parcels/transit-updates/', data),
};

// ===== Pickup Request Endpoints =====
export const pickupRequestService = {
  list: (params) => api.get('/parcels/pickup-requests/', { params }),
  create: (data) => api.post('/parcels/pickup-requests/', data),
  retrieve: (id) => api.get(`/parcels/pickup-requests/${id}/`),
  approve: (id) => api.post(`/parcels/pickup-requests/${id}/approve/`),
  reject: (id, reason) => api.post(`/parcels/pickup-requests/${id}/reject/`, { reason }),
  schedulePickup: (id, driverId, pickupDate) =>
    api.post(`/parcels/pickup-requests/${id}/schedule_pickup/`, { 
      driver_id: driverId, pickup_date: pickupDate 
    }),
  confirmPickup: (id) => api.post(`/parcels/pickup-requests/${id}/confirm_pickup/`),
  createParcel: (id, data) => api.post(`/parcels/pickup-requests/${id}/create_parcel/`, data),
  pendingCount: () => api.get('/parcels/pickup-requests/pending_count/'),
};

// ===== Delivery Proof Endpoints =====
export const deliveryProofService = {
  list: (params) => api.get('/parcels/delivery-proofs/', { params }),
  create: (data) => {
    const formData = new FormData();
    formData.append('parcel', data.parcel);
    formData.append('proof_image', data.proofImage);
    if (data.deliveryNotes) formData.append('delivery_notes', data.deliveryNotes);
    if (data.signatureImage) formData.append('signature_image', data.signatureImage);
    return api.post('/parcels/delivery-proofs/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// ===== Vehicle Endpoints =====
export const vehicleService = {
  list: (params) => api.get('/vehicles/vehicles/', { params }),
  create: (data) => api.post('/vehicles/vehicles/', data),
  retrieve: (id) => api.get(`/vehicles/vehicles/${id}/`),
  update: (id, data) => api.put(`/vehicles/vehicles/${id}/`, data),
  delete: (id) => api.delete(`/vehicles/vehicles/${id}/`),
  assignDriver: (id, driverId) =>
    api.post(`/vehicles/vehicles/${id}/assign_driver/`, { driver_id: driverId }),
  unassignDriver: (id) =>
    api.post(`/vehicles/vehicles/${id}/unassign_driver/`),
  updateLocation: (id, latitude, longitude, locationName) =>
    api.post(`/vehicles/vehicles/${id}/update_location/`, {
      latitude,
      longitude,
      location_name: locationName,
    }),
  getParcels: (id) => api.get(`/vehicles/vehicles/${id}/parcels/`),
  getAvailable: () => api.get('/vehicles/vehicles/available/'),
};

// ===== Vehicle Maintenance Endpoints =====
export const vehicleMaintenanceService = {
  list: (params) => api.get('/vehicles/maintenance/', { params }),
  create: (data) => api.post('/vehicles/maintenance/', data),
  retrieve: (id) => api.get(`/vehicles/maintenance/${id}/`),
  update: (id, data) => api.put(`/vehicles/maintenance/${id}/`, data),
  delete: (id) => api.delete(`/vehicles/maintenance/${id}/`),
};

// ===== Audit Log Endpoints =====
export const auditLogService = {
  list: (params) => api.get('/audit/', { params }),
};

// ===== Notification Endpoints =====
export const notificationService = {
  list: (params) => api.get('/notifications/notifications/', { params }),
  retrieve: (id) => api.get(`/notifications/notifications/${id}/`),
  markRead: (id) => api.post(`/notifications/notifications/${id}/mark_read/`),
  markAllRead: () => api.post('/notifications/notifications/mark_all_read/'),
  unreadCount: () => api.get('/notifications/notifications/unread_count/'),
  unread: () => api.get('/notifications/notifications/unread/'),
  // Preferences
  getPreferences: () => api.get('/notifications/preferences/'),
  updatePreferences: (data) => api.patch('/notifications/preferences/', data),
};

export default api;
