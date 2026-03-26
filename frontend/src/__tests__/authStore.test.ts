import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useAuthStore } from '../stores/authStore';

const FAKE_USER = {
  id: 'u1', username: 'alice', email: 'alice@example.com',
  organization_id: 'org1', roles: ['COACH'],
};

describe('authStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.setState({ user: null, token: null, isAuthenticated: false });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('starts unauthenticated', () => {
    const { isAuthenticated, token, user } = useAuthStore.getState();
    expect(isAuthenticated).toBe(false);
    expect(token).toBeNull();
    expect(user).toBeNull();
  });

  it('setAuth sets credentials and persists to localStorage', () => {
    useAuthStore.getState().setAuth(FAKE_USER, 'access-token-123');

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.token).toBe('access-token-123');
    expect(state.user?.username).toBe('alice');

    expect(localStorage.getItem('access_token')).toBe('access-token-123');
    expect(localStorage.getItem('user')).toBe(JSON.stringify(FAKE_USER));
  });

  it('logout clears state and localStorage', () => {
    useAuthStore.getState().setAuth(FAKE_USER, 'tok');
    useAuthStore.getState().logout();

    const { isAuthenticated, token, user } = useAuthStore.getState();
    expect(isAuthenticated).toBe(false);
    expect(token).toBeNull();
    expect(user).toBeNull();
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('loadFromLocalStorage restores token and user', () => {
    localStorage.setItem('access_token', 'restored-tok');
    localStorage.setItem('user', JSON.stringify(FAKE_USER));
    useAuthStore.getState().loadFromLocalStorage();

    const state = useAuthStore.getState();
    expect(state.token).toBe('restored-tok');
    expect(state.isAuthenticated).toBe(true);
    expect(state.user?.username).toBe('alice');
  });

  it('loadFromLocalStorage does nothing when no token', () => {
    useAuthStore.getState().loadFromLocalStorage();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });
});
