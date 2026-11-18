import { useState } from 'react';
import { LocateFixed, MapPin } from 'lucide-react';
import { api } from '../lib/api';
import { useI18n } from '../i18n';
import { useToast } from './Toast';
import { Spinner } from './ui';

/** Browser location, as a promise. */
export function currentPosition() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) return reject(new Error('unsupported'));
    navigator.geolocation.getCurrentPosition(
      (p) => resolve({ lat: p.coords.latitude, lng: p.coords.longitude }),
      (e) => reject(new Error(e.code === 1 ? 'denied' : 'unavailable')),
      { enableHighAccuracy: false, timeout: 15000, maximumAge: 600000 },
    );
  });
}

/** Great-circle distance in km. */
export function kmBetween(a, b) {
  if (!a || !b || a.lat == null || b.lat == null) return null;
  const rad = (x) => (x * Math.PI) / 180;
  const dLat = rad(b.lat - a.lat);
  const dLng = rad(b.lng - a.lng);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.sqrt(h));
}

/** Never more precise than half a kilometre. */
export const roundKm = (km) => (km == null ? null : Math.max(0.5, Math.round(km * 2) / 2));

/** Profile card: opt in to nearest-first alerts. */
export function NearbyCard({ user, onUser }) {
  const { t, ago } = useI18n();
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  const share = async () => {
    setBusy(true);
    try {
      const pos = await currentPosition();
      onUser(await api.setLocation(user.id, pos));
      toast(t('geo.saved'));
    } catch (e) {
      toast(t(e.message === 'denied' ? 'geo.denied' : 'geo.unsupported'), 'error');
    } finally {
      setBusy(false);
    }
  };
  const remove = async () => onUser(await api.clearLocation(user.id));
  return (
    <div className="card p-6">
      <h2 className="flex items-center gap-2 text-lg font-bold">
        <MapPin className="h-5 w-5 text-blood-500" aria-hidden /> {t('geo.title')}
      </h2>
      <p className="mt-2 text-sm text-slate-400">{t('geo.hint')}</p>
      {user.location ? (
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl bg-emerald-950/40 p-3 text-sm text-emerald-300">
          <span>
            ✓ {t('geo.saved')} · {ago(user.location.updated_at)}
          </span>
          <span className="flex gap-3">
            <button onClick={share} className="font-semibold hover:underline" disabled={busy}>
              {t('geo.update')}
            </button>
            <button onClick={remove} className="text-slate-400 hover:text-blood-500">
              {t('geo.remove')}
            </button>
          </span>
        </div>
      ) : (
        <button onClick={share} className="btn-primary mt-4" disabled={busy}>
          {busy ? <Spinner className="h-4 w-4" /> : <LocateFixed className="h-4 w-4" />} {t('geo.use')}
        </button>
      )}
    </div>
  );
}
