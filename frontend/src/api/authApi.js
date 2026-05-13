import { apiRequest } from './client';

export async function loginUser(credentials) {
  const data = await apiRequest('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });

  localStorage.setItem('accessToken', data.access);
  localStorage.setItem('refreshToken', data.refresh);

  return data;
}

export async function registerUser(userData) {
  const data = await apiRequest('/auth/register/', {
    method: 'POST',
    body: JSON.stringify(userData),
  });

  localStorage.setItem('accessToken', data.access);
  localStorage.setItem('refreshToken', data.refresh);

  return data;
}

export function getCurrentUser() {
  return apiRequest('/me');
}

export function updateCurrentUser(profileData) {
  return apiRequest('/me', {
    method: 'PATCH',
    body: JSON.stringify(profileData),
  });
}

export function logoutUser() {
  const refreshToken = localStorage.getItem('refreshToken');

  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');

  if (!refreshToken) {
    return Promise.resolve();
  }

  return apiRequest('/auth/logout/', {
    method: 'POST',
    body: JSON.stringify({ refresh: refreshToken }),
  });
}
