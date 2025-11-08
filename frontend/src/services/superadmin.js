import { apiFetch } from './api.js';

export async function createClub(formData) {
  // The apiFetch helper automatically adds the token and handles FormData correctly.
  // We just need to call it with the correct endpoint and options.
  try {
    const response = await apiFetch('/users/', {
      method: 'POST',
      body: formData, // Pass FormData directly
    });
    return response;
  } catch (error) {
    // The apiFetch helper already formats the error message, so we can just re-throw it.
    throw error;
  }
}
