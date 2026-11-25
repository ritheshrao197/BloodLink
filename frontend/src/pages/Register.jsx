import { useState } from 'react';
import { Gift, HeartHandshake, Send } from 'lucide-react';
import { api } from '../lib/api';
import { Link, useRouter } from '../lib/router';
import { useSession } from '../lib/session';
import { BLOOD_GROUPS, cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { CopyField, ErrorBox, PageHeader, Spinner } from '../components/ui';
import SignInByCode, { TelegramLinkButton } from '../components/SignInByCode';
import LocationPicker from '../components/LocationPicker';
import { ConditionsCheck, EMPTY_CONDITIONS, HealthFields, PermanentNotice, WhoCanDonate, conditionsAnswer } from '../components/Eligibility';

export default function Register() {
  const { search, navigate } = useRouter();
  const { signIn, user } = useSession();
  const { t, lang } = useI18n();
  const ref = new URLSearchParams(search).get('ref') || '';
  const [form, setForm] = useState({ name: '', blood_group: 'O+', state: null, city: '', phone: '', role: 'donor', referred_by: ref });
  const [health, setHealth] = useState({ sex: null, date_of_birth: null, weight_kg: null });
  const [conditions, setConditions] = useState(EMPTY_CONDITIONS);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [created, setCreated] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const donor = form.role === 'donor';
  const screened = !donor || conditionsAnswer(conditions) !== null;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      // the account remembers the language it was created in (used for Telegram alerts)
      // donors answer the health basics and the permanent-conditions check (only the outcome is stored)
      const screening = donor ? { ...health, conditions: conditionsAnswer(conditions) } : {};
      const res = await api.register({
        ...form,
        ...screening,
        language: lang,
        referred_by: form.referred_by.trim() || null,
        phone: form.phone.trim() || null,
      });
      signIn(res.user, res.token);
      setCreated(res.user);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  if (created) {
    const points = <span className="font-bold text-red-400">{created.points} BLP</span>;
    const [before, after] = t(created.referred_by ? 'register.earnedBonus' : 'register.earned', { points: '\u0000' }).split('\u0000');
    return (
      <div className="mx-auto max-w-xl">
        <div className="card p-8 text-center">
          <div className="text-5xl">🎉</div>
          <h1 className="mt-3 text-3xl font-extrabold">{t('register.welcome', { name: created.name })}</h1>
          <p className="mt-2 text-slate-300">
            {before}
            {points}
            {after}
          </p>
          {created.permanently_ineligible && (
            <div className="mt-6 text-left">
              <PermanentNotice />
            </div>
          )}
          <div className="mt-6 rounded-xl bg-slate-800/60 p-4">
            <div className="text-sm text-slate-400">{t('register.yourCode')}</div>
            <div className="mt-1 font-mono text-3xl font-extrabold tracking-wider text-red-400">{created.referral_code}</div>
            <div className="mt-1 text-xs text-slate-500">{t('register.codeHint')}</div>
          </div>
          <div className="mt-6 space-y-4 text-left">
            <CopyField label={t('register.tgInvite')} value={created.referral_link} />
            <CopyField label={t('register.webInvite')} value={created.web_referral_link} />
          </div>
          <div className="mt-6 text-left">
            <TelegramLinkButton className="w-full" />
            <p className="mt-2 text-xs text-slate-400">{t('auth.keepSafe')}</p>
          </div>
          <Link to="/profile" className="btn-ghost mt-3 w-full">
            {t('register.dashboard')}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-[1.3fr_1fr]">
      <div>
        <PageHeader icon={HeartHandshake} title={t('register.title')} subtitle={t('register.subtitle')} />
        {user && (
          <div className="mb-4 rounded-lg border border-sky-500/30 bg-sky-950/30 p-3 text-sm text-sky-200">{t('register.signedInAs', { name: user.name })}</div>
        )}
        <form onSubmit={submit} className="card space-y-5 p-6 sm:p-8">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="label" htmlFor="reg-name">
                {t('register.name')}
              </label>
              <input id="reg-name" className="input" value={form.name} onChange={set('name')} required autoComplete="name" />
            </div>
            <div className="sm:col-span-2">
              <LocationPicker idPrefix="reg" value={form} onChange={(v) => setForm({ ...form, ...v })} />
            </div>
            <div>
              <label className="label" htmlFor="reg-phone">
                {t('register.phone')}
              </label>
              <input id="reg-phone" className="input" value={form.phone} onChange={set('phone')} placeholder="+91 …" inputMode="tel" autoComplete="tel" />
            </div>
          </div>
          <div>
            <span className="label">{t('register.group')}</span>
            <div className="grid grid-cols-4 gap-2">
              {BLOOD_GROUPS.map((g) => (
                <button
                  type="button"
                  key={g}
                  aria-pressed={form.blood_group === g}
                  onClick={() => setForm({ ...form, blood_group: g })}
                  className={cx(
                    'min-h-11 rounded-lg border py-2.5 font-extrabold transition',
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
              <label className="label" htmlFor="reg-role">
                {t('register.role')}
              </label>
              <select id="reg-role" className="input" value={form.role} onChange={set('role')}>
                <option value="donor">{t('register.roleDonor')}</option>
                <option value="hospital">{t('register.roleHospital')}</option>
              </select>
            </div>
            <div>
              <label className="label" htmlFor="reg-ref">
                {t('register.referral')}
              </label>
              <input id="reg-ref" className="input font-mono uppercase" value={form.referred_by} onChange={set('referred_by')} placeholder="USER_12345" />
            </div>
          </div>
          {donor && (
            <div className="space-y-4 border-t border-slate-800 pt-5">
              <div>
                <h2 className="font-bold">{t('register.healthTitle')}</h2>
                <p className="text-xs text-slate-400">{t('register.healthIntro')}</p>
              </div>
              <HealthFields value={health} onChange={setHealth} idPrefix="reg-health" required />
              <WhoCanDonate />
              <ConditionsCheck value={conditions} onChange={setConditions} idPrefix="reg-cond" />
            </div>
          )}
          <ErrorBox error={error} />
          <button className="btn-primary w-full py-3 text-base" disabled={busy || !screened}>
            {busy ? <Spinner /> : <Gift className="h-5 w-5" />} {t('register.submit', { n: form.referred_by.trim() ? 100 : 50 })}
          </button>
        </form>
      </div>

      <aside className="space-y-4 lg:pt-24">
        <div className="card p-6">
          <h2 className="font-bold">{t('register.whatYouGet')}</h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            {['perk1', 'perk2', 'perk3', 'perk4', 'perk5'].map((k) => (
              <li key={k}>{t(`register.${k}`)}</li>
            ))}
          </ul>
        </div>
        <div className="card p-6">
          <h2 className="mb-3 font-bold">{t('register.already')}</h2>
          <SignInByCode onSignedIn={() => navigate('/profile')} />
        </div>
      </aside>
    </div>
  );
}
