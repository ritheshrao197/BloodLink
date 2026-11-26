// Browser push notifications: register the service worker, subscribe this browser, tell the backend.
import { api } from './api';

export const pushSupported = () =>
  typeof window !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;

export const permission = () => (pushSupported() ? Notification.permission : 'unsupported');

let keyPromise;
/** { enabled, public_key } from the server (cached). Push is off until the server has VAPID keys. */
export const pushConfig = () => (keyPromise ??= api.push.key().catch(() => ({ enabled: false })));

const registration = () => navigator.serviceWorker.register('/sw.js');

function keyBytes(base64url) {
  const b64 = (base64url + '='.repeat((4 - (base64url.length % 4)) % 4)).replace(/-/g, '+').replace(/_/g, '/');
  return Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
}

/** This browser's current subscription, if any. */
export async function currentSubscription() {
  if (!pushSupported()) return null;
  const reg = await navigator.serviceWorker.getRegistration('/');
  return reg ? reg.pushManager.getSubscription() : null;
}

/**
 * Ask permission (if needed), subscribe and register with the backend.
 * Signed in: alerts for this account. With { requestId, requestToken }: updates for that SOS only.
 * Returns 'on' | 'denied' | 'unavailable'.
 */
export async function enablePush({ requestId, requestToken } = {}) {
  const cfg = await pushConfig();
  if (!pushSupported() || !cfg.enabled) return 'unavailable';
  if ((await Notification.requestPermission()) !== 'granted') return 'denied';
  const reg = await registration();
  await navigator.serviceWorker.ready;
  const sub =
    (await reg.pushManager.getSubscription()) ||
    (await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: keyBytes(cfg.public_key) }));
  await api.push.subscribe({ subscription: sub.toJSON(), request_id: requestId ?? null, request_token: requestToken ?? null });
  return 'on';
}

/** Stop all notifications to this browser (account alerts and any SOS it follows). */
export async function disablePush() {
  const sub = await currentSubscription();
  if (!sub) return;
  await api.push.unsubscribe(sub.endpoint).catch(() => {});
  await sub.unsubscribe().catch(() => {});
}
