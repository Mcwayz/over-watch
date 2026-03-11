/**
 * Customer Portal Component
 * Full implementation with parcel tracking, pickup requests, and parcel history
 */

import React, { useState, useEffect } from 'react';
import { parcelService, pickupRequestService, branchService } from '../services/api';

const CustomerPortal = () => {
  const [myParcels, setMyParcels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('parcels');
  const [trackingNumber, setTrackingNumber] = useState('');
  const [selectedParcel, setSelectedParcel] = useState(null);
  const [pickupRequests, setPickupRequests] = useState([]);
  const [branches, setBranches] = useState([]);
  
  // Pickup request form
  const [showPickupForm, setShowPickupForm] = useState(false);
  const [pickupRequest, setPickupRequest] = useState({
    pickup_address: '',
    parcel_description: '',
    weight_kg: '',
    destination_branch: '',
    preferred_pickup_date: '',
    is_priority: false,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [parcelsRes, pickupsRes, branchesRes] = await Promise.all([
        parcelService.list({ limit: 100 }),
        pickupRequestService.list({ limit: 100 }),
        branchService.list({ limit: 100 }),
      ]);

      setMyParcels(parcelsRes.data.results || []);
      setPickupRequests(pickupsRes.data.results || []);
      setBranches(branchesRes.data.results || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrackParcel = async (e) => {
    e.preventDefault();
    try {
      const response = await parcelService.track(trackingNumber);
      setSelectedParcel(response.data);
    } catch (error) {
      alert('Parcel not found');
      setSelectedParcel(null);
    }
  };

  const handleCreatePickupRequest = async (e) => {
    e.preventDefault();
    try {
      await pickupRequestService.create(pickupRequest);
      alert('Pickup request submitted successfully!');
      setShowPickupForm(false);
      setPickupRequest({
        pickup_address: '',
        parcel_description: '',
        weight_kg: '',
        destination_branch: '',
        preferred_pickup_date: '',
        is_priority: false,
      });
      fetchData();
    } catch (error) {
      alert('Error creating pickup request: ' + error.message);
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
      <h1>Customer Portal</h1>

      {/* Tab Navigation */}
      <div style={styles.tabs}>
        <button style={activeTab === 'parcels' ? styles.activeTab : styles.tab} onClick={() => setActiveTab('parcels')}>
          My Parcels
        </button>
        <button style={activeTab === 'tracking' ? styles.activeTab : styles.tab} onClick={() => setActiveTab('tracking')}>
          Track Parcel
        </button>
        <button style={activeTab === 'pickups' ? styles.activeTab : styles.tab} onClick={() => setActiveTab('pickups')}>
          Pickup Requests
        </button>
      </div>

      {/* My Parcels Tab */}
      {activeTab === 'parcels' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <h3>My Parcels</h3>
            {myParcels.length === 0 ? (
              <p style={styles.emptyMessage}>You haven't sent any parcels yet</p>
            ) : (
              <div style={styles.parcelList}>
                {myParcels.map((parcel) => (
                  <div key={parcel.id} style={styles.parcelCard}>
                    <div style={styles.parcelHeader}>
                      <strong>{parcel.tracking_number}</strong>
                      <span style={getStatusStyle(parcel.status)}>{parcel.status_display}</span>
                    </div>
                    <div style={styles.parcelDetails}>
                      <p><strong>To:</strong> {parcel.receiver_name}</p>
                      <p><strong>Destination:</strong> {parcel.destination_branch_name}</p>
                      <p><strong>Weight:</strong> {parcel.weight_kg} kg</p>
                      <p><strong>Total:</strong> ${parcel.total_price}</p>
                    </div>
                    <button style={styles.smallButton} onClick={() => { setSelectedParcel(parcel); setActiveTab('tracking'); }}>
                      View Details
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Track Parcel Tab */}
      {activeTab === 'tracking' && (
        <div style={styles.content}>
          <div style={styles.searchSection}>
            <h3>Track Your Parcel</h3>
            <form onSubmit={handleTrackParcel} style={styles.searchForm}>
              <input
                type="text"
                placeholder="Enter tracking number"
                value={trackingNumber}
                onChange={(e) => setTrackingNumber(e.target.value)}
                style={styles.input}
              />
              <button type="submit" style={styles.button}>
                Track
              </button>
            </form>
          </div>

          {selectedParcel && (
            <div style={styles.trackingResult}>
              <h3>Parcel Details</h3>
              <div style={styles.detailGrid}>
                <div><strong>Tracking Number:</strong> {selectedParcel.tracking_number}</div>
                <div><strong>Status:</strong> <span style={getStatusStyle(selectedParcel.status)}>{selectedParcel.status_display}</span></div>
                <div><strong>Receiver:</strong> {selectedParcel.receiver_name}</div>
                <div><strong>Phone:</strong> {selectedParcel.receiver_phone}</div>
                <div><strong>Address:</strong> {selectedParcel.receiver_address}</div>
                <div><strong>Weight:</strong> {selectedParcel.weight_kg} kg</div>
                <div><strong>Submission Type:</strong> {selectedParcel.submission_type_display}</div>
                <div><strong>Total Price:</strong> ${selectedParcel.total_price}</div>
                <div><strong>Created:</strong> {new Date(selectedParcel.created_at).toLocaleString()}</div>
                {selectedParcel.delivered_at && <div><strong>Delivered:</strong> {new Date(selectedParcel.delivered_at).toLocaleString()}</div>}
              </div>

              {/* Tracking Timeline */}
              {selectedParcel.tracking_history && selectedParcel.tracking_history.length > 0 && (
                <div style={styles.timeline}>
                  <h4>Tracking History</h4>
                  {selectedParcel.tracking_history.map((update, index) => (
                    <div key={update.id} style={styles.timelineItem}>
                      <div style={styles.timelineDot}></div>
                      <div style={styles.timelineContent}>
                        <p style={styles.timelineStatus}>{update.status_display}</p>
                        {update.notes && <p style={styles.timelineNotes}>{update.notes}</p>}
                        <p style={styles.timestamp}>{new Date(update.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Transit Updates */}
              {selectedParcel.transit_updates && selectedParcel.transit_updates.length > 0 && (
                <div style={styles.timeline}>
                  <h4>Transit Updates</h4>
                  {selectedParcel.transit_updates.map((update) => (
                    <div key={update.id} style={styles.timelineItem}>
                      <div style={styles.timelineDot}></div>
                      <div style={styles.timelineContent}>
                        <p style={styles.timelineStatus}>{update.location_name}</p>
                        <p style={styles.timestamp}>{new Date(update.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Pickup Requests Tab */}
      {activeTab === 'pickups' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <h3>My Pickup Requests</h3>
              <button style={styles.primaryButton} onClick={() => setShowPickupForm(true)}>Request Pickup</button>
            </div>

            {pickupRequests.length === 0 ? (
              <p style={styles.emptyMessage}>No pickup requests</p>
            ) : (
              <div style={styles.pickupList}>
                {pickupRequests.map((pickup) => (
                  <div key={pickup.id} style={styles.pickupCard}>
                    <div style={styles.pickupHeader}>
                      <strong>Pickup Request</strong>
                      <span style={getStatusStyle(pickup.status)}>{pickup.status_display}</span>
                    </div>
                    <div style={styles.pickupDetails}>
                      <p><strong>Address:</strong> {pickup.pickup_address}</p>
                      <p><strong>Description:</strong> {pickup.parcel_description}</p>
                      <p><strong>Weight:</strong> {pickup.weight_kg} kg</p>
                      <p><strong>Destination:</strong> {pickup.destination_branch_name}</p>
                      <p><strong>Preferred Date:</strong> {pickup.preferred_pickup_date}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Pickup Request Modal */}
      {showPickupForm && (
        <div style={styles.modal}>
          <div style={styles.modalContent}>
            <div style={styles.modalHeader}>
              <h2>Request Pickup</h2>
              <button style={styles.closeButton} onClick={() => setShowPickupForm(false)}>×</button>
            </div>
            <form onSubmit={handleCreatePickupRequest} style={styles.form}>
              <div style={styles.formGroup}>
                <label>Pickup Address *</label>
                <textarea
                  required
                  value={pickupRequest.pickup_address}
                  onChange={(e) => setPickupRequest({...pickupRequest, pickup_address: e.target.value})}
                  style={styles.textarea}
                />
              </div>
              
              <div style={styles.formGroup}>
                <label>Parcel Description *</label>
                <textarea
                  required
                  value={pickupRequest.parcel_description}
                  onChange={(e) => setPickupRequest({...pickupRequest, parcel_description: e.target.value})}
                  style={styles.textarea}
                />
              </div>
              
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label>Weight (kg) *</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={pickupRequest.weight_kg}
                    onChange={(e) => setPickupRequest({...pickupRequest, weight_kg: e.target.value})}
                    style={styles.input}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label>Destination Branch *</label>
                  <select
                    required
                    value={pickupRequest.destination_branch}
                    onChange={(e) => setPickupRequest({...pickupRequest, destination_branch: e.target.value})}
                    style={styles.select}
                  >
                    <option value="">Select Branch</option>
                    {branches.map(branch => (
                      <option key={branch.id} value={branch.id}>{branch.name} - {branch.city}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label>Preferred Pickup Date *</label>
                  <input
                    type="date"
                    required
                    value={pickupRequest.preferred_pickup_date}
                    onChange={(e) => setPickupRequest({...pickupRequest, preferred_pickup_date: e.target.value})}
                    style={styles.input}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={pickupRequest.is_priority}
                      onChange={(e) => setPickupRequest({...pickupRequest, is_priority: e.target.checked})}
                    />
                    Priority Pickup (+₦100)
                  </label>
                </div>
              </div>
              
              <div style={styles.formActions}>
                <button type="button" style={styles.cancelButton} onClick={() => setShowPickupForm(false)}>Cancel</button>
                <button type="submit" style={styles.submitButton}>Submit Request</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: { padding: '20px', maxWidth: '1000px', margin: '0 auto' },
  loading: { textAlign: 'center', padding: '40px', fontSize: '18px' },
  tabs: { display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '2px solid #eee', paddingBottom: '10px' },
  tab: { padding: '10px 20px', backgroundColor: 'transparent', border: 'none', cursor: 'pointer', fontSize: '14px', color: '#666', borderRadius: '4px' },
  activeTab: { padding: '10px 20px', backgroundColor: '#3498db', color: 'white', border: 'none', cursor: 'pointer', fontSize: '14px', borderRadius: '4px' },
  content: { display: 'flex', flexDirection: 'column', gap: '20px' },
  card: { backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
  primaryButton: { padding: '10px 20px', backgroundColor: '#2ecc71', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  parcelList: { display: 'flex', flexDirection: 'column', gap: '15px' },
  parcelCard: { border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#f8f9fa' },
  parcelHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' },
  parcelDetails: { marginBottom: '10px' },
  smallButton: { padding: '5px 10px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
  searchSection: { backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' },
  searchForm: { display: 'flex', gap: '10px', marginTop: '15px' },
  input: { flex: 1, padding: '10px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '14px' },
  button: { padding: '10px 20px', backgroundColor: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  trackingResult: { backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' },
  detailGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' },
  timeline: { marginTop: '30px', paddingTop: '20px', borderTop: '1px solid #eee' },
  timelineItem: { display: 'flex', gap: '15px', paddingBottom: '20px', position: 'relative' },
  timelineDot: { width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#3498db', marginTop: '5px' },
  timelineContent: { flex: 1 },
  timelineStatus: { fontWeight: 'bold', margin: '0 0 5px 0' },
  timelineNotes: { color: '#666', margin: '0 0 5px 0' },
  timestamp: { fontSize: '12px', color: '#999', margin: 0 },
  pickupList: { display: 'flex', flexDirection: 'column', gap: '15px' },
  pickupCard: { border: '1px solid #ddd', borderRadius: '8px', padding: '15px', backgroundColor: '#f8f9fa' },
  pickupHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' },
  pickupDetails: { marginBottom: '10px' },
  emptyMessage: { textAlign: 'center', padding: '40px', color: '#666' },
  modal: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
  modalContent: { backgroundColor: 'white', borderRadius: '8px', padding: '20px', width: '90%', maxWidth: '500px', maxHeight: '90vh', overflow: 'auto' },
  modalHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
  closeButton: { backgroundColor: 'transparent', border: 'none', fontSize: '24px', cursor: 'pointer' },
  form: { display: 'flex', flexDirection: 'column', gap: '15px' },
  formRow: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' },
  formGroup: { display: 'flex', flexDirection: 'column', gap: '5px' },
  textarea: { padding: '10px', borderRadius: '4px', border: '1px solid #ddd', fontSize: '14px', minHeight: '80px' },
  select: { padding: '10px', borderRadius: '4px', border: '1px solid #ddd', fontSize: '14px' },
  checkboxLabel: { display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', marginTop: '25px' },
  formActions: { display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' },
  cancelButton: { padding: '10px 20px', backgroundColor: '#95a5a6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  submitButton: { padding: '10px 20px', backgroundColor: '#2ecc71', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
};

export default CustomerPortal;

