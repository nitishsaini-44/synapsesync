/**
 * components/AuthContext.jsx
 * ───────────────────────────
 * React context for user authentication state.
 *
 * Fixes:
 * - Token expiry is checked on page load using the JWT `exp` claim.
 *   An expired token is cleared immediately instead of waiting for the
 *   first API call to fail (which would leave the UI in a broken state).
 * - Uses setAuthHeader() from client.js instead of mutating axios defaults directly.
 */
import React, { createContext, useState, useEffect, useContext } from 'react';
import { setAuthHeader } from '../api/client';

const AuthContext = createContext(null);

/** Decodes a JWT and checks if it has expired. Returns true if valid, false if expired. */
function isTokenValid(token) {
  try {
    // JWT payload is the second base64url-encoded segment
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (!payload.exp) return true;                          // no expiry claim → treat as valid
    return payload.exp * 1000 > Date.now();                 // exp is in seconds
  } catch {
    return false;                                           // malformed token
  }
}

export const AuthProvider = ({ children }) => {
  const [user,    setUser]    = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token      = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      if (isTokenValid(token)) {
        // Token is still valid — restore session
        setUser(JSON.parse(storedUser));
        setAuthHeader(token);           // uses the exported helper (no direct axios mutation)
      } else {
        // Token has expired — clear storage silently before the user makes an API call
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setAuthHeader(null);
      }
    }

    setLoading(false);
  }, []);

  const login = (userData, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setAuthHeader(token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setAuthHeader(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
