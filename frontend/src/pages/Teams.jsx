import { useState } from 'react';
import { Building2, Copy, GraduationCap, Heart, Plus, Trophy, Users, UsersRound } from 'lucide-react';
import { api } from '../lib/api';
import { Link, useRouter } from '../lib/router';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { BADGES, cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { useToast } from '../components/Toast';
import { BloodTag, Empty, ErrorBox, Loading, PageHeader, Spinner } from '../components/ui';

const KINDS = ['college', 'company', 'community', 'group'];
const KIND_ICON = { college: GraduationCap, company: Building2, community: Heart, group: UsersRound };

export default function Teams() {
  const { search } = useRouter();
  const id = Number(new URLSearchParams(search).get('id')) || null;
  return id ? <TeamDetail id={id} /> : <TeamList />;
}

function TeamList() {
  const { user } = useSession();
  const { t, num } = useI18n();
  const [kind, setKind] = useState('');
  const list = usePoll(() => api.teams.list(kind, user?.id), 15000, `${kind}-${user?.id}`);
  const mine = (list.data || []).filter((x) => x.is_mine);

  return (
    <div className="space-y-8">
      <PageHeader icon={Users} title={t('teams.title')} subtitle={t('teams.subtitle')} />

      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        <section>
          <div className="mb-4 -mx-4 flex gap-1.5 overflow-x-auto px-4 pb-1 [scrollbar-width:none] sm:mx-0 sm:flex-wrap sm:px-0" role="group" aria-label={t('teams.kindLabel')}>
            {['', ...KINDS].map((k) => (
              <button
                key={k || 'all'}
                onClick={() => setKind(k)}
                aria-pressed={kind === k}
                className={cx('min-h-9 shrink-0 rounded-full px-3.5 py-1 text-sm font-semibold transition', kind === k ? 'bg-blood-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700')}
              >
                {k ? t(`teams.kind.${k}`) : t('common.all')}
              </button>
            ))}
          </div>
          <ErrorBox error={list.error} />
          {list.loading && !list.data ? (
            <Loading rows={6} />
          ) : !list.data?.length ? (
            <Empty icon={Users} title={t('teams.none')} />
          ) : (
            <div className="card divide-y divide-slate-800 overflow-hidden">
              {list.data.map((team, i) => {
                const Icon = KIND_ICON[team.kind] || UsersRound;
                return (
                  <Link
                    key={team.id}
                    to={`/teams?id=${team.id}`}
                    className={cx('flex items-center gap-3 px-4 py-3.5 transition hover:bg-slate-800/40 sm:gap-4 sm:px-6', team.is_mine && 'bg-amber-500/10')}
                  >
                    <span className={cx('w-9 text-lg font-extrabold', i < 3 ? 'text-amber-500' : 'text-slate-500')}>#{team.rank}</span>
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-800">
                      <Icon className="h-5 w-5 text-slate-300" aria-hidden />
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="truncate font-bold">{team.name}</span>
                        {team.is_mine && <span className="shrink-0 rounded bg-amber-500 px-1.5 text-[10px] font-bold text-white">{t('teams.you')}</span>}
                      </div>
                      <div className="text-xs text-slate-400">
                        {t(`teams.kind.${team.kind}`)}
                        {team.city && ` · ${team.city}`} · {t('teams.members', { n: team.members })}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-extrabold tabular-nums text-blood-600 dark:text-blood-400">{num(team.points)} BLP</div>
                      <div className="text-xs text-slate-400">{t('teams.donations', { n: team.donations })}</div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </section>

        <aside className="space-y-4">
          {user ? (
            <>
              {mine.length > 0 && (
                <div className="card p-5">
                  <p className="overline">{t('teams.mine')}</p>
                  <ul className="mt-2 space-y-1">
                    {mine.map((m) => (
                      <li key={m.id}>
                        <Link to={`/teams?id=${m.id}`} className="flex items-center justify-between rounded-lg px-2 py-2 text-sm hover:bg-slate-800/50">
                          <span className="truncate font-semibold">{m.name}</span>
                          <span className="text-slate-400">#{m.rank}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <JoinTeam user={user} onDone={list.reload} />
              <CreateTeam user={user} onDone={list.reload} />
            </>
          ) : (
            <div className="card p-5 text-sm text-slate-300">
              {t('teams.signIn')}{' '}
              <Link to="/profile" className="font-semibold text-blood-500 hover:underline">
                {t('common.signIn')}
              </Link>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

function JoinTeam({ user, onDone }) {
  const { t } = useI18n();
  const toast = useToast();
  const { navigate } = useRouter();
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const team = await api.teams.join(user.id, code.trim());
      toast(t('teams.joinedToast', { name: team.name }));
      onDone();
      navigate(`/teams?id=${team.id}`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setBusy(false);
    }
  };
  return (
    <form onSubmit={submit} className="card space-y-3 p-5">
      <p className="font-bold">{t('teams.join')}</p>
      <div className="flex gap-2">
        <input className="input font-mono uppercase" placeholder="TEAM-XXXXX" aria-label={t('teams.invite')} value={code} onChange={(e) => setCode(e.target.value)} required />
        <button className="btn-ghost shrink-0" disabled={busy}>
          {busy ? <Spinner className="h-4 w-4" /> : null} {t('teams.joinBtn')}
        </button>
      </div>
    </form>
  );
}

function CreateTeam({ user, onDone }) {
  const { t } = useI18n();
  const toast = useToast();
  const { navigate } = useRouter();
  const [form, setForm] = useState({ name: '', kind: 'college' });
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const team = await api.teams.create({ user_id: user.id, ...form });
      toast(t('teams.created'));
      onDone();
      navigate(`/teams?id=${team.id}`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setBusy(false);
    }
  };
  return (
    <form onSubmit={submit} className="card space-y-3 p-5">
      <p className="font-bold">{t('teams.create')}</p>
      <div>
        <label className="label" htmlFor="team-name">
          {t('teams.name')}
        </label>
        <input id="team-name" className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} minLength={2} maxLength={60} required />
      </div>
      <div>
        <label className="label" htmlFor="team-kind">
          {t('teams.kindLabel')}
        </label>
        <select id="team-kind" className="input" value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}>
          {KINDS.map((k) => (
            <option key={k} value={k}>
              {t(`teams.kind.${k}`)}
            </option>
          ))}
        </select>
      </div>
      <button className="btn-primary w-full" disabled={busy}>
        {busy ? <Spinner /> : <Plus className="h-4 w-4" />} {t('teams.createBtn')}
      </button>
    </form>
  );
}

function TeamDetail({ id }) {
  const { user } = useSession();
  const { t, num, ago } = useI18n();
  const toast = useToast();
  const { navigate } = useRouter();
  const { data: team, error, loading, reload } = usePoll(() => api.teams.get(id, user?.id), 15000, `${id}-${user?.id}`);
  if (loading && !team) return <Loading />;
  if (!team) return <ErrorBox error={error} />;
  const Icon = KIND_ICON[team.kind] || UsersRound;

  const leave = async () => {
    await api.teams.leave(team.id, user.id);
    navigate('/teams');
  };
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(team.invite_code);
      toast(t('teams.copied'));
    } catch {
      /* clipboard blocked */
    }
  };

  return (
    <div className="space-y-6">
      <Link to="/teams" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-50">
        {t('teams.back')}
      </Link>
      <div className="card flex flex-wrap items-center gap-5 p-6 sm:p-8">
        <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-500 to-amber-700 text-white shadow-lg shadow-amber-900/30">
          <Icon className="h-8 w-8" aria-hidden />
        </span>
        <div className="min-w-0 flex-1">
          <h1 className="text-3xl font-extrabold">{team.name}</h1>
          <p className="text-slate-400">
            {t(`teams.kind.${team.kind}`)}
            {team.city && ` · ${team.city}, ${team.state}`}
          </p>
          <p className="mt-1 flex items-center gap-1.5 text-sm font-semibold text-amber-500">
            <Trophy className="h-4 w-4" /> {t('teams.rank', { rank: team.rank, total: team.teams_total })}
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3 text-center">
          {[
            [num(team.points), 'BLP'],
            [team.donations, t('profile.donations')],
            [team.members, t('teams.membersTitle')],
          ].map(([v, l]) => (
            <div key={l} className="rounded-xl bg-slate-800/60 px-4 py-2">
              <div className="text-xl font-extrabold tabular-nums">{v}</div>
              <div className="text-xs text-slate-400">{l}</div>
            </div>
          ))}
        </div>
      </div>

      <div className={cx('rounded-xl border p-4 text-sm', team.gap_to_next ? 'border-amber-500/40 bg-amber-950/20 text-amber-200' : 'border-emerald-500/40 bg-emerald-950/30 text-emerald-300')}>
        {team.gap_to_next ? t('teams.gap', { n: num(team.gap_to_next.points), name: team.gap_to_next.name }) : t('teams.leader')}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="card overflow-hidden">
          <h2 className="border-b border-slate-800 px-5 py-4 font-bold">{t('teams.membersTitle')}</h2>
          <ol className="divide-y divide-slate-800">
            {team.members_list.map((m, i) => (
              <li key={m.id} className={cx('flex items-center gap-3 px-5 py-3', user?.id === m.id && 'bg-blood-600/10')}>
                <span className={cx('w-7 text-sm font-extrabold', i < 3 ? 'text-amber-500' : 'text-slate-500')}>#{i + 1}</span>
                <span aria-hidden>{BADGES[m.badge]?.icon}</span>
                <div className="min-w-0 flex-1">
                  <div className="truncate font-semibold">
                    {m.name} {m.role === 'owner' && <span className="text-xs text-amber-500">★</span>}
                  </div>
                  <div className="text-xs text-slate-500">{t('teams.joined', { when: ago(m.joined_at) })}</div>
                </div>
                <BloodTag group={m.blood_group} size="sm" />
                <div className="w-20 text-right">
                  <div className="font-bold tabular-nums text-blood-600 dark:text-blood-400">{num(m.points)}</div>
                  <div className="text-[11px] text-slate-500">{t('teams.donations', { n: m.donations })}</div>
                </div>
              </li>
            ))}
          </ol>
        </div>
        <aside className="space-y-4">
          {team.invite_code ? (
            <div className="card space-y-3 p-5">
              <p className="font-bold">{t('teams.invite')}</p>
              <button onClick={copy} className="flex w-full items-center justify-between rounded-xl border-2 border-dashed border-amber-500/50 px-4 py-3 font-mono text-xl font-extrabold tracking-wider text-amber-500">
                {team.invite_code} <Copy className="h-4 w-4" />
              </button>
              <p className="text-xs text-slate-400">{t('teams.inviteHint')}</p>
              <button onClick={leave} className="text-xs font-semibold text-slate-500 hover:text-blood-500">
                {t('teams.leave')}
              </button>
            </div>
          ) : (
            user && (
              <div className="card p-5 text-sm text-slate-300">
                <JoinTeam user={user} onDone={reload} />
              </div>
            )
          )}
          <Link to="/camps" className="card card-hover block p-5 text-sm">
            <p className="font-bold">🏕️ {t('camps.title')}</p>
            <p className="mt-1 text-slate-400">{t('teams.campsHint')}</p>
          </Link>
        </aside>
      </div>
    </div>
  );
}
