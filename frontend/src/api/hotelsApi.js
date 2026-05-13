import { apiRequest } from './client';

export function getHotels(search = '') {
  const query = search ? `?search=${encodeURIComponent(search)}` : '';
  return apiRequest(`/hotels/${query}`);
}

export function getHotelById(id) {
  return apiRequest(`/hotels/${id}/`);
}

export function getHotelRooms(hotelId, filters = {}) {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value);
    }
  });

  const query = params.toString() ? `?${params.toString()}` : '';
  return apiRequest(`/hotels/${hotelId}/rooms/${query}`);
}

export function getRoomById(hotelId, roomId) {
  return apiRequest(`/hotels/${hotelId}/rooms/${roomId}/`);
}
