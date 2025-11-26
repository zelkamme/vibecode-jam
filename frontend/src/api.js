import axios from 'axios';

// Базовый URL: берём из env, иначе по умолчанию '/api'
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const fetchCandidates = async () => {
  const response = await axios.get(`${API_BASE_URL}/candidates`);
  return response.data;
};
