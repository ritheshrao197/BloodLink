import { useState } from 'react';
import { Activity, Award, ChevronRight, Droplet, Gift, HeartHandshake, Hospital, Radio, Send, Siren, Sparkles, Trophy, Users, Zap } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { BADGES, BLOOD_GROUPS, canDonate, cx } from '../lib/utils';
import { useI18n } from '../i18n';
import RequestCard from '../components/RequestCard';
import { kmBetween } from '../components/Nearby';
import DonateModal from '../components/DonateModal';
import { Showcase } from '../components/Achievements';
import { BadgeChip, BloodTag, Empty, ErrorBox, Loading } from '../components/ui';

export default function Home() {
  const { user, config } = useSession();
  const { t, num, ago } = useI18n();
  const [filter, setFilter] = useState('All');
  const [respondTo, setRespondTo] = useState(null);
  const [nearest, setNearest] = useState(false);
  const me = user?.location || null;
  const feed = usePoll(() => api.requests('Active'), 4000);
  const stats = usePoll(() => api.stats(), 15000);
  const board = usePoll(() => api.leaderboard(5), 15000);
  const catalog = usePoll(() => api.achievements(), 0);
  const activity = usePoll(() => api.recentActivity(), 10000);

  const requests = (feed.data || []).filter((r) =>
    filter === 'All' ? true : filter === 'Mine' ? user && canDonate(user.blood_group, r.blood_group) : r.blood_group === filter,
  );
  if (me && nearest) requests.sort((a, b) => (kmBetween(me, a) ?? 1e9) - (kmBetween(me, b) ?? 1e9));
  const s = stats.data?.totals;
  const bot = config?.bot_username || 'BloodLinkBot';
  const spotlight = (feed.data || []).find((r) => r.urgency === 'Critical') || feed.data?.[0];
  const bold = (n) => <b className="text-slate-200">{num(n)}</b>;

  return (
    <div className="space-y-14">
      {/* ---------------- hero ---------------- */}
      <section className="relative isolate pb-4 pt-6 sm:pt-10">
        <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute left-0 top-0 h-80 w-80 rounded-full bg-blood-500/15 blur-[100px] dark:bg-blood-600/25" />
          <div className="absolute right-0 top-10 h-72 w-72 rounded-full bg-blood-200/60 blur-[100px] dark:bg-rose-500/10" />
          <div className="absolute bottom-0 left-1/3 h-56 w-56 rounded-full bg-slate-400/10 blur-[100px]" />
        </div>

        <div className="grid items-center gap-12 lg:grid-cols-[1.15fr_1fr]">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-blood-200 bg-white/70 px-3 py-1 backdrop-blur dark:border-blood-500/30 dark:bg-blood-500/10">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blood-500 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-blood-500" />
              </span>
              <span className="overline">{t('home.live')}</span>
            </span>
            <h1 className="hero-title mt-5">{t('home.heroTitle')}</h1>
            <p className="mt-5 max-w-xl text-lg leading-relaxed text-slate-400">{t('home.heroText')}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/sos" className="btn-sos px-7 py-3.5 text-base">
                <Droplet className="h-5 w-5 fill-white" /> {t('nav.sosLong')}
              </Link>
              {user ? (
                <a href={`https://t.me/${bot}`} target="_blank" rel="noreferrer" className="btn-secondary px-6 py-3.5 text-base">
                  <Send className="h-5 w-5 text-sky-500" /> {t('home.openBot', { bot })}
                </a>
              ) : (
                <Link to="/register" className="btn-secondary px-6 py-3.5 text-base">
                  <HeartHandshake className="h-5 w-5" /> {t('home.join')}
                </Link>
              )}
            </div>
            <p className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-400">
              <span className="flex items-center gap-1.5">
                <Zap className="h-4 w-4 text-yellow-500" aria-hidden />
                <Fill text={t('home.donationsMatched', { n: '\u0000' })} value={bold(s?.donations)} />
              </span>
              <span aria-hidden>•</span>
              <span className="flex items-center gap-1.5">
                <Hospital className="h-4 w-4 text-sky-500" aria-hidden />
                <Fill text={t('home.partnerHospitals', { n: '\u0000' })} value={bold(s?.hospitals)} />
              </span>
            </p>
          </div>

          {/* live spotlight */}
          <div className="relative mx-auto w-full max-w-md">
            <div aria-hidden className="absolute -right-2 -top-16 z-10 animate-float text-7xl leading-none drop-shadow-[0_16px_24px_rgba(220,38,38,0.4)] sm:-right-8">
              🩸
            </div>
            <div className="card-glass relative p-6 shadow-2xl shadow-blood-900/10">
              <p className="overline flex items-center gap-2">
                <Radio className="h-3.5 w-3.5" /> {t('home.happening')}
              </p>
              {spotlight ? (
                <>
                  <div className="mt-4 flex items-center gap-4">
                    <BloodTag group={spotlight.blood_group} size="lg" />
                    <div className="min-w-0">
                      <p className="text-xl font-extrabold">{t('home.needed', { group: spotlight.blood_group })}</p>
                      <p className="truncate text-sm text-slate-400">{spotlight.hospital}</p>
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap items-center justify-between gap-x-3 text-sm">
                    <span className="text-slate-400">
                      {spotlight.city} · {ago(spotlight.created_at)}
                    </span>
                    <span className="font-semibold text-blood-600 dark:text-blood-400">{t('home.alerted', { n: num(spotlight.notified_count) })}</span>
                  </div>
                  <div className="progress-bar mt-3">
                    <div className="progress-fill" style={{ width: `${Math.round((100 * spotlight.units_fulfilled) / spotlight.units_needed)}%` }} />
                  </div>
                  <button onClick={() => setRespondTo(spotlight)} className="btn-primary mt-5 w-full">
                    🩸 {t('common.iCanDonate')}
                  </button>
                </>
              ) : (
                <div className="skeleton mt-4 h-32" />
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ---------------- live stats bar ---------------- */}
      <section className="card grid grid-cols-1 divide-y divide-slate-800 overflow-hidden p-0 sm:grid-cols-2 sm:divide-y-0 lg:grid-cols-4 lg:divide-x" aria-label={t('home.stats')}>
        {[
          [Users, num(s?.donors), t('home.statDonors'), s && t('home.statAvailable', { n: num(s.available_donors) }), 'text-blood-500'],
          [Hospital, num(s?.hospitals), t('home.statHospitals'), s && t('home.statFulfilled', { n: num(s.fulfilled_requests) }), 'text-sky-500'],
          [
            Zap,
            stats.data?.avg_response_minutes != null ? t('home.minutes', { n: num(stats.data.avg_response_minutes) }) : '—',
            t('home.statResponse'),
            t('home.statResponseHint'),
            'text-yellow-500',
          ],
          [Award, num(catalog.data?.achievements?.length), t('home.statAchievements'), t('home.statAchievementsHint'), 'text-violet-500'],
        ].map(([Icon, value, label, hint, color]) => (
          <div key={label} className="flex items-center gap-4 p-5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-slate-900">
              <Icon className={cx('h-5 w-5', color)} aria-hidden />
            </span>
            <div className="min-w-0">
              <div className="text-2xl font-extrabold tabular-nums tracking-tight">{value}</div>
              <div className="text-xs font-semibold text-slate-400">{label}</div>
              {hint && <div className="truncate text-[11px] text-slate-500">{hint}</div>}
            </div>
          </div>
        ))}
      </section>

      {/* ---------------- feed + dashboard ---------------- */}
      <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
        <section aria-labelledby="feed-title">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <h2 id="feed-title" className="section-title flex items-center gap-3">
              <Activity className="h-7 w-7 text-blood-600 dark:text-blood-500" aria-hidden /> {t('home.feedTitle')}
              <span className="rounded-full bg-blood-600 px-2.5 py-0.5 text-sm text-white">{feed.data?.length ?? 0}</span>
            </h2>
          </div>
          <div className="mb-5 -mx-4 flex gap-1.5 overflow-x-auto px-4 pb-1 [scrollbar-width:none] sm:mx-0 sm:flex-wrap sm:px-0" role="group" aria-label={t('home.filter')}>
            {['All', ...(user ? ['Mine'] : []), ...BLOOD_GROUPS].map((g) => (
              <button
                key={g}
                onClick={() => setFilter(g)}
                aria-pressed={filter === g}
                className={cx(
                  'min-h-9 shrink-0 rounded-full px-3.5 py-1 text-sm font-semibold transition',
                  filter === g ? 'bg-blood-600 text-white shadow-md shadow-blood-600/30' : 'bg-slate-800 text-slate-300 hover:bg-slate-700',
                )}
              >
                {g === 'Mine' ? t('home.mine') : g === 'All' ? t('common.all') : g}
              </button>
            ))}
            {me && (
              <button
                onClick={() => setNearest(!nearest)}
                aria-pressed={nearest}
                className={cx('min-h-9 shrink-0 rounded-full px-3.5 py-1 text-sm font-semibold transition', nearest ? 'bg-sky-600 text-white' : 'bg-slate-800 text-sky-400 hover:bg-slate-700')}
              >
                📍 {t('geo.nearest')}
              </button>
            )}
          </div>
          <ErrorBox error={feed.error} />
          {feed.loading && !feed.data ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="skeleton h-64" />
              ))}
            </div>
          ) : requests.length === 0 ? (
            <Empty icon={HeartHandshake} title={t('home.emptyTitle')}>
              {filter === 'All' ? t('home.emptyAll') : t('home.emptyFilter')}
            </Empty>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {requests.map((r) => (
                <RequestCard key={r.id} request={r} onRespond={setRespondTo} me={me} />
              ))}
            </div>
          )}
        </section>

        <aside className="space-y-4 lg:pt-14">
          {user ? <ProfileWidget user={user} /> : <JoinWidget />}
          <LiveActivity data={activity.data} />
          <TopHeroes data={board.data} loading={board.loading} me={user?.id} />
        </aside>
      </div>

      {/* ---------------- how it works ---------------- */}
      <section aria-labelledby="how-title">
        <p className="overline">{t('home.howOverline')}</p>
        <h2 id="how-title" className="section-title mt-1">
          {t('home.howTitle')}
        </h2>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {[
            [t('home.how1'), t('home.how1Text'), Siren],
            [t('home.how2'), t('home.how2Text'), Radio],
            [t('home.how3'), t('home.how3Text'), HeartHandshake],
          ].map(([title, text, Icon], i) => (
            <div key={i} className="card card-hover p-6">
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blood-600/10 dark:bg-blood-500/15">
                  <Icon className="h-5 w-5 text-blood-600 dark:text-blood-400" aria-hidden />
                </span>
                <span className="font-mono text-sm font-semibold text-slate-500">0{i + 1}</span>
              </div>
              <h3 className="mt-4 text-lg font-bold">{title}</h3>
              <p className="mt-1 text-sm leading-relaxed text-slate-400">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <DonateModal
        request={respondTo}
        onClose={() => setRespondTo(null)}
        onDone={() => {
          feed.reload();
          stats.reload();
          board.reload();
        }}
      />
    </div>
  );
}

/** Render a translated sentence with a styled value where its {n} placeholder was (word order differs by language). */
function Fill({ text, value }) {
  const [before, after] = text.split('\u0000');
  return (
    <span>
      {before}
      {value}
      {after}
    </span>
  );
}

function ProfileWidget({ user }) {
  const { t, num } = useI18n();
  const info = user.badge_info;
  const next = info.next;
  const pct = next ? Math.min(100, Math.round(((user.points - info.min_points) / (next.min_points - info.min_points)) * 100)) : 100;
  return (
    <div className="card overflow-hidden">
      <div className="p-5">
        <p className="overline">{t('home.yourProfile')}</p>
        <div className="mt-3 flex items-center gap-3">
          <BloodTag group={user.blood_group} size="lg" />
          <div className="min-w-0">
            <p className="truncate text-lg font-bold">{user.name}</p>
            <BadgeChip badge={user.badge} />
          </div>
        </div>
        <div className="mt-4 flex flex-wrap items-baseline justify-between gap-x-2">
          <span className="text-3xl font-extrabold tabular-nums">
            {num(user.points)} <span className="text-sm font-semibold text-slate-400">BLP</span>
          </span>
          <span className="text-xs text-slate-400">
            {next ? t('home.toNext', { n: num(next.min_points - user.points), icon: next.icon, name: t(`badge.${next.name}`) }) : t('home.maxLevel')}
          </span>
        </div>
        <div className="progress-bar mt-2">
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>
      <Link to="/achievements" className="flex items-center justify-between gap-2 border-t border-slate-800 px-5 py-3.5 text-sm transition hover:bg-slate-900">
        <span className="flex items-center gap-2 font-semibold">
          <Sparkles className="h-4 w-4 text-violet-500" aria-hidden /> {t('nav.achievements')}
        </span>
        <span className="flex items-center gap-1">
          {user.achievements?.count ? <Showcase data={user.achievements} size="text-base" /> : <span className="text-slate-500">{t('home.startCollection')}</span>}
          <ChevronRight className="h-4 w-4 text-slate-500" aria-hidden />
        </span>
      </Link>
      <Link to="/rewards" className="flex items-center justify-between gap-2 border-t border-slate-800 px-5 py-3.5 text-sm transition hover:bg-slate-900">
        <span className="flex items-center gap-2 font-semibold">
          <Gift className="h-4 w-4 text-pink-500" aria-hidden /> {t('home.redeem')}
        </span>
        <span className="flex items-center gap-1 text-slate-400">
          {t('home.fromBlp')} <ChevronRight className="h-4 w-4 text-slate-500" aria-hidden />
        </span>
      </Link>
    </div>
  );
}

function LiveActivity({ data }) {
  const { t, ago } = useI18n();
  if (!data?.length) return null;
  return (
    <div className="card p-5">
      <p className="overline flex items-center gap-2">
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-500 opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
        </span>
        {t('home.activityTitle')}
      </p>
      <ul className="mt-3 space-y-2.5">
        {data.slice(0, 5).map((a, i) => (
          <li key={`${a.created_at}-${i}`} className="flex gap-2.5 text-sm">
            <BloodTag group={a.blood_group} size="sm" />
            <span className="min-w-0">
              <span className="block truncate text-slate-300">{t('home.activityLine', { name: a.name, hospital: a.hospital })}</span>
              <span className="text-xs text-slate-500">
                {a.city} · {ago(a.created_at)}
              </span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function JoinWidget() {
  const { t } = useI18n();
  return (
    <div className="card overflow-hidden">
      <div className="bg-gradient-to-br from-blood-600 to-blood-800 p-5 text-white">
        <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-blood-100">{t('home.heroOverline')}</p>
        <p className="mt-2 text-xl font-extrabold leading-snug">{t('home.heroLine')}</p>
        <p className="mt-1 text-sm text-blood-100">{t('home.heroJoin')}</p>
      </div>
      <div className="space-y-2 p-5">
        <Link to="/register" className="btn-primary w-full">
          <HeartHandshake className="h-4 w-4" /> {t('home.registerDonor')}
        </Link>
        <Link to="/profile" className="btn-ghost w-full">
          {t('home.haveCode')}
        </Link>
      </div>
    </div>
  );
}

function TopHeroes({ data, loading, me }) {
  const { t, num } = useI18n();
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between gap-2">
        <p className="overline flex items-center gap-1.5">
          <Trophy className="h-3.5 w-3.5" /> {t('home.topHeroes')}
        </p>
        <Link to="/leaderboard" className="text-xs font-semibold text-slate-400 hover:text-blood-500">
          {t('common.viewAll')}
        </Link>
      </div>
      {loading && !data ? (
        <Loading rows={3} />
      ) : (
        <ol className="mt-3 space-y-1">
          {(data || []).map((u, i) => (
            <li key={u.id} className={cx('flex items-center gap-3 rounded-lg px-2 py-2', me === u.id && 'bg-blood-600/10')}>
              <span className={cx('w-6 text-sm font-extrabold', i < 3 ? 'text-amber-500' : 'text-slate-500')}>#{i + 1}</span>
              <span className="text-lg" aria-hidden>
                {BADGES[u.badge]?.icon}
              </span>
              <span className="min-w-0 flex-1 truncate text-sm font-semibold">{u.name}</span>
              <BloodTag group={u.blood_group} size="sm" />
              <span className="w-16 text-right text-sm font-bold tabular-nums text-blood-600 dark:text-blood-400">{num(u.points)}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
