import { useState } from 'react';
import { CalendarDays, CheckCircle2, ClipboardList, MapPin, Plus, Tent, Trophy, Users } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { useToast } from '../components/Toast';
import { ReasonList } from '../components/Eligibility';
import LocationPicker from '../components/LocationPicker';
import { BloodTag, Empty, ErrorBox, Loading, Modal, PageHeader, Spinner } from '../components/ui';

export default function Camps() {
  const { user } = useSession();
  const { t } = useI18n();
  const [tab, setTab] = useState('upcoming');
  const [creating, setCreating] = useState(false);
  const list = usePoll(() => api.camps.list(tab, user?.id), 20000, `${tab}-${user?.id}`);
  const top = usePoll(() => api.camps.leaderboard(), 0);

  return (
    <div className="space-y-8">
      <PageHeader icon={Tent} title={t('camps.title')} subtitle={t('camps.subtitle')}>
        {user && (
          <button className="btn-primary" onClick={() => setCreating(true)}>
            <Plus className="h-4 w-4" /> {t('camps.host')}
          </button>
        )}
      </PageHeader>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <section>
          <div className="mb-4 flex gap-1 rounded-xl bg-slate-900 p-1" role="tablist">
            {['upcoming', 'past'].map((k) => (
              <button
                key={k}
                role="tab"
                aria-selected={tab === k}
                onClick={() => setTab(k)}
                className={cx('min-h-10 flex-1 rounded-lg px-4 py-2 text-sm font-semibold transition', tab === k ? 'bg-brand-700 text-white' : 'text-slate-300 hover:bg-slate-800')}
              >
                {t(`camps.${k}`)}
              </button>
            ))}
          </div>
          <ErrorBox error={list.error} />
          {list.loading && !list.data ? (
            <Loading rows={4} />
          ) : !list.data?.length ? (
            <Empty icon={Tent} title={t('camps.none')} />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {list.data.map((c) => (
                <CampCard key={c.id} camp={c} onChange={list.reload} />
              ))}
            </div>
          )}
        </section>

        <aside className="space-y-4">
          {!user && (
            <div className="card p-5 text-sm text-slate-300">
              {t('camps.signIn')}{' '}
              <Link to="/profile" className="font-semibold text-brand-600 hover:underline">
                {t('common.signIn')}
              </Link>
            </div>
          )}
          <div className="card p-5">
            <p className="overline flex items-center gap-1.5">
              <Trophy className="h-3.5 w-3.5" /> {t('camps.leaderboard')}
            </p>
            <ol className="mt-3 space-y-2">
              {(top.data || []).slice(0, 5).map((c, i) => (
                <li key={c.id} className="flex items-center gap-3 text-sm">
                  <span className={cx('w-6 font-extrabold', i < 3 ? 'text-amber-500' : 'text-slate-500')}>#{i + 1}</span>
                  <span className="min-w-0 flex-1 truncate font-semibold">{c.title}</span>
                  <span className="shrink-0 text-xs text-emerald-500">{t('camps.attended', { n: c.attended })}</span>
                </li>
              ))}
            </ol>
          </div>
        </aside>
      </div>

      {creating && <CreateCamp user={user} onClose={() => setCreating(false)} onDone={list.reload} />}
    </div>
  );
}

function CampCard({ camp: c, onChange }) {
  const { user } = useSession();
  const { t, date, locale } = useI18n();
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  const [blocked, setBlocked] = useState(null);
  const [managing, setManaging] = useState(false);
  const start = new Date(c.starts_at);
  const going = c.my_status === 'Registered';
  const pct = Math.min(100, Math.round((100 * c.registered) / c.expected_donors));
  const upcoming = c.status === 'Upcoming';
  const organiser = user && c.created_by === user.id;

  const rsvp = async () => {
    setBusy(true);
    setBlocked(null);
    try {
      const res = await api.camps.rsvp(c.id, user.id);
      toast(res.status === 'registered' ? t('camps.rsvpOk') : t('camps.rsvpCancelled'));
      onChange();
    } catch (e) {
      if (e.data?.eligibility) setBlocked(e.data.eligibility.reasons);
      else toast(e.message, 'error');
    } finally {
      setBusy(false);
    }
  };

  return (
    <article className="card card-hover flex flex-col p-5">
      <div className="flex items-start gap-3">
        <div className="flex w-14 shrink-0 flex-col items-center rounded-xl bg-brand-600/10 py-1.5 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300">
          <span className="text-[11px] font-bold uppercase">{start.toLocaleDateString(locale, { month: 'short' })}</span>
          <span className="text-2xl font-extrabold leading-none">{start.getDate()}</span>
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-bold leading-tight">{c.title}</h3>
          <p className="truncate text-sm text-slate-400">{c.organizer}</p>
        </div>
        {c.my_status === 'Attended' && <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-500" aria-label={t('camps.donated')} />}
      </div>
      <div className="mt-3 space-y-1 text-sm text-slate-300">
        <p className="flex items-center gap-2">
          <MapPin className="h-4 w-4 shrink-0 text-slate-500" />
          <span>
            {c.venue}, {c.city}
          </span>
        </p>
        <p className="flex items-center gap-2">
          <CalendarDays className="h-4 w-4 shrink-0 text-slate-500" />
          {date(c.starts_at)} · {start.toLocaleTimeString(locale, { hour: 'numeric', minute: '2-digit' })}
        </p>
        {c.team && (
          <p className="flex items-center gap-2">
            <Users className="h-4 w-4 shrink-0 text-slate-500" />
            <Link to={`/teams?id=${c.team.id}`} className="hover:underline">
              {t('camps.team', { name: c.team.name })}
            </Link>
          </p>
        )}
      </div>
      <div className="mt-3">
        <div className="mb-1 flex justify-between text-xs text-slate-400">
          <span>{upcoming ? t('camps.registered', { n: c.registered }) : t('camps.attended', { n: c.attended })}</span>
          <span>{t('camps.expected', { n: c.expected_donors })}</span>
        </div>
        <div className="progress-bar h-1.5">
          <div className="progress-fill" style={{ width: `${upcoming ? pct : Math.min(100, (100 * c.attended) / c.expected_donors)}%` }} />
        </div>
      </div>
      {blocked && (
        <div className="mt-3 rounded-lg border border-amber-500/40 bg-amber-950/30 p-3 text-amber-200">
          <p className="mb-1 text-sm font-semibold">{t('camps.cantRsvp')}</p>
          <ReasonList reasons={blocked} />
        </div>
      )}
      <div className="mt-auto flex flex-wrap gap-2 pt-4">
        {upcoming && user && (
          <button onClick={rsvp} disabled={busy} className={cx('flex-1', going ? 'btn-ghost' : 'btn-primary')}>
            {busy ? <Spinner className="h-4 w-4" /> : null}
            {going ? t('camps.going') : t('camps.rsvp')}
          </button>
        )}
        {organiser && (
          <button onClick={() => setManaging(true)} className="btn-ghost">
            <ClipboardList className="h-4 w-4" /> {t('camps.attendees')}
          </button>
        )}
      </div>
      {managing && <Attendees camp={c} onClose={() => setManaging(false)} onChange={onChange} />}
    </article>
  );
}

function Attendees({ camp, onClose, onChange }) {
  const { user } = useSession();
  const { t } = useI18n();
  const toast = useToast();
  const { data, loading, reload } = usePoll(() => api.camps.attendees(camp.id, user.id), 0);
  const mark = async (a) => {
    try {
      await api.camps.attend(camp.id, user.id, a.id);
      toast(t('camps.attendedOk'));
      reload();
      onChange();
    } catch (e) {
      toast(e.message, 'error');
    }
  };
  return (
    <Modal open onClose={onClose} title={t('camps.attendees')}>
      <p className="mb-3 text-sm text-slate-400">{t('camps.organizing')}</p>
      {loading && !data ? (
        <Loading rows={3} />
      ) : (
        <ul className="max-h-96 divide-y divide-slate-800 overflow-y-auto">
          {(data || []).map((a) => (
            <li key={a.id} className="flex items-center gap-3 py-2.5">
              <BloodTag group={a.blood_group} size="sm" />
              <div className="min-w-0 flex-1">
                <div className="truncate font-semibold">{a.name}</div>
                {a.phone && <div className="text-xs text-slate-500">{a.phone}</div>}
              </div>
              {a.status === 'Attended' ? (
                <span className="text-sm font-semibold text-emerald-500">✓ {t('camps.donated')}</span>
              ) : (
                <button onClick={() => mark(a)} className="btn-ghost min-h-9 py-1 text-xs">
                  {t('camps.markAttended')}
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </Modal>
  );
}

function CreateCamp({ user, onClose, onDone }) {
  const { t } = useI18n();
  const toast = useToast();
  const tomorrow = new Date(Date.now() + 7 * 86400000);
  tomorrow.setHours(9, 30, 0, 0);
  const local = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  const [form, setForm] = useState({
    title: '',
    organizer: '',
    venue: '',
    state: user.state || null,
    city: user.state ? user.city : '',
    starts_at: local(tomorrow),
    hours: 6,
    expected_donors: 50,
    description: '',
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.camps.create({
        ...form,
        user_id: user.id,
        starts_at: new Date(form.starts_at).toISOString(),
        hours: Number(form.hours),
        expected_donors: Number(form.expected_donors),
      });
      toast(t('camps.created'));
      onDone();
      onClose();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal open onClose={onClose} title={t('camps.host')}>
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="label" htmlFor="camp-title">
            {t('camps.titleLabel')}
          </label>
          <input id="camp-title" className="input" value={form.title} onChange={set('title')} minLength={3} required />
        </div>
        <div>
          <label className="label" htmlFor="camp-org">
            {t('camps.organizer')}
          </label>
          <input id="camp-org" className="input" value={form.organizer} onChange={set('organizer')} minLength={2} required />
        </div>
        <div>
          <label className="label" htmlFor="camp-venue">
            {t('camps.venue')}
          </label>
          <input id="camp-venue" className="input" value={form.venue} onChange={set('venue')} required />
        </div>
        <LocationPicker idPrefix="camp" value={form} onChange={(v) => setForm({ ...form, ...v })} />
        <div className="grid grid-cols-2 gap-3">
          <div className="col-span-2 sm:col-span-1">
            <label className="label" htmlFor="camp-date">
              {t('camps.date')}
            </label>
            <input id="camp-date" type="datetime-local" className="input" value={form.starts_at} onChange={set('starts_at')} required />
          </div>
          <div>
            <label className="label" htmlFor="camp-hours">
              {t('camps.hours')}
            </label>
            <input id="camp-hours" type="number" min={1} max={14} className="input" value={form.hours} onChange={set('hours')} />
          </div>
          <div>
            <label className="label" htmlFor="camp-expected">
              {t('camps.expectedLabel')}
            </label>
            <input id="camp-expected" type="number" min={5} max={2000} className="input" value={form.expected_donors} onChange={set('expected_donors')} />
          </div>
        </div>
        <div>
          <label className="label" htmlFor="camp-desc">
            {t('camps.description')}
          </label>
          <textarea id="camp-desc" rows={2} maxLength={400} className="input" value={form.description} onChange={set('description')} />
        </div>
        <ErrorBox error={error} />
        <button className="btn-primary w-full" disabled={busy}>
          {busy ? <Spinner /> : <Tent className="h-4 w-4" />} {t('camps.create')}
        </button>
      </form>
    </Modal>
  );
}
