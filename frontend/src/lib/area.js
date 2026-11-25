import { useState } from 'react';
import { api } from './api';
import { useSession } from './session';

const KEY = 'bloodlink-area'; // a visitor's chosen district: { state, district, lat, lng }

function readPicked() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || null;
  } catch {
    return null;
  }
}

/**
 * Where "nearby" is measured from.
 *  - a one-off "use my current position" (kept in memory only, never saved or tracked)
 *  - signed in: the account's home point (shared location, else the district centre)
 *  - visitor: the district they picked (remembered in this browser)
 * area = { lat, lng, label, source, state, district } or null.
 */
export function useArea() {
  const { user } = useSession();
  const [picked, setPicked] = useState(readPicked);
  const [here, setHere] = useState(null);

  const choose = async ({ state, city }) => {
    const p = await api.geoPoint(city, state);
    const next = { state, district: city, lat: p.lat, lng: p.lng };
    try {
      localStorage.setItem(KEY, JSON.stringify(next));
    } catch {
      /* storage blocked: applies for this visit */
    }
    setPicked(next);
    setHere(null);
  };

  const base = user?.home_point
    ? { ...user.home_point, label: user.city, state: user.state, district: user.city }
    : picked
      ? { lat: picked.lat, lng: picked.lng, label: picked.district, source: 'picked', state: picked.state, district: picked.district }
      : null;
  const area = here ? { ...here, label: null, source: 'here', state: base?.state, district: base?.district } : base;
  return { area, choose, setHere, signedIn: !!user };
}

/** Query params for the nearby feed. */
export const feedParams = (area, scope) =>
  area ? { lat: area.lat, lng: area.lng, scope, state: area.state || '', district: area.district || '' } : {};
