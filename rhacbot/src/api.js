// src/api.js
import axios from 'axios';

// Determine application environment. Prefer REACT_APP_ENV if provided so dev/prod
// behavior can be controlled independently of build-time NODE_ENV.
// Build-time env (from REACT_APP_ENV or NODE_ENV) but allow a runtime override
export const BUILD_ENV = process.env.REACT_APP_ENV || process.env.NODE_ENV || 'development';

// At runtime allow override via localStorage RHAC_ENV only (no global/window fallback)
const runtimeOverride = (typeof window !== 'undefined') ? localStorage.getItem('RHAC_ENV') : null;
export const ENV = runtimeOverride || BUILD_ENV;

// Determine API base URL and optional prefix.
// Priority:
// 1. REACT_APP_API_URL (explicit full base)
// 2. developer defaults: dev -> http://127.0.0.1:5000 with prefix '/api'
//                      prod -> https://example.com with NO prefix (so endpoints like https://example.com/auth)
const explicitBase = process.env.REACT_APP_API_URL;
const defaultBase = ENV === 'development' ? 'http://127.0.0.1:5000' : 'https://example.com';
const base = explicitBase || defaultBase;

// Prefix is for mounting the API under a path (e.g. '/api').
// REACT_APP_API_PREFIX overrides the default. Defaults to '/api' in dev, '' in prod.
const explicitPrefix = process.env.REACT_APP_API_PREFIX;
const defaultPrefix = ENV === 'development' ? '/api' : '';
const prefix = typeof explicitPrefix !== 'undefined' ? explicitPrefix : defaultPrefix;

const API_URL = base + prefix;

export const addChat = (data) => axios.post(`${API_URL}/chats/add`, data);

export const sendMessage = (data) =>
  axios.post(`${API_URL}/messages/send`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const getBuildings = () => axios.get(`${API_URL}/buildings`);

// Authenticate against server-side admin password
export const authenticate = (password) => axios.post(`${API_URL}/auth`, { password });
