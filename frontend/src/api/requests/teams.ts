import type { HbTrackApiClient } from '../client';

export async function listTeamsRequest(
  client: HbTrackApiClient,
  params?: { organizationId?: string },
) {
  const { data, error } = await client.GET('/teams', {
    params: { query: params as Record<string, string | undefined> },
  });
  if (error) throw error;
  return data!;
}
