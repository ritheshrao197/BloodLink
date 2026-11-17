import { useState } from 'react';
import { CheckCircle2, Send, Siren } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { BLOOD_GROUPS, COMPATIBILITY, cx } from '../lib/utils';
import { BadgeChip, BloodTag, ErrorBox, PageHeader, Spinner } from '../components/ui';
import LocationPicker from '../components/LocationPicker';

const URGENCIES = [
  ['Critical', 'Needed within the hour', 'border-red-500 bg-red-600/15 text-red-300'],
  ['High', 'Needed today', 'border-orange-500 bg-orange-500/15 text-orange-300'],
  ['Normal', 'Planned procedure', 'border-amber-400 bg-amber-400/10 text-amber-200'],
];

export default function SOS() {
  const { user, config } = useSession();
  const [form, setForm] = useState({
    requester_name: user?.role === 'hospital' ? user.name : '',
    blood_group: 'O+',
    hospital: '',
    state: user?.state || null,
    city: user?.state ? user.city : '',
    units_needed: 1,
    urgency: 'Critical',
    contact_phone: '',
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      setResult(await api.sos({ ...form, units_needed: Number(form.units_needed) }));
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
            <Siren className="h-8 w-8 animate-pulse text-red-500" />
          </div>
          <h1 className="mt-4 text-3xl font-extrabold">🚨 SOS Broadcasted!</h1>
          <p className="mt-2 text-slate-300">
            Request <b>#{r.id}</b> for <b>{r.units_needed} unit(s) of {r.blood_group}</b> at {r.hospital}, {r.city}.
          </p>
          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-800/60 p-4">
              <div className="text-3xl font-extrabold text-red-400">{result.matched_donors}</div>
              <div className="text-sm text-slate-400">compatible donors matched</div>
            </div>
            <div className="rounded-xl bg-slate-800/60 p-4">
              <div className="text-3xl font-extrabold text-sky-400">{result.telegram_reachable}</div>
              <div className="text-sm text-slate-400">alerted instantly on Telegram</div>
            </div>
          </div>
          {!config?.telegram_enabled && (
            <p className="mt-3 text-xs text-amber-300/80">Telegram bot token not configured on the server — alerts are logged only.</p>
          )}
        </div>

        {result.donors.length > 0 && (
          <div className="card mt-6 p-5">
            <h2 className="mb-3 font-bold">Matched donors</h2>
            <ul className="divide-y divide-slate-800">
              {result.donors.map((d) => (
                <li key={d.id} className="flex items-center justify-between py-2.5">
                  <div className="flex items-center gap-3">
                    <BloodTag group={d.blood_group} size="sm" />
                    <span className="font-medium">{d.name}</span>
                    <span className="text-sm text-slate-500">{d.city}</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm">
                    {d.telegram_linked && <Send className="h-4 w-4 text-sky-400" title="Telegram alert sent" />}
                    <BadgeChip badge={d.badge} />
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="mt-6 flex justify-center gap-3">
          <Link to="/" className="btn-primary">
            Track on live feed
          </Link>
          <button className="btn-ghost" onClick={() => setResult(null)}>
            New request
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader icon={Siren} title="Emergency SOS" subtitle="Broadcast to every compatible, available donor in seconds." />
      <form onSubmit={submit} className="card space-y-6 p-6 sm:p-8">
        <div>
          <span className="label">Blood group needed</span>
          <div className="grid grid-cols-4 gap-2 sm:grid-cols-8">
            {BLOOD_GROUPS.map((g) => (
              <button
                type="button"
                key={g}
                onClick={() => setForm({ ...form, blood_group: g })}
                className={cx(
                  'rounded-xl border py-3 text-lg font-extrabold transition',
                  form.blood_group === g ? 'border-red-500 bg-red-600 text-white' : 'border-slate-700 bg-slate-800/50 text-slate-300 hover:border-red-500/50',
                )}
              >
                {g}
              </button>
            ))}
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Will alert donors with: <span className="font-semibold text-slate-200">{COMPATIBILITY[form.blood_group].join(', ')}</span>
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label" htmlFor="sos-name">Patient / requester name</label>
            <input id="sos-name" className="input" value={form.requester_name} onChange={set('requester_name')} required />
          </div>
          <div>
            <label className="label" htmlFor="sos-phone">Contact phone (shared with responding donors)</label>
            <input id="sos-phone" className="input" value={form.contact_phone} onChange={set('contact_phone')} placeholder="+91 …" />
          </div>
          <div className="sm:col-span-2">
            <LocationPicker withHospital idPrefix="sos" value={form} onChange={(v) => setForm({ ...form, ...v })} />
          </div>
          <div>
            <label className="label" htmlFor="sos-units">Units needed</label>
            <input id="sos-units" type="number" min={1} max={10} className="input" value={form.units_needed} onChange={set('units_needed')} />
          </div>
        </div>

        <div>
          <span className="label">Urgency</span>
          <div className="grid gap-2 sm:grid-cols-3">
            {URGENCIES.map(([u, hint, active]) => (
              <button
                type="button"
                key={u}
                onClick={() => setForm({ ...form, urgency: u })}
                className={cx('rounded-xl border px-4 py-3 text-left transition', form.urgency === u ? active : 'border-slate-700 text-slate-300 hover:border-slate-500')}
              >
                <div className="font-bold">{u}</div>
                <div className="text-xs opacity-80">{hint}</div>
              </button>
            ))}
          </div>
        </div>

        <ErrorBox error={error} />
        <button className="btn-primary w-full py-3.5 text-lg" disabled={busy}>
          {busy ? <Spinner /> : <Siren className="h-5 w-5" />} Broadcast SOS
        </button>
        <p className="flex items-center justify-center gap-1.5 text-center text-xs text-slate-500">
          <CheckCircle2 className="h-3.5 w-3.5" /> Faster on the go: send <code className="text-slate-300">/sos</code> to @
          {config?.bot_username || 'BloodLinkBot'} on Telegram.
        </p>
      </form>
    </div>
  );
}
