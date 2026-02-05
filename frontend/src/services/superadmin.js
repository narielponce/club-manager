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

export async function getClubs(includeInactive = false) {
  let apiPath = '/superadmin/clubs/';
  if (includeInactive) {
    apiPath += '?include_inactive=true';
  }
  return apiFetch(apiPath);
}

export async function updateClub(clubId, clubData) {
  return apiFetch(`/superadmin/clubs/${clubId}`, {
    method: 'PUT',
    body: JSON.stringify(clubData),
  });
}

export async function deactivateClub(clubId) {
  return apiFetch(`/superadmin/clubs/${clubId}`, {
    method: 'DELETE',
  });
}

export async function permanentlyDeleteClub(clubId) {
  return apiFetch(`/superadmin/clubs/${clubId}/permanent`, {
    method: 'DELETE',
  });
}

export async function uploadClubLogo(clubId, logoFile) {
  const formData = new FormData();
  formData.append('logo', logoFile);

  return apiFetch(`/superadmin/clubs/${clubId}/logo`, {
    method: 'POST',
    body: formData,
  });
}

export async function getClubAdmins(clubId) {
  return apiFetch(`/superadmin/clubs/${clubId}/admins`);
}
