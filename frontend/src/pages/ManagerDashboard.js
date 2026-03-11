/**
 * Manager Dashboard Component
 * Full implementation with branch metrics, staff/driver management, and audit logs
 */

import React, { useState, useEffect } from 'react';
import { parcelService, staffService, driverService, branchService, auditLogService } from '../services/api';

const ManagerDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [staff, setStaff] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [branches, setBranches] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, staffRes, driversRes, branchesRes, logsRes] = await Promise.all([
        parcelService.getDashboardStats(),
        staffService.list({ limit: 100 }),
        driverService.list({ limit: 100 }),
        branchService.list({ limit: 100 }),
        auditLogService.list({ limit: 50 }),
      ]);

      setStats(statsRes.data);
      setStaff(staffRes.data.results || []);
      setDrivers(driversRes.data.results || []);
      setBranches(branchesRes.data.results || []);
      setAuditLogs(logsRes.data.results || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
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
    return colors[status] || '#95a5a6';
  };

  if (loading) return <div style={styles.loading}>Loading...</div>;

  return (
    <div style={styles.container}>
      <h1>Manager Dashboard</h1>
      
      {/* Tab Navigation */}
      <div style={styles.tabs}>
        <button 
          style={activeTab === 'overview' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          style={activeTab === 'staff' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('staff')}
        >
          Staff
        </button>
        <button 
          style={activeTab === 'drivers' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('drivers')}
        >
          Drivers
        </button>
        <button 
          style={activeTab === 'branches' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('branches')}
        >
          Branches
        </button>
        <button 
          style={activeTab === 'audit' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('audit')}
        >
          Audit Logs
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && stats && (
        <div style={styles.content}>
          <div style={styles.statsGrid}>
            <StatCard title="Total Parcels" value={stats.total_parcels} color="#3498db" />
            <StatCard title="Today's Parcels" value={stats.today_parcels} color="#2ecc71" />
            <StatCard title="This Week" value={stats.week_parcels} color="#9b59b6" />
            <StatCard title="Total Revenue" value={`$${stats.total_revenue?.toFixed(2) || 0}`} color="#f39c12" />
            <StatCard title="Pending Pickups" value={stats.pending_pickups} color="#e74c3c" />
            <StatCard title="Delivery Rate" value={`${stats.delivery_rate}%`} color="#1abc9c" />
          </div>

          {/* Status Distribution */}
          <div style={styles.card}>
            <h3>Parcel Status Distribution</h3>
            <div style={styles.statusGrid}>
              {Object.entries(stats.parcels_by_status || {}).map(([status, count]) => (
                <div key={status} style={{ ...styles.statusItem, borderLeftColor: getStatusColor(status) }}>
                  <span style={styles.statusLabel}>{status.replace('_', ' ')}</span>
                  <span style={styles.statusValue}>{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div style={styles.card}>
            <h3>Quick Actions</h3>
            <div style={styles.actionsGrid}>
              <button style={styles.actionButton} onClick={() => window.location.href = '/staff/new'}>
                Add New Staff
              </button>
              <button style={styles.actionButton} onClick={() => window.location.href = '/drivers/new'}>
                Add New Driver
              </button>
              <button style={styles.actionButton} onClick={() => window.location.href = '/branches/new'}>
                Add New Branch
              </button>
              <button style={styles.actionButton} onClick={() => window.location.href = '/parcels'}>
                View All Parcels
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Staff Tab */}
      {activeTab === 'staff' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <h3>Staff Management</h3>
              <button style={styles.primaryButton}>Add New Staff</button>
            </div>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Employee ID</th>
                  <th>Position</th>
                  <th>Branch</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {staff.map((member) => (
                  <tr key={member.id}>
                    <td>{member.user_name || `${member.user?.first_name} ${member.user?.last_name}`}</td>
                    <td>{member.employee_id}</td>
                    <td>{member.position}</td>
                    <td>{member.branch_name}</td>
                    <td>
                      <span style={member.is_active ? styles.activeBadge : styles.inactiveBadge}>
                        {member.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <button style={styles.smallButton}>Edit</button>
                      <button style={{...styles.smallButton, backgroundColor: '#e74c3c'}}>
                        {member.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Drivers Tab */}
      {activeTab === 'drivers' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <h3>Driver Management</h3>
              <button style={styles.primaryButton}>Add New Driver</button>
            </div>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Driver ID</th>
                  <th>Vehicle</th>
                  <th>Branch</th>
                  <th>Rating</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {drivers.map((driver) => (
                  <tr key={driver.id}>
                    <td>{driver.user_name || `${driver.user?.first_name} ${driver.user?.last_name}`}</td>
                    <td>{driver.driver_id}</td>
                    <td>{driver.vehicle_number}</td>
                    <td>{driver.branch_name}</td>
                    <td>{driver.rating}</td>
                    <td>
                      <span style={driver.is_active ? styles.activeBadge : styles.inactiveBadge}>
                        {driver.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <button style={styles.smallButton}>Edit</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Branches Tab */}
      {activeTab === 'branches' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <h3>Branch Management</h3>
              <button style={styles.primaryButton}>Add New Branch</button>
            </div>
            <div style={styles.branchGrid}>
              {branches.map((branch) => (
                <div key={branch.id} style={styles.branchCard}>
                  <h4>{branch.name}</h4>
                  <p>{branch.city}</p>
                  <p>{branch.address}</p>
                  <p>Phone: {branch.contact_phone}</p>
                  <span style={branch.is_active ? styles.activeBadge : styles.inactiveBadge}>
                    {branch.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Audit Logs Tab */}
      {activeTab === 'audit' && (
        <div style={styles.content}>
          <div style={styles.card}>
            <h3>Recent Audit Logs</h3>
            <div style={styles.logList}>
              {auditLogs.map((log) => (
                <div key={log.id} style={styles.logItem}>
                  <div style={styles.logHeader}>
                    <span style={styles.logAction}>{log.action}</span>
                    <span style={styles.logModel}>{log.model_name}</span>
                    <span style={styles.logTime}>
                      {new Date(log.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div style={styles.logDescription}>{log.description}</div>
                  <div style={styles.logUser}>User: {log.user_name || log.user?.username}</div>
                </div>
              ))}
            </div>
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
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '20px',
  },
  statCard: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    borderLeft: '4px solid',
  },
  card: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  statusGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '15px',
    marginTop: '15px',
  },
  statusItem: {
    padding: '15px',
    borderRadius: '4px',
    borderLeft: '4px solid',
    backgroundColor: '#f8f9fa',
  },
  statusLabel: {
    display: 'block',
    fontSize: '12px',
    color: '#666',
    textTransform: 'uppercase',
  },
  statusValue: {
    display: 'block',
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#333',
  },
  actionsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '15px',
    marginTop: '15px',
  },
  actionButton: {
    padding: '15px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  primaryButton: {
    padding: '10px 20px',
    backgroundColor: '#2ecc71',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
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
  activeBadge: {
    display: 'inline-block',
    padding: '4px 8px',
    backgroundColor: '#2ecc71',
    color: 'white',
    borderRadius: '4px',
    fontSize: '12px',
  },
  inactiveBadge: {
    display: 'inline-block',
    padding: '4px 8px',
    backgroundColor: '#95a5a6',
    color: 'white',
    borderRadius: '4px',
    fontSize: '12px',
  },
  branchGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
  },
  branchCard: {
    padding: '15px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    backgroundColor: '#f8f9fa',
  },
  logList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  logItem: {
    padding: '15px',
    border: '1px solid #eee',
    borderRadius: '4px',
  },
  logHeader: {
    display: 'flex',
    gap: '15px',
    marginBottom: '5px',
  },
  logAction: {
    fontWeight: 'bold',
    color: '#3498db',
  },
  logModel: {
    color: '#666',
  },
  logTime: {
    color: '#999',
    fontSize: '12px',
  },
  logDescription: {
    color: '#333',
  },
  logUser: {
    fontSize: '12px',
    color: '#999',
    marginTop: '5px',
  },
};

export default ManagerDashboard;

