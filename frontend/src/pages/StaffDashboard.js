/**
 * Staff Dashboard Component
 * Full implementation with parcel registration, pickup requests, and bulk operations
 */

import React, { useState, useEffect } from 'react';
import { parcelService, pickupRequestService, branchService, vehicleService, driverService } from '../services/api';

const StaffDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('parcels');
  const [parcels, setParcels] = useState([]);
  const [pickupRequests, setPickupRequests] = useState([]);
  const [branches, setBranches] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  
  // Form states
  const [showParcelForm, setShowParcelForm] = useState(false);
  const [newParcel, setNewParcel] = useState({
    receiver_name: '',
    receiver_phone: '',
    receiver_address: '',
    receiver_city: '',
    receiver_postal_code: '',
    destination_branch: '',
    weight_kg: '',
    declared_value: '',
  });
  
  // Bulk selection
  const [selectedParcels, setSelectedParcels] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, parcelsRes, pickupsRes, branchesRes, vehiclesRes] = await Promise.all([
        parcelService.getStaffDashboardStats(),
        parcelService.list({ limit: 100 }),
        pickupRequestService.list({ limit: 100 }),
        branchService.list({ limit: 100 }),
        vehicleService.list({ limit: 100 }),
      ]);

      setStats(statsRes.data);
      setParcels(parcelsRes.data.results || []);
      setPickupRequests(pickupsRes.data.results || []);
      setBranches(branchesRes.data.results || []);
      setVehicles(vehiclesRes.data.results || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateParcel = async (e) => {
    e.preventDefault();
    try {
      await parcelService.create({
        ...newParcel,
        submission_type: 'BRANCH_DROPOFF',
        destination_branch: newParcel.destination_branch,
      });
      alert('Parcel created successfully!');
      setShowParcelForm(false);
      setNewParcel({
        receiver_name: '',
        receiver_phone: '',
        receiver_address: '',
        receiver_city: '',
        receiver_postal_code: '',
        destination_branch: '',
        weight_kg: '',
        declared_value: '',
      });
      fetchDashboardData();
    } catch (error) {
      alert('Error creating parcel: ' + error.message);
    }
  };

  const handleSchedulePickup = async (pickupId, driverId) => {
    try {
      const pickupDate = new Date().toISOString().split('T')[0];
      await pickupRequestService.schedulePickup(pickupId, driverId, pickupDate);
      alert('Pickup scheduled successfully!');
      fetchDashboardData();
    } catch (error) {
      alert('Error scheduling pickup: ' + error.message);
    }
  };

  const handleApprovePickup = async (pickupId) => {
    try {
      await pickupRequestService.approve(pickupId);
      alert('Pickup approved!');
      fetchDashboardData();
    } catch (error) {
      alert('Error approving pickup: ' + error.message);
    }
  };

  const handleRejectPickup = async (pickupId) => {
    const reason = prompt('Enter rejection reason:');
    if (reason) {
      try {
        await pickupRequestService.reject(pickupId, reason);
        alert('Pickup rejected!');
        fetchDashboardData();
      } catch (error) {
        alert('Error rejecting pickup: ' + error.message);
      }
    }
  };

  const handleBulkLoad = async () => {
    if (selectedParcels.length === 0) {
      alert('Please select parcels to load');
      return;
    }
    try {
      await parcelService.bulkLoad(selectedParcels, selectedVehicle || null);
      alert('Parcels loaded successfully!');
      setSelectedParcels([]);
      fetchDashboardData();
    } catch (error) {
      alert('Error loading parcels: ' + error.message);
    }
  };

  const handleBulkDispatch = async () => {
    if (selectedParcels.length === 0) {
      alert('Please select parcels to dispatch');
      return;
    }
    try {
      await parcelService.bulkDispatch(selectedParcels);
      alert('Parcels dispatched successfully!');
      setSelectedParcels([]);
      fetchDashboardData();
    } catch (error) {
      alert('Error dispatching parcels: ' + error.message);
    }
  };

  const toggleParcelSelection = (parcelId) => {
    setSelectedParcels(prev => 
      prev.includes(parcelId) 
        ? prev.filter(id => id !== parcelId)
        : [...prev, parcelId]
    );
  };

  const getStatusStyle = (status) => {
    const colors = {
      REGISTERED: '#9b59b6',
      RECEIVED: '#3498db',
      LOADED: '#f39c12',
      DISPATCHED: '#e67e22',
      IN_TRANSIT: '#1abc9c',
      ARRIVED: '#16a085',
      OUT_FOR_DELIVERY: '#e74c3c',
      DELIVERED: '#2ecc71',
    };
    return {
      display: 'inline-block',
      padding: '5px 10px',
      borderRadius: '4px',
      backgroundColor: colors[status] || '#95a5a6',
      color: 'white',
      fontSize: '12px',
    };
  };

  if (loading) return <div style={styles.loading}>Loading...</div>;

  return (
    <div style={styles.container}>
      <h1>Staff Dashboard</h1>

      {/* Stats Cards */}
      {stats && (
        <div style={styles.statsGrid}>
          <StatCard title="Incoming Parcels" value={stats.incoming_parcels} color="#3498db" />
          <StatCard title="Outgoing Parcels" value={stats.outgoing_parcels} color="#2ecc71" />
          <StatCard title="Pending Pickups" value={stats.pending_pickups} color="#f39c12" />
          <StatCard title="Received Today" value={stats.today_received} color="#9b59b6" />
        </div>
      )}

      {/* Tab Navigation */}
      <div style={styles.tabs}>
        <button 
          style={activeTab === 'parcels' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('parcels')}
        >
          Parcels
        </button>
        <button 
          style={activeTab === 'pickups' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('pickups')}
        >
          Pickup Requests
        </button>
        <button 
          style={activeTab === 'register' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('register')}
        >
          Register Parcel
        </button>
      </div>

      {/* Parcels Tab */}
      {activeTab === 'parcels' && (
        <div style={styles.content}>
          {/* Bulk Actions */}
          <div style={styles.bulkActions}>
            <select 
              style={styles.select}
              value={selectedVehicle}
              onChange={(e) => setSelectedVehicle(e.target.value)}
            >
              <option value="">Select Vehicle (optional)</option>
              {vehicles.map(v => (
                <option key={v.id} value={v.id}>{v.vehicle_number} - {v.vehicle_name}</option>
              ))}
            </select>
            <button style={styles.actionButton} onClick={handleBulkLoad}>
              Bulk Load ({selectedParcels.length})
            </button>
            <button style={{...styles.actionButton, backgroundColor: '#e67e22'}} onClick={handleBulkDispatch}>
              Bulk Dispatch
            </button>
          </div>

          <div style={styles.card}>
            <h3>All Parcels</h3>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={{width: '40px'}}></th>
                  <th>Tracking #</th>
                  <th>Receiver</th>
                  <th>Destination</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {parcels.map((parcel) => (
                  <tr key={parcel.id}>
                    <td>
                      {parcel.status === 'RECEIVED' && (
                        <input 
                          type="checkbox"
                          checked={selectedParcels.includes(parcel.id)}
                          onChange={() => toggleParcelSelection(parcel.id)}
                        />
                      )}
                    </td>
                    <td>{parcel.tracking_number}</td>
                    <td>{parcel.receiver_name}</td>
                    <td>{parcel.destination_branch_name}</td>
                    <td>
                      <span style={getStatusStyle(parcel.status)}>
                        {parcel.status_display}
                      </span>
                    </td>
                    <td>
                      <button style={styles.smallButton} onClick={() => window.location.href = `/parcels/${parcel.id}`}>
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pickup Requests Tab */}
      {activeTab === 'pickups' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <h3>Pickup Requests</h3>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Pickup Address</th>
                  <th>Weight</th>
                  <th>Destination</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pickupRequests.map((pickup) => (
                  <tr key={pickup.id}>
                    <td>{pickup.customer_name}</td>
                    <td>{pickup.pickup_address}</td>
                    <td>{pickup.weight_kg} kg</td>
                    <td>{pickup.destination_branch_name}</td>
                    <td>
                      <span style={getStatusStyle(pickup.status)}>
                        {pickup.status_display}
                      </span>
                    </td>
                    <td>
                      {pickup.status === 'PENDING' && (
                        <>
                          <button 
                            style={{...styles.smallButton, backgroundColor: '#2ecc71'}}
                            onClick={() => handleApprovePickup(pickup.id)}
                          >
                            Approve
                          </button>
                          <button 
                            style={{...styles.smallButton, backgroundColor: '#e74c3c'}}
                            onClick={() => handleRejectPickup(pickup.id)}
                          >
                            Reject
                          </button>
                        </>
                      )}
                      {pickup.status === 'APPROVED' && (
                        <select 
                          style={styles.smallSelect}
                          onChange={(e) => handleSchedulePickup(pickup.id, e.target.value)}
                          defaultValue=""
                        >
                          <option value="" disabled>Schedule Driver</option>
                          {drivers.filter(d => d.is_active).map(d => (
                            <option key={d.id} value={d.id}>{d.user?.first_name} {d.user?.last_name}</option>
                          ))}
                        </select>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Register Parcel Tab */}
      {activeTab === 'register' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <h3>Register New Parcel (Branch Drop-Off)</h3>
            <form onSubmit={handleCreateParcel} style={styles.form}>
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label>Receiver Name *</label>
                  <input
                    type="text"
                    required
                    value={newParcel.receiver_name}
                    onChange={(e) => setNewParcel({...newParcel, receiver_name: e.target.value})}
                    style={styles.input}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label>Receiver Phone *</label>
                  <input
                    type="text"
                    required
                    value={newParcel.receiver_phone}
                    onChange={(e) => setNewParcel({...newParcel, receiver_phone: e.target.value})}
                    style={styles.input}
                  />
                </div>
              </div>
              
              <div style={styles.formGroup}>
                <label>Receiver Address *</label>
                <textarea
                  required
                  value={newParcel.receiver_address}
                  onChange={(e) => setNewParcel({...newParcel, receiver_address: e.target.value})}
                  style={styles.textarea}
                />
              </div>
              
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label>City *</label>
                  <input
                    type="text"
                    required
                    value={newParcel.receiver_city}
                    onChange={(e) => setNewParcel({...newParcel, receiver_city: e.target.value})}
                    style={styles.input}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label>Postal Code *</label>
                  <input
                    type="text"
                    required
                    value={newParcel.receiver_postal_code}
                    onChange={(e) => setNewParcel({...newParcel, receiver_postal_code: e.target.value})}
                    style={styles.input}
                  />
                </div>
              </div>
              
              <div style={styles.formGroup}>
                <label>Destination Branch *</label>
                <select
                  required
                  value={newParcel.destination_branch}
                  onChange={(e) => setNewParcel({...newParcel, destination_branch: e.target.value})}
                  style={styles.select}
                >
                  <option value="">Select Branch</option>
                  {branches.map(branch => (
                    <option key={branch.id} value={branch.id}>{branch.name} - {branch.city}</option>
                  ))}
                </select>
              </div>
              
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label>Weight (kg) *</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={newParcel.weight_kg}
                    onChange={(e) => setNewParcel({...newParcel, weight_kg: e.target.value})}
                    style={styles.input}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label>Declared Value</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newParcel.declared_value}
                    onChange={(e) => setNewParcel({...newParcel, declared_value: e.target.value})}
                    style={styles.input}
                  />
                </div>
              </div>
              
              <button type="submit" style={styles.submitButton}>
                Register Parcel
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper components
const StatCard = ({ title, value, color }) => (
  <div style={{ ...styles.statCard, borderLeftColor: color }}>
    <h4 style={{ color }}>{title}</h4>
    <p style={{ fontSize: '28px', color, margin: '10px 0' }}>{value}</p>
  </div>
);

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '18px',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '20px',
    marginBottom: '20px',
  },
  statCard: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    borderLeft: '4px solid',
  },
  tabs: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
    borderBottom: '2px solid #eee',
    paddingBottom: '10px',
  },
  tab: {
    padding: '10px 20px',
    backgroundColor: 'transparent',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#666',
    borderRadius: '4px',
  },
  activeTab: {
    padding: '10px 20px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    borderRadius: '4px',
  },
  content: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  bulkActions: {
    display: 'flex',
    gap: '10px',
    padding: '15px',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  actionButton: {
    padding: '10px 20px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  select: {
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    minWidth: '200px',
  },
  card: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  smallButton: {
    padding: '5px 10px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    marginRight: '5px',
  },
  smallSelect: {
    padding: '5px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '12px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
    maxWidth: '600px',
  },
  formRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '15px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  input: {
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '14px',
  },
  textarea: {
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '14px',
    minHeight: '80px',
  },
  submitButton: {
    padding: '15px',
    backgroundColor: '#2ecc71',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
  },
};

export default StaffDashboard;

