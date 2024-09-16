// src/axiosConfig.js

import axios from 'axios';

const API_URL = 'https://your-backend-app.up.railway.app'; // Replace with your actual backend URL


const axiosInstance = axios.create({
  baseURL: API_URL,
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;
