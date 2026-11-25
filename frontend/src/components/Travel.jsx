import { useState } from 'react';
import { Car, LifeBuoy, Map } from 'lucide-react';
import { api } from '../lib/api';
import { useI18n } from '../i18n';
import { ErrorBox, Spinner } from './ui';

const destination = (r) => [r.hospital, r.city, r.state].filter(Boolean).join(', ');

/** Google Maps directions; the hospital is found by name (our own point for a request is only approximate). */
export const directionsUrl = (r) =>
  `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(destination(r))}&travelmode=driving`;

const uberUrl = (r) =>
  'https://m.uber.com/ul/?action=setPickup&pickup=my_location' +
  `&dropoff[formatted_address]=${encodeURIComponent(destination(r))}&dropoff[nickname]=${encodeURIComponent(r.hospital || '')}`;

// Ola's link only takes coordinates, so it uses the request's approximate point
const olaUrl = (r) => (r.lat != null && r.lng != null ? `https://book.olacabs.com/?drop_lat=${r.lat}&drop_lng=${r.lng}` : null);

/** After pledging: directions, cab apps, calling the requester, and "I need help getting there". */
export default function GettingThere({ request, donationId }) {
  const { t } = useI18n();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [help, setHelp] = useState(null); // response of the ride-help request
  const ola = olaUrl(request);
  const phone = request.contact_phone;

  const askHelp = async () => {
    setBusy(true);
    setError(null);
    try {
      setHelp(await api.rideHelp(donationId));
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="space-y-3 rounded-xl border border-slate-800 p-4" aria-labelledby="travel-title">
      <h3 id="travel-title" className="font-bold">
        {t('travel.title')}
      </h3>
      <p className="text-sm text-slate-300">{t('donate.headTo', { place: destination(request) })}</p>
      <a href={directionsUrl(request)} target="_blank" rel="noreferrer" className="btn-primary w-full">
        <Map className="h-4 w-4" /> {t('travel.directions')}
      </a>
      <div className={ola ? 'grid grid-cols-2 gap-2' : 'grid gap-2'}>
        <a href={uberUrl(request)} target="_blank" rel="noreferrer" className="btn-ghost">
          <Car className="h-4 w-4" /> Uber
        </a>
        {ola && (
          <a href={ola} target="_blank" rel="noreferrer" className="btn-ghost">
            <Car className="h-4 w-4" /> Ola
          </a>
        )}
      </div>
      <p className="text-xs text-slate-500">{t('travel.cabNote')}</p>
      {phone && (
        <div className="grid grid-cols-2 gap-2">
          <a href={`tel:${phone.replace(/[^\d+]/g, '')}`} className="btn-ghost">
            📞 {phone}
          </a>
          <a href={`https://wa.me/${phone.replace(/\D/g, '')}`} target="_blank" rel="noreferrer" className="btn-ghost text-emerald-500">
            💬 WhatsApp
          </a>
        </div>
      )}
      {help ? (
        <p className="rounded-lg bg-sky-950/40 px-3 py-2 text-sm text-sky-200" role="status">
          {help.status === 'already_requested'
            ? t('travel.helpAlready')
            : help.phone
              ? t('travel.helpSent', { phone: help.phone })
              : t('travel.helpSentNoPhone')}
        </p>
      ) : (
        donationId && (
          <button onClick={askHelp} disabled={busy} className="btn-ghost w-full border-amber-500/50 text-amber-300">
            {busy ? <Spinner /> : <LifeBuoy className="h-4 w-4" />} {t('travel.help')}
          </button>
        )
      )}
      <ErrorBox error={error} />
    </section>
  );
}
