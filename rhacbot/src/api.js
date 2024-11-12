// src/api.js
import axios from 'axios';

const base_URL = "http://127.0.0.1:5000"

const API_URL = base_URL + '/api';

export const addChat = (data) => axios.post(`${API_URL}/chats/add`, data);

export const sendMessage = (data) =>
  axios.post(`${API_URL}/messages/send`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const getBuildings = () => axios.get(`${API_URL}/buildings`);
