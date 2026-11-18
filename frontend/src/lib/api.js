const TOKEN_KEY = 'bloodlink_token';
let token = (() => {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
})();

/** Session token for this browser (sent as a Bearer token). */
export function setToken(value) {
  token = value || null;
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage blocked: the session lasts for this tab */
  }
}
export const hasToken = () => !!token;

async function request(path, { method = 'GET', body, params } = {}) {
  const query = params
    ? '?' + new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v != null)).toString()
    : '';
  let res;
  const headers = {};
  if (body) headers['Content-Type'] = 'application/json';
  if (token) headers.Authorization = `Bearer ${token}`;
  try {
    res = await fetch(`/api${path}${query}`, {
      method,
      headers,
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
      : typeof d === 'object' && d
        ? d.message
        : d;
    const err = new Error(msg || `Request failed (${res.status})`);
    err.status = res.status;
    err.data = typeof d === 'object' && !Array.isArray(d) ? d : null; // e.g. { eligibility } on a 409
    throw err;
  }
  return data;
}

const enc = encodeURIComponent;

export const api = {
  config: () => request('/config'),
  locations: () => request('/locations'),
  register: (body) => request('/register', { method: 'POST', body }),
  user: (id) => request(`/users/${id}`),
  stats: () => request('/stats'),
  recentActivity: () => request('/activity/recent'),
  setLocation: (id, pos) => request(`/users/${id}/location`, { method: 'PATCH', body: pos }),
  clearLocation: (id) => request(`/users/${id}/location`, { method: 'DELETE' }),
  auth: {
    me: () => request('/auth/me'),
    telegramStart: (purpose = 'login') => request('/auth/telegram/start', { method: 'POST', body: { purpose } }),
    telegramPoll: (nonce) => request(`/auth/telegram/poll/${enc(nonce)}`),
    demo: (code) => request('/auth/demo', { method: 'POST', body: { code } }),
    admin: (password) => request('/auth/admin', { method: 'POST', body: { password } }),
    logout: () => request('/auth/logout', { method: 'POST' }),
  },
  activity: (id) => request(`/users/${id}/activity`),
  setLanguage: (id, language) => request(`/users/${id}/language`, { method: 'PATCH', body: { language } }),
  setAvailability: (id, isAvailable) =>
    request(`/users/${id}/availability`, { method: 'PATCH', body: { is_available: isAvailable } }),
  donors: (params) => request('/donors', { params }),
  leaderboard: (limit = 10) => request('/leaderboard', { params: { limit } }),
  requests: (status = 'Active') => request('/requests', { params: { status } }),
  sos: (body) => request('/sos', { method: 'POST', body }),
  donate: (requestId, userId, screening) =>
    request(`/donate/${requestId}`, { method: 'POST', body: { user_id: userId, confirmed: true, screening } }),
  rewards: () => request('/rewards'),
  eligibilityQuestions: (sex) => request('/eligibility/questions', { params: { sex } }),
  checkEligibility: (userId, screening) => request('/eligibility/check', { method: 'POST', body: { user_id: userId, screening } }),
  setHealth: (id, body) => request(`/users/${id}/health`, { method: 'PATCH', body }),
  clearDeferral: (id) => request(`/users/${id}/deferral`, { method: 'DELETE' }),
  achievements: () => request('/achievements'),
  userAchievements: (id) => request(`/users/${id}/achievements`),
  achievementsSeen: (id) => request(`/users/${id}/achievements/seen`, { method: 'POST' }),
  redeem: (rewardId, userId) => request(`/redeem/${rewardId}`, { method: 'POST', body: { user_id: userId } }),
  teams: {
    list: (kind, userId) => request('/teams', { params: { kind, user_id: userId } }),
    get: (id, userId) => request(`/teams/${id}`, { params: { user_id: userId } }),
    create: (body) => request('/teams', { method: 'POST', body }),
    join: (userId, code) => request('/teams/join', { method: 'POST', body: { user_id: userId, invite_code: code } }),
    leave: (id, userId) => request(`/teams/${id}/leave`, { method: 'POST', body: { user_id: userId } }),
    mine: (userId) => request(`/users/${userId}/teams`),
  },
  camps: {
    list: (when, userId) => request('/camps', { params: { when, user_id: userId } }),
    leaderboard: () => request('/camps/leaderboard'),
    create: (body) => request('/camps', { method: 'POST', body }),
    rsvp: (id, userId) => request(`/camps/${id}/rsvp`, { method: 'POST', body: { user_id: userId } }),
    attendees: (id, userId) => request(`/camps/${id}/attendees`, { params: { user_id: userId } }),
    attend: (id, userId, attendeeId) => request(`/camps/${id}/attend`, { method: 'POST', body: { user_id: userId, attendee_id: attendeeId } }),
  },
  admin: {
    stats: () => request('/admin/stats'),
    users: () => request('/admin/users'),
    vouchers: () => request('/admin/vouchers'),
    favorite: (id) => request(`/admin/users/${id}/favorite`, { method: 'POST' }),
    verifyUser: (id, verified) => request(`/admin/users/${id}/verify`, { method: 'POST', params: { verified } }),
    verifyRequest: (id, verified) =>
      request(`/admin/requests/${id}/verify`, { method: 'POST', params: { verified } }),
    setStatus: (id, status) => request(`/admin/requests/${id}/status`, { method: 'POST', params: { status } }),
  },
};
