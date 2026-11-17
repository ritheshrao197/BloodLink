async function request(path, { method = 'GET', body, params } = {}) {
  const query = params
    ? '?' + new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v != null)).toString()
    : '';
  let res;
  try {
    res = await fetch(`/api${path}${query}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new Error('Cannot reach the BloodLink server. Is the backend running on port 8000?');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const d = data.detail;
    const msg = Array.isArray(d)
      ? d.map((e) => `${e.loc?.slice(-1)[0]}: ${String(e.msg).replace('Value error, ', '')}`).join('; ')
      : d;
    throw new Error(msg || `Request failed (${res.status})`);
  }
  return data;
}

const enc = encodeURIComponent;

export const api = {
  config: () => request('/config'),
  locations: () => request('/locations'),
  register: (body) => request('/register', { method: 'POST', body }),
  user: (id) => request(`/users/${id}`),
  userByCode: (code) => request(`/users/by-code/${enc(code)}`),
  activity: (id) => request(`/users/${id}/activity`),
  setAvailability: (id, isAvailable) =>
    request(`/users/${id}/availability`, { method: 'PATCH', body: { is_available: isAvailable } }),
  donors: (params) => request('/donors', { params }),
  leaderboard: (limit = 10) => request('/leaderboard', { params: { limit } }),
  requests: (status = 'Active') => request('/requests', { params: { status } }),
  sos: (body) => request('/sos', { method: 'POST', body }),
  donate: (requestId, userId) =>
    request(`/donate/${requestId}`, { method: 'POST', body: { user_id: userId, confirmed: true } }),
  rewards: () => request('/rewards'),
  redeem: (rewardId, userId) => request(`/redeem/${rewardId}`, { method: 'POST', body: { user_id: userId } }),
  admin: {
    stats: () => request('/admin/stats'),
    users: () => request('/admin/users'),
    vouchers: () => request('/admin/vouchers'),
    verifyUser: (id, verified) => request(`/admin/users/${id}/verify`, { method: 'POST', params: { verified } }),
    verifyRequest: (id, verified) =>
      request(`/admin/requests/${id}/verify`, { method: 'POST', params: { verified } }),
    setStatus: (id, status) => request(`/admin/requests/${id}/status`, { method: 'POST', params: { status } }),
  },
};
