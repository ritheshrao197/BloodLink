import { useState } from 'react';
import { CalendarClock, CheckCircle2, HeartPulse, ShieldAlert, Stethoscope } from 'lucide-react';
import { api } from '../lib/api';
import { cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { useToast } from './Toast';
import { ErrorBox, Spinner } from './ui';

const QUESTIONS = ['fever', 'antibiotics', 'alcohol', 'tattoo', 'surgery', 'pregnancy'];
// reasons that come from what we already know (no questionnaire can change them today)
const BLOCKING = new Set(['interval', 'deferred', 'too_young', 'too_old', 'underweight']);

export function ReasonList({ reasons }) {
  const { t, date } = useI18n();
  return (
    <ul className="space-y-1.5">
      {reasons.map((r) => (
        <li key={r.code} className="flex gap-2 text-sm">
          <CalendarClock className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
          <span>{t(`elig.r.${r.code}`, { date: r.until ? date(r.until) : '', days: r.days ?? '' })}</span>
        </li>
      ))}
    </ul>
  );
}

function HealthFields({ value, onChange, idPrefix }) {
  const { t } = useI18n();
  const set = (k) => (e) => onChange({ ...value, [k]: e.target.value || null });
  const today = new Date().toISOString().slice(0, 10);
  return (
    <div className="grid gap-3 sm:grid-cols-3">
      <div>
        <label className="label" htmlFor={`${idPrefix}-sex`}>
          {t('elig.sex')}
        </label>
        <select id={`${idPrefix}-sex`} className="input" value={value.sex || ''} onChange={set('sex')}>
          <option value="">—</option>
          <option value="male">{t('elig.male')}</option>
          <option value="female">{t('elig.female')}</option>
          <option value="other">{t('elig.other')}</option>
        </select>
      </div>
      <div>
        <label className="label" htmlFor={`${idPrefix}-dob`}>
          {t('elig.dob')}
        </label>
        <input id={`${idPrefix}-dob`} type="date" max={today} className="input" value={value.date_of_birth || ''} onChange={set('date_of_birth')} />
      </div>
      <div>
        <label className="label" htmlFor={`${idPrefix}-weight`}>
          {t('elig.weight')}
        </label>
        <input
          id={`${idPrefix}-weight`}
          type="number"
          min={20}
          max={250}
          inputMode="numeric"
          className="input"
          value={value.weight_kg ?? ''}
          onChange={(e) => onChange({ ...value, weight_kg: e.target.value ? Number(e.target.value) : null })}
        />
      </div>
    </div>
  );
}

function YesNo({ value, onChange, label }) {
  const { t } = useI18n();
  return (
    <div className="flex items-center justify-between gap-3 py-2">
      <span className="text-sm text-slate-300">{label}</span>
      <div className="flex shrink-0 rounded-lg bg-slate-800 p-0.5 text-xs font-semibold" role="radiogroup" aria-label={label}>
        {[
          [false, t('elig.no')],
          [true, t('elig.yes')],
        ].map(([v, text]) => (
          <button
            key={text}
            type="button"
            role="radio"
            aria-checked={value === v}
            onClick={() => onChange(v)}
            className={cx(
              'min-h-8 rounded-md px-3 transition',
              value === v ? (v ? 'bg-amber-500 text-white' : 'bg-emerald-600 text-white') : 'text-slate-400 hover:text-slate-50',
            )}
          >
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}

/**
 * Pre-donation self-check. Calls onEligible(screening) when the donor may go ahead;
 * the same `screening` must be sent with the donation (the server re-checks it).
 */
export function EligibilityForm({ user, onEligible }) {
  const { t } = useI18n();
  const known = user.eligibility || { reasons: [], profile: {} };
  const [health, setHealth] = useState({
    sex: known.profile?.sex || null,
    date_of_birth: known.profile?.date_of_birth || null,
    weight_kg: known.profile?.weight_kg ?? null,
  });
  const [basicsConfirmed, setBasicsConfirmed] = useState(false);
  const [answers, setAnswers] = useState(Object.fromEntries(QUESTIONS.map((q) => [q, false])));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const blocking = known.reasons.filter((r) => BLOCKING.has(r.code));
  if (blocking.length) return <NotNow reasons={blocking} />;
  if (result && !result.eligible) return <NotNow reasons={result.reasons} honest={result.reasons.some((r) => QUESTIONS.includes(r.code))} />;

  const profileComplete = health.sex && health.date_of_birth && health.weight_kg;
  const questions = QUESTIONS.filter((q) => q !== 'pregnancy' || health.sex === 'female');

  const submit = async () => {
    setBusy(true);
    setError(null);
    const screening = {
      answers: Object.fromEntries(questions.map((q) => [q, answers[q]])),
      basics_confirmed: basicsConfirmed,
      health: Object.fromEntries(Object.entries(health).filter(([, v]) => v != null && v !== '')),
    };
    try {
      const res = await api.checkEligibility(user.id, screening);
      setResult(res);
      if (res.eligible) onEligible(screening);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-3 rounded-xl bg-slate-800/60 p-3">
        <Stethoscope className="mt-0.5 h-5 w-5 shrink-0 text-blood-500" aria-hidden />
        <div>
          <p className="font-bold">{t('elig.title')}</p>
          <p className="text-xs text-slate-400">{t('elig.intro')}</p>
        </div>
      </div>

      {!profileComplete && (
        <fieldset className="space-y-3">
          <legend className="mb-2 text-sm font-semibold">{t('elig.basicsTitle')}</legend>
          <HealthFields value={health} onChange={setHealth} idPrefix="elig" />
          <label className="flex cursor-pointer items-start gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              className="mt-0.5 h-4 w-4 shrink-0 accent-red-600"
              checked={basicsConfirmed}
              onChange={(e) => setBasicsConfirmed(e.target.checked)}
            />
            {t('elig.basicsConfirm')}
          </label>
        </fieldset>
      )}

      <fieldset>
        <legend className="mb-1 text-sm font-semibold">{t('elig.questionsTitle')}</legend>
        <div className="divide-y divide-slate-800">
          {questions.map((q) => (
            <YesNo key={q} label={t(`elig.q.${q}`)} value={answers[q]} onChange={(v) => setAnswers({ ...answers, [q]: v })} />
          ))}
        </div>
      </fieldset>

      <ErrorBox error={error} />
      <button className="btn-primary w-full" disabled={busy || (!profileComplete && !basicsConfirmed)} onClick={submit}>
        {busy ? <Spinner /> : <HeartPulse className="h-4 w-4" />} {t('elig.check')}
      </button>
      <p className="text-center text-[11px] text-slate-500">{t('elig.disclaimer')}</p>
    </div>
  );
}

function NotNow({ reasons, honest }) {
  const { t } = useI18n();
  return (
    <div className="space-y-3 rounded-xl border border-amber-500/40 bg-amber-950/30 p-4 text-amber-200">
      <p className="flex items-center gap-2 font-bold">
        <ShieldAlert className="h-5 w-5" aria-hidden /> {t('elig.notNow')}
      </p>
      <ReasonList reasons={reasons} />
      {honest && <p className="text-xs opacity-80">{t('elig.thanks')}</p>}
      <p className="text-[11px] opacity-70">{t('elig.disclaimer')}</p>
    </div>
  );
}

/** Profile card: when the donor can donate next, self-reported pauses, and health basics. */
export function EligibilityCard({ user, onUser }) {
  const { t, date } = useI18n();
  const toast = useToast();
  const e = user.eligibility;
  const [health, setHealth] = useState({
    sex: e?.profile?.sex || null,
    date_of_birth: e?.profile?.date_of_birth || null,
    weight_kg: e?.profile?.weight_kg ?? null,
  });
  const [busy, setBusy] = useState(false);
  if (!e) return null;

  const days = e.next_eligible_at ? Math.ceil((new Date(e.next_eligible_at) - Date.now()) / 86400000) : 0;
  const waiting = days > 0;
  const pausedUntil = e.deferred_until && new Date(e.deferred_until) > new Date() ? e.deferred_until : null;
  const ready = e.eligible;

  const save = async () => {
    setBusy(true);
    try {
      onUser(await api.setHealth(user.id, Object.fromEntries(Object.entries(health).filter(([, v]) => v != null && v !== ''))));
      toast(t('elig.saved'));
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setBusy(false);
    }
  };
  const undo = async () => {
    try {
      onUser(await api.clearDeferral(user.id));
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  return (
    <div className="card p-6">
      <h2 className="flex items-center gap-2 text-lg font-bold">
        <HeartPulse className="h-5 w-5 text-blood-500" aria-hidden /> {t('elig.card')}
      </h2>
      <div className={cx('mt-4 flex items-center gap-3 rounded-xl p-4', ready ? 'bg-emerald-950/40 text-emerald-300' : 'bg-amber-950/30 text-amber-200')}>
        {ready ? <CheckCircle2 className="h-6 w-6 shrink-0" /> : <CalendarClock className="h-6 w-6 shrink-0" />}
        <div className="min-w-0">
          <p className="font-bold">{ready ? t('elig.canDonate') : waiting ? t('elig.nextFrom', { date: date(e.next_eligible_at) }) : t('elig.notNow')}</p>
          <p className="text-xs opacity-80">{waiting ? t('elig.daysLeft', { n: days }) : !user.last_donation_at ? t('elig.neverDonated') : ''}</p>
        </div>
      </div>
      {!ready && !waiting && <div className="mt-3 text-amber-200"><ReasonList reasons={e.reasons} /></div>}
      {waiting && (
        <div className="progress-bar mt-3">
          <div className="progress-streak h-full rounded-full" style={{ width: `${Math.max(4, 100 - (100 * days) / e.interval_days)}%` }} />
        </div>
      )}
      {pausedUntil && (
        <p className="mt-3 flex flex-wrap items-center justify-between gap-2 text-sm text-slate-400">
          {t('elig.pausedUntil', { date: date(pausedUntil) })}
          <button onClick={undo} className="text-xs font-semibold text-blood-500 hover:underline">
            {t('elig.undo')}
          </button>
        </p>
      )}
      <p className="mt-3 text-xs text-slate-500">{t('elig.hint')}</p>

      <h3 className="mt-6 text-sm font-semibold">{t('elig.editBasics')}</h3>
      <div className="mt-2">
        <HealthFields value={health} onChange={setHealth} idPrefix="profile" />
      </div>
      <button className="btn-ghost mt-3 min-h-10 py-2 text-sm" onClick={save} disabled={busy}>
        {busy ? <Spinner className="h-4 w-4" /> : null} {t('elig.save')}
      </button>
    </div>
  );
}
