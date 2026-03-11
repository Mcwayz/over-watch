/**
 * Driver Dashboard Component
 * Full implementation with parcel management, bulk in-transit, and delivery confirmation
 */

import React, { useState, useEffect } from 'react';
import { parcelService, driverService, pickupRequestService } from '../services/api';

const DriverDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('parcels');
  const [myParcels, setMyParcels] = useState([]);
  const [pendingPickups, setPendingPickups] = useState([]);
  
  // Bulk operations
  const [selectedParcels, setSelectedParcels] = useState([]);
  const [currentLocation, setCurrentLocation] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  
  // QR Scanner input
  const [scanInput, setScanInput] = useState('');
  const [scannedParcel, setScannedParcel] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, parcelsRes, pickupsRes] = await Promise.all([
        parcelService.getDriverDashboardStats(),
        driverService.myVehicleParcels(),
        driverService.myPendingPickups(),
      ]);

      setStats(statsRes.data);
      setMyParcels(parcelsRes.data || []);
      setPendingPickups(pickupsRes.data || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScanQR = async () => {
    if (!scanInput.trim()) {
      alert('Please enter a tracking number');
      return;
    }
    try {
      const response = await parcelService.scanQR(scanInput.trim());
      setScannedParcel(response.data);
      alert('Parcel found!');
    } catch (error) {
      alert('Parcel not found');
      setScannedParcel(null);
    }
  };

  const handleBulkInTransit = async () => {
    if (selectedParcels.length === 0) {
      alert('Please select parcels to update');
      return;
    }
    try {
      await parcelService.bulkInTransit(
        selectedParcels,
        currentLocation || 'In Transit',
        latitude || 0,
        longitude || 0
      );
      alert('Parcels marked as in transit!');
      setSelectedParcels([]);
      fetchDashboardData();
    } catch (error) {
      alert('Error updating parcels: ' + error.message);
    }
  };

  const handleMarkInTransit = async (parcelId) => {
    try {
      await parcelService.markInTransit(
        parcelId,
        currentLocation || 'In Transit',
        latitude || 0,
        longitude || 0,
        'Driver marked as in transit'
      );
      alert('Parcel marked as in transit!');
      fetchDashboardData();
    } catch (error) {
      alert('Error updating parcel: ' + error.message);
    }
  };

  const handleConfirmDelivery = async (parcelId) => {
    const notes = prompt('Enter delivery notes (optional):');
    try {
      await parcelService.confirmDelivery(parcelId, null, notes || '');
      alert('Delivery confirmed!');
      fetchDashboardData();
    } catch (error) {
      alert('Error confirming delivery: ' + error.message);
    }
  };

  const handleOutForDelivery = async (parcelId) => {
    try {
      await parcelService.outForDelivery(parcelId, 'Out for delivery');
      alert('Parcel marked as out for delivery!');
      fetchDashboardData();
    } catch (error) {
      alert('Error updating parcel: ' + error.message);
    }
  };

  const handleConfirmPickup = async (pickupId) => {
    try {
      await pickupRequestService.confirmPickup(pickupId);
      alert('Pickup confirmed!');
      fetchDashboardData();
    } catch (error) {
      alert('Error confirming pickup: ' + error.message);
    }
  };

  const toggleParcelSelection = (parcelId) => {
    setSelectedParcels(prev => 
      prev.includes(parcelId) 
        ? prev.filter(id => id !== parcelId)
        : [...prev, parcelId]
    );
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toString());
          setLongitude(position.coords.longitude.toString());
          alert('Location captured!');
        },
        (error) => {
          alert('Error getting location: ' + error.message);
        }
      );
    } else {
      alert('Geolocation is not supported by this browser');
    }
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
      <h1>Driver Dashboard</h1>

      {/* Stats Cards */}
      {stats && (
        <div style={styles.statsGrid}>
          <StatCard title="Assigned Parcels" value={stats.assigned_parcels} color="#3498db" />
          <StatCard title="Out for Delivery" value={stats.out_for_delivery} color="#e74c3c" />
          <StatCard title="Delivered Today" value={stats.delivered_today} color="#2ecc71" />
          <StatCard title="Total Deliveries" value={stats.total_deliveries} color="#9b59b6" />
        </div>
      )}

      {/* Tab Navigation */}
      <div style={styles.tabs}>
        <button style={activeTab === 'parcels' ? styles.activeTab : styles.tab} onClick={() => setActiveTab('parcels')}>
          My Parcels
        </button>
        <button style={activeTab === 'pickups' ? styles.activeTab : styles.tab} onClick={() => setActiveTab('pickups')}>
          Pickups ({pendingPickups.length})
        </button>
        <button style={activeTab === 'scan' ? styles.activeTab : styles.tab} onClick={() => setActiveTab('scan')}>
          Scan QR
        </button>
      </div>

      {/* Location Update */}
      <div style={styles.locationBar}>
        <h3>Current Location</h3>
        <div style={styles.locationInputs}>
          <input type="text" placeholder="Location name" value={currentLocation} onChange={(e) => setCurrentLocation(e.target.value)} style={styles.input} />
          <input type="text" placeholder="Latitude" value={latitude} onChange={(e) => setLatitude(e.target.value)} style={styles.smallInput} />
          <input type="text" placeholder="Longitude" value={longitude} onChange={(e) => setLongitude(e.target.value)} style={styles.smallInput} />
          <button style={styles.locationButton} onClick={getCurrentLocation}>📍 Get GPS</button>
        </div>
      </div>

      {/* Parcels Tab */}
      {activeTab === 'parcels' && (
        <div style={styles.content}>
          <div style={styles.bulkActions}>
            <span style={styles.selectedCount}>{selectedParcels.length} parcel(s) selected</span>
            <button style={styles.actionButton} onClick={handleBulkInTransit}>Bulk Mark In Transit</button>
          </div>

          <div style={styles.card}>
            <h3>My Assigned Parcels</h3>
            <div style={styles.parcelList}>
              {myParcels.length === 0 ? (
                <p style={styles.emptyMessage}>No parcels assigned to you</p>
              ) : (
                myParcels.map((parcel) => (
                  <div key={parcel.id} style={styles.parcelCard}>
                    <div style={styles.parcelHeader}>
                      <div>
                        <strong>{parcel.tracking_number}</strong>
                        <span style={getStatusStyle(parcel.status)}>{parcel.status_display}</span>
                      </div>
                      {(parcel.status === 'LOADED' || parcel.status === 'DISPATCHED') && (
                        <input type="checkbox" checked={selectedParcels.includes(parcel.id)} onChange={() => toggleParcelSelection(parcel.id)} />
                      )}
                    </div>
                    <div style={styles.parcelDetails}>
                      <p><strong>To:</strong> {parcel.receiver_name}</p>
                      <p><strong>Address:</strong> {parcel.receiver_address}, {parcel.receiver_city}</p>
                      <p><strong>Weight:</strong> {parcel.weight_kg} kg</p>
                    </div>
                    <div style={styles.parcelActions}>
                      {(parcel.status === 'LOADED' || parcel.status === 'DISPATCHED') && (
                        <button style={styles.actionButton} onClick={() => handleMarkInTransit(parcel.id)}>Mark In Transit</button>
                      )}
                      {parcel.status === 'IN_TRANSIT' && (
                        <button style={{...styles.actionButton, backgroundColor: '#16a085'}} onClick={() => handleOutForDelivery(parcel.id)}>Out for Delivery</button>
                      )}
                      {parcel.status === 'OUT_FOR_DELIVERY' && (
                        <button style={{...styles.actionButton, backgroundColor: '#2ecc71'}} onClick={() => handleConfirmDelivery(parcel.id)}>Confirm Delivery</button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Pickups Tab */}
      {activeTab === 'pickups' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <h3>Scheduled Pickups</h3>
            {pendingPickups.length === 0 ? (
              <p style={styles.emptyMessage}>No pending pickups</p>
            ) : (
              <div style={styles.pickupList}>
                {pendingPickups.map((pickup) => (
                  <div key={pickup.id} style={styles.pickupCard}>
                    <div style={styles.pickupDetails}>
                      <p><strong>Address:</strong> {pickup.pickup_address}</p>
                      <p><strong>Description:</strong> {pickup.parcel_description}</p>
                      <p><strong>Weight:</strong> {pickup.weight_kg} kg</p>
                      <p><strong>Preferred Date:</strong> {pickup.preferred_pickup_date}</p>
                    </div>
                    <button style={{...styles.actionButton, backgroundColor: '#2ecc71'}} onClick={() => handleConfirmPickup(pickup.id)}>Confirm Pickup</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* QR Scanner Tab */}
      {activeTab === 'scan' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <h3>Scan Parcel QR Code</h3>
            <div style={styles.scanForm}>
              <input type="text" placeholder="Enter tracking number" value={scanInput} onChange={(e) => setScanInput(e.target.value)} style={styles.scanInput} />
              <button style={styles.scanButton} onClick={handleScanQR}>Scan</button>
            </div>

            {scannedParcel && (
              <div style={styles.scannedParcel}>
                <h4>Parcel Details</h4>
                <div style={styles.detailGrid}>
                  <div><strong>Tracking #:</strong> {scannedParcel.tracking_number}</div>
                  <div><strong>Status:</strong> <span style={getStatusStyle(scannedParcel.status)}>{scannedParcel.status_display}</span></div>
                  <div><strong>To:</strong> {scannedParcel.receiver_name}</div>
                  <div><strong>Address:</strong> {scannedParcel.receiver_address}</div>
                  <div><strong>Weight:</strong> {scannedParcel.weight_kg} kg</div>
                  <div><strong>Origin:</strong> {scannedParcel.origin_branch_name}</div>
                  <div><strong>Destination:</strong> {scannedParcel.destination_branch_name}</div>
                </div>
                <div style={styles.scanActions}>
                  {(scannedParcel.status === 'LOADED' || scannedParcel.status === 'DISPATCHED') && (
                    <button style={styles.actionButton} onClick={() => handleMarkInTransit(scannedParcel.id)}>Mark In Transit</button>
                  )}
                  {scannedParcel.status === 'IN_TRANSIT' && (
                    <button style={{...styles.actionButton, backgroundColor: '#16a085'}} onClick={() => handleOutForDelivery(scannedParcel.id)}>Out for Delivery</button>
                  )}
                  {scannedParcel.status === 'OUT_FOR_DELIVERY' && (
                    <button style={{...styles.actionButton, backgroundColor: '#2ecc71'}} onClick={() => handleConfirmDelivery(scannedParcel.id)}>Confirm Delivery</button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ title, value, color }) => (
  <div style={{ ...styles.statCard, borderLeftColor: color }}>
    <h4 style={{ color }}>{title}</h4>
    <p style={{ fontSize: '28px', color, margin: '10px 0' }}>{value}</p>
  </div>
);

const styles = {
  container: { padding: '20px', maxWidth: '1200px', margin: '0 auto' },
  loading: { textAlign: 'center', padding: '40px', fontSize: '18px' },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '20px', marginBottom: '20px' },
  statCard: { backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', borderLeft: '4px solid' },
  tabs: { display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #eee', paddingBottom: '10px' },
  tab: { padding: '10px 20px', backgroundColor: 'transparent', border: 'none', cursor: 'pointer', fontSize: '14px', color: '#666', borderRadius: '4px' },
  activeTab: { padding: '10px 20px', backgroundColor: '#3498db', color: 'white', border: 'none', cursor: 'pointer', fontSize: '14px', borderRadius: '4px' },
  locationBar: { backgroundColor: 'white', padding: '15px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', marginBottom: '20px' },
  locationInputs: { display: 'flex', gap: '10px', flexWrap: 'wrap' },
  input: { padding: '10px', borderRadius: '4px', border: '1px solid #ddd', flex: 1, minWidth: '200px' },
  smallInput: { padding: '10px', borderRadius: '4px', border: '1px solid #ddd', width: '100px' },
  locationButton: { padding: '10px 20px', backgroundColor: '#1abc9c', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  content: { display: 'flex', flexDirection: 'column', gap: '20px' },
  bulkActions: { display: 'flex', gap: '15px', alignItems: 'center', padding: '15px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' },
  selectedCount: { fontWeight: 'bold', color: '#666' },
  actionButton: { padding: '10px 20px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  card: { backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' },
  parcelList: { display: 'flex', flexDirection: 'column', gap: '15px' },
  parcelCard: { border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#f8f9fa' },
  parcelHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', gap: '15px' },
  parcelDetails: { marginBottom: '10px' },
  parcelActions: { display: 'flex', gap: '10px', flexWrap: 'wrap' },
  pickupList: { display: 'flex', flexDirection: 'column', gap: '15px' },
  pickupCard: { border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#f8f9fa', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  pickupDetails: { flex: 1 },
  scanForm: { display: 'flex', gap: '10px', marginBottom: '20px' },
  scanInput: { flex: 1, padding: '15px', borderRadius: '4px', border: '1px solid #ddd', fontSize: '16px' },
  scanButton: { padding: '15px 30px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' },
  scannedParcel: { border: '2px solid #3498db', borderRadius: '8px', padding: '20px', backgroundColor: '#f8f9fa' },
  detailGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', margin: '15px 0' },
  scanActions: { display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '15px' },
  emptyMessage: { textAlign: 'center', padding: '40px', color: '#666' },
};

export default DriverDashboard;

