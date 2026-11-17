import { useState } from 'react';
import { Gift, HeartHandshake, Send } from 'lucide-react';
import { api } from '../lib/api';
import { Link, useRouter } from '../lib/router';
import { useSession } from '../lib/session';
import { BLOOD_GROUPS, cx } from '../lib/utils';
import { CopyField, ErrorBox, PageHeader, Spinner } from '../components/ui';
import SignInByCode from '../components/SignInByCode';
import LocationPicker from '../components/LocationPicker';

export default function Register() {
  const { search, navigate } = useRouter();
  const { signIn, user } = useSession();
  const ref = new URLSearchParams(search).get('ref') || '';
  const [form, setForm] = useState({ name: '', blood_group: 'O+', state: null, city: '', phone: '', role: 'donor', referred_by: ref });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [created, setCreated] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await api.register({ ...form, referred_by: form.referred_by.trim() || null, phone: form.phone.trim() || null });
      signIn(res.user);
      setCreated(res.user);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  if (created) {
    return (
      <div className="mx-auto max-w-xl">
        <div className="card p-8 text-center">
          <div className="text-5xl">🎉</div>
          <h1 className="mt-3 text-3xl font-extrabold">Welcome, {created.name}!</h1>
          <p className="mt-2 text-slate-300">
            You earned <span className="font-bold text-red-400">{created.points} BLP</span>
            {created.referred_by && ' (including a +50 welcome bonus)'} and the 🥉 Bronze badge.
          </p>
          <div className="mt-6 rounded-xl bg-slate-800/60 p-4">
            <div className="text-sm text-slate-400">Your referral code</div>
            <div className="mt-1 font-mono text-3xl font-extrabold tracking-wider text-red-400">{created.referral_code}</div>
            <div className="mt-1 text-xs text-slate-500">Also your sign-in code, so keep it handy.</div>
          </div>
          <div className="mt-6 space-y-4 text-left">
            <CopyField label="Telegram invite link" value={created.referral_link} />
            <CopyField label="Web invite link" value={created.web_referral_link} />
          </div>
          <a href={created.telegram_link_url} target="_blank" rel="noreferrer" className="btn-primary mt-6 w-full bg-sky-600 shadow-sky-900/40 hover:bg-sky-500">
            <Send className="h-4 w-4" /> Link Telegram to receive SOS alerts
          </a>
          <Link to="/profile" className="btn-ghost mt-3 w-full">
            Go to my dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-[1.3fr_1fr]">
      <div>
        <PageHeader icon={HeartHandshake} title="Become a Donor" subtitle="Join the network that answers emergencies in minutes, not hours." />
        {user && (
          <div className="mb-4 rounded-lg border border-sky-500/30 bg-sky-950/30 p-3 text-sm text-sky-200">
            You're signed in as <b>{user.name}</b>. Registering again creates a separate account.
          </div>
        )}
        <form onSubmit={submit} className="card space-y-5 p-6 sm:p-8">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="label" htmlFor="reg-name">Full name</label>
              <input id="reg-name" className="input" value={form.name} onChange={set('name')} required />
            </div>
            <div className="sm:col-span-2">
              <LocationPicker idPrefix="reg" value={form} onChange={(v) => setForm({ ...form, ...v })} />
            </div>
            <div>
              <label className="label" htmlFor="reg-phone">Phone (optional)</label>
              <input id="reg-phone" className="input" value={form.phone} onChange={set('phone')} placeholder="+91 …" />
            </div>
          </div>
          <div>
            <span className="label">Blood group</span>
            <div className="grid grid-cols-4 gap-2">
              {BLOOD_GROUPS.map((g) => (
                <button
                  type="button"
                  key={g}
                  onClick={() => setForm({ ...form, blood_group: g })}
                  className={cx(
                    'rounded-lg border py-2.5 font-extrabold transition',
                    form.blood_group === g ? 'border-red-500 bg-red-600 text-white' : 'border-slate-700 bg-slate-800/50 text-slate-300 hover:border-red-500/50',
                  )}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="reg-role">I am registering as</label>
              <select id="reg-role" className="input" value={form.role} onChange={set('role')}>
                <option value="donor">Individual donor</option>
                <option value="hospital">Hospital / blood bank</option>
              </select>
            </div>
            <div>
              <label className="label" htmlFor="reg-ref">Referral code (optional)</label>
              <input id="reg-ref" className="input font-mono uppercase" value={form.referred_by} onChange={set('referred_by')} placeholder="USER_12345" />
            </div>
          </div>
          <ErrorBox error={error} />
          <button className="btn-primary w-full py-3 text-base" disabled={busy}>
            {busy ? <Spinner /> : <Gift className="h-5 w-5" />} Register &amp; Earn {form.referred_by.trim() ? 100 : 50} Points
          </button>
        </form>
      </div>

      <aside className="space-y-4 lg:pt-24">
        <div className="card p-6">
          <h2 className="font-bold">What you get</h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            <li>⭐ +50 BLP for joining (+50 more with a referral code)</li>
            <li>🩸 +100 BLP per donation, +20 for responding in under 5 minutes</li>
            <li>🤝 +50 BLP per friend who joins, +200 BLP and a voucher when they donate</li>
            <li>🎁 Redeem BLP for coffee, movies and merch</li>
            <li>🏆 Climb from 🥉 Bronze to 💎 Platinum</li>
          </ul>
        </div>
        <div className="card p-6">
          <h2 className="mb-3 font-bold">Already registered?</h2>
          <SignInByCode onSignedIn={() => navigate('/profile')} />
        </div>
      </aside>
    </div>
  );
}
