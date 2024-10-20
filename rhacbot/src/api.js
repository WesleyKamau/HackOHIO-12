// src/api.js
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export const addChat = (data) => axios.post(`${API_URL}/chats/add`, data);

export const sendMessage = (data) =>
  axios.post(`${API_URL}/messages/send`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const getBuildings = () => axios.get(`${API_URL}/buildings`);
