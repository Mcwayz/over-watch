/**
 * Navigation Component
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Navigation = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getRoleLinks = () => {
    if (!user) return [];

    const links = [
      { label: 'Dashboard', href: '/dashboard' },
    ];

    switch (user.role) {
      case 'manager':
        return [
          ...links,
          { label: 'Staff', href: '/staff' },
          { label: 'Drivers', href: '/drivers' },
          { label: 'Reports', href: '/reports' },
        ];
      case 'staff':
        return [
          ...links,
          { label: 'Parcels', href: '/parcels' },
          { label: 'Images', href: '/images' },
        ];
      case 'driver':
        return [
          ...links,
          { label: 'Deliveries', href: '/deliveries' },
        ];
      case 'customer':
        return [
          ...links,
          { label: 'Track Parcel', href: '/track' },
          { label: 'My Parcels', href: '/my-parcels' },
        ];
      default:
        return links;
    }
  };

  return (
    <nav style={styles.navbar}>
      <div style={styles.container}>
        <Link to="/" style={styles.logo}>
          Courier Management System
        </Link>
        
        <div style={styles.navLinks}>
          {isAuthenticated ? (
            <>
              {getRoleLinks().map((link) => (
                <Link key={link.href} to={link.href} style={styles.link}>
                  {link.label}
                </Link>
              ))}
              
              <div style={styles.userMenu}>
                <span style={styles.username}>{user?.username}</span>
                <button
                  onClick={handleLogout}
                  style={styles.logoutButton}
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" style={styles.link}>
                Login
              </Link>
              <Link to="/register" style={styles.link}>
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

const styles = {
  navbar: {
    backgroundColor: '#2c3e50',
    color: 'white',
    padding: '15px 0',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  container: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 20px',
  },
  logo: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: 'white',
    textDecoration: 'none',
  },
  navLinks: {
    display: 'flex',
    gap: '20px',
    alignItems: 'center',
  },
  link: {
    color: 'white',
    textDecoration: 'none',
    fontSize: '14px',
    padding: '8px 12px',
    borderRadius: '4px',
    transition: 'background-color 0.3s',
  },
  userMenu: {
    display: 'flex',
    gap: '15px',
    alignItems: 'center',
    marginLeft: '20px',
    paddingLeft: '20px',
    borderLeft: '1px solid rgba(255, 255, 255, 0.3)',
  },
  username: {
    fontSize: '14px',
  },
  logoutButton: {
    padding: '8px 15px',
    backgroundColor: '#e74c3c',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
};

export default Navigation;
