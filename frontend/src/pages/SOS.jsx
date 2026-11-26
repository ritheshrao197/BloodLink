import { useState } from 'react';
import { CheckCircle2, Send, Siren } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { BLOOD_GROUPS, COMPATIBILITY, cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { BadgeChip, BloodTag, ErrorBox, PageHeader, Spinner } from '../components/ui';
import LocationPicker from '../components/LocationPicker';
import { currentPosition } from '../components/Nearby';
import { LocateFixed } from 'lucide-react';
import PushToggle from '../components/PushToggle';

const URGENCIES = [
  ['Critical', 'border-red-500 bg-red-600/15 text-red-300'],
  ['High', 'border-amber-500 bg-amber-500/15 text-amber-300'],
  ['Normal', 'border-slate-500 bg-slate-800 text-slate-200'],
];

export default function SOS() {
  const { user, config } = useSession();
  const { t, lang } = useI18n();
  const [form, setForm] = useState({
    requester_name: user?.role === 'hospital' ? user.name : '',
    blood_group: 'O+',
    hospital: '',
    state: user?.state || null,
    city: user?.state ? user.city : '',
    units_needed: 1,
    urgency: 'Critical',
    contact_phone: '',
    lat: null,
    lng: null,
  });
  const [locating, setLocating] = useState(false);
  const useMyLocation = async () => {
    setLocating(true);
    try {
      const pos = await currentPosition();
      setForm((f) => ({ ...f, ...pos }));
    } catch (e) {
      setError(new Error(t(e.message === 'denied' ? 'geo.denied' : 'geo.unsupported')));
    } finally {
      setLocating(false);
    }
  };
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      // requester_language: Telegram updates about this request go out in the language it was made in
      setResult(await api.sos({ ...form, units_needed: Number(form.units_needed), requester_language: lang }));
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  if (result) {
    const r = result.request;
    return (
      <div className="mx-auto max-w-2xl">
        <div className="card border-red-500/40 p-8 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-600/20">
            <Siren className="h-8 w-8 text-red-500" />
          </div>
          <h1 className="mt-4 text-3xl font-extrabold">{t('sos.sent')}</h1>
          <p className="mt-2 text-slate-300">
            {t('sos.summary', { id: r.id, units: r.units_needed, group: r.blood_group, hospital: r.hospital, city: r.city })}
          </p>
          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-800/60 p-4">
              <div className="text-3xl font-extrabold text-red-400">{result.matched_donors}</div>
              <div className="text-sm text-slate-400">{t('sos.matched')}</div>
            </div>
            <div className="rounded-xl bg-slate-800/60 p-4">
              <div className="text-3xl font-extrabold text-sky-400">{result.reachable ?? result.telegram_reachable}</div>
              <div className="text-sm text-slate-400">{t('sos.alerted')}</div>
            </div>
          </div>
          <p className="mt-4 rounded-lg bg-sky-950/40 p-3 text-sm text-sky-300">
            {result.first_wave_km
              ? t('geo.firstWave', { n: result.first_wave, km: result.first_wave_km, min: result.escalate_minutes })
              : t('geo.firstWaveDistrict', { n: result.first_wave, min: result.escalate_minutes })}
          </p>
          {!config?.telegram_enabled && <p className="mt-3 text-xs text-amber-300/80">{t('sos.noBot')}</p>}
          {result.request_token && (
            <div className="mt-4">
              <PushToggle compact requestId={r.id} requestToken={result.request_token} />
            </div>
          )}
        </div>

        {result.donors.length > 0 && (
          <div className="card mt-6 p-5">
            <h2 className="mb-3 font-bold">{t('sos.matchedDonors')}</h2>
            <ul className="divide-y divide-slate-800">
              {result.donors.map((d) => (
                <li key={d.id} className="flex items-center justify-between gap-3 py-2.5">
                  <div className="flex min-w-0 items-center gap-3">
                    <BloodTag group={d.blood_group} size="sm" />
                    <span className="truncate font-medium">{d.name}</span>
                    <span className="hidden text-sm text-slate-500 sm:inline">{d.distance_km != null ? t('geo.away', { km: d.distance_km }) : d.city}</span>
                  </div>
                  <div className="flex shrink-0 items-center gap-3 text-sm">
                    {d.telegram_linked && <Send className="h-4 w-4 text-sky-400" aria-label={t('sos.telegramSent')} />}
                    <BadgeChip badge={d.badge} />
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <Link to="/" className="btn-primary">
            {t('sos.track')}
          </Link>
          <button className="btn-ghost" onClick={() => setResult(null)}>
            {t('sos.another')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader icon={Siren} title={t('sos.title')} subtitle={t('sos.subtitle')} />
      <form onSubmit={submit} className="card space-y-6 p-6 sm:p-8">
        <div>
          <span className="label">{t('sos.group')}</span>
          <div className="grid grid-cols-4 gap-2 sm:grid-cols-8">
            {BLOOD_GROUPS.map((g) => (
              <button
                type="button"
                key={g}
                aria-pressed={form.blood_group === g}
                onClick={() => setForm({ ...form, blood_group: g })}
                className={cx(
                  'min-h-11 rounded-xl border py-3 text-lg font-extrabold transition',
                  form.blood_group === g ? 'border-red-500 bg-red-600 text-white' : 'border-slate-700 bg-slate-800/50 text-slate-300 hover:border-red-500/50',
                )}
              >
                {g}
              </button>
            ))}
          </div>
          <p className="mt-2 text-sm text-slate-400">
            {t('sos.willAlert')} <span className="font-semibold text-slate-200">{COMPATIBILITY[form.blood_group].join(', ')}</span>
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="sos-name">
              {t('sos.name')}
            </label>
            <input id="sos-name" className="input" value={form.requester_name} onChange={set('requester_name')} required />
          </div>
          <div>
            <label className="label" htmlFor="sos-phone">
              {t('sos.phone')}
            </label>
            <input id="sos-phone" className="input" value={form.contact_phone} onChange={set('contact_phone')} placeholder="+91 …" inputMode="tel" />
          </div>
          <div className="sm:col-span-2">
            <LocationPicker withHospital idPrefix="sos" value={form} onChange={(v) => setForm({ ...form, ...v })} />
            <div className="mt-2">
              {form.lat != null ? (
                <p className="text-sm text-emerald-500">✓ {t('geo.added')}</p>
              ) : (
                <button type="button" onClick={useMyLocation} disabled={locating} className="flex items-center gap-1.5 text-sm font-semibold text-sky-500 hover:underline">
                  <LocateFixed className="h-4 w-4" /> {t('geo.atHospital')}
                </button>
              )}
            </div>
          </div>
          <div>
            <label className="label" htmlFor="sos-units">
              {t('sos.units')}
            </label>
            <input id="sos-units" type="number" min={1} max={10} className="input" value={form.units_needed} onChange={set('units_needed')} />
          </div>
        </div>

        <div>
          <span className="label">{t('sos.urgency')}</span>
          <div className="grid gap-2 sm:grid-cols-3">
            {URGENCIES.map(([u, active]) => (
              <button
                type="button"
                key={u}
                aria-pressed={form.urgency === u}
                onClick={() => setForm({ ...form, urgency: u })}
                className={cx('rounded-xl border px-4 py-3 text-left transition', form.urgency === u ? active : 'border-slate-700 text-slate-300 hover:border-slate-500')}
              >
                <div className="font-bold">{t(`urgency.${u}`)}</div>
                <div className="text-xs opacity-80">{t(`urgency.${u}Hint`)}</div>
              </button>
            ))}
          </div>
        </div>

        <ErrorBox error={error} />
        <button className="btn-primary w-full py-3.5 text-lg" disabled={busy}>
          {busy ? <Spinner /> : <Siren className="h-5 w-5" />} {t('sos.broadcast')}
        </button>
        <p className="flex items-center justify-center gap-1.5 text-center text-xs text-slate-500">
          <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
          <span>{t('sos.faster', { cmd: '/sos', bot: config?.bot_username || 'BloodLinkBot' })}</span>
        </p>
      </form>
    </div>
  );
}
