import type { HbTrackApiClient } from '../client';

export async function loginRequest(
  client: HbTrackApiClient,
  body: { email: string; password: string },
) {
  const { data, error } = await client.POST('/auth/login', { body });
  if (error) throw error;
  return data!;
}

export async function logoutRequest(client: HbTrackApiClient) {
  const { error } = await client.POST('/auth/logout', {});
  if (error) throw error;
}

export async function getCurrentSessionRequest(client: HbTrackApiClient) {
  const { data, error } = await client.GET('/auth/me');
  if (error) throw error;
  return data!;
}
