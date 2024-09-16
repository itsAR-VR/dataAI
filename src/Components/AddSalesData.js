// src/components/AddSalesData.js

import React, { useState } from 'react';
import axios from '../axiosConfig';

function AddSalesData() {
  const [formData, setFormData] = useState({
    date: '',
    product_name: '',
    quantity: '',
    price: '',
    additional_info: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const dataToSend = {
        ...formData,
        quantity: parseInt(formData.quantity),
        price: parseFloat(formData.price),
        additional_info: formData.additional_info ? JSON.parse(formData.additional_info) : {}
      };
      await axios.post('/add_sales_data', dataToSend);
      setSuccess('Sales data added successfully!');
      // Reset form
      setFormData({
        date: '',
        product_name: '',
        quantity: '',
        price: '',
        additional_info: ''
      });
    } catch (error) {
      setError('Failed to add sales data. Please check your input.');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div>
      <h2>Add Sales Data</h2>
      {error && <p style={{color:'red'}}>{error}</p>}
      {success && <p style={{color:'green'}}>{success}</p>}
      <form onSubmit={handleSubmit}>
        <input type="date" name="date" value={formData.date} onChange={handleChange} required />
        <input type="text" name="product_name" value={formData.product_name} onChange={handleChange} placeholder="Product Name" required />
        <input type="number" name="quantity" value={formData.quantity} onChange={handleChange} placeholder="Quantity" required />
        <input type="number" step="0.01" name="price" value={formData.price} onChange={handleChange} placeholder="Price" required />
        <textarea name="additional_info" value={formData.additional_info} onChange={handleChange} placeholder="Additional Info (JSON format)"></textarea>
        <button type="submit">Add Sales Data</button>
      </form>
    </div>
  );
}

export default AddSalesData;
