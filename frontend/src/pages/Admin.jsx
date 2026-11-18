import { useState } from 'react';
import { Activity, BadgeCheck, CheckCircle2, Droplet, Gift, Hospital, Send, Shield, Siren, Timer, Users, XCircle } from 'lucide-react';
import { api } from '../lib/api';
import { usePoll } from '../lib/usePoll';
import { URGENCY, cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { useToast } from '../components/Toast';
import { useSession } from '../lib/session';
import { AdminSignIn } from '../components/SignInByCode';
import { BadgeChip, BloodTag, ErrorBox, Loading, PageHeader, StatCard } from '../components/ui';

const TABS = [
  ['overview', Activity],
  ['requests', Siren],
  ['users', Users],
  ['vouchers', Gift],
];

export default function Admin() {
  const { t } = useI18n();
  const { user, ready } = useSession();
  const [tab, setTab] = useState('overview');
  if (!ready) return <Loading />;
  if (!user?.is_admin)
    return (
      <div>
        <PageHeader icon={Shield} title={t('admin.title')} subtitle={t('admin.subtitle')} />
        <AdminSignIn />
      </div>
    );
  return (
    <div>
      <PageHeader icon={Shield} title={t('admin.title')} subtitle={t('admin.subtitle')}>
        <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400">🔒 {user.name}</span>
      </PageHeader>
      <div className="mb-6 flex flex-wrap gap-1 rounded-xl bg-slate-900 p-1" role="tablist">
        {TABS.map(([key, Icon]) => (
          <button
            key={key}
            role="tab"
            aria-selected={tab === key}
            onClick={() => setTab(key)}
            className={cx(
              'flex min-h-10 items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition',
              tab === key ? 'bg-red-600 text-white' : 'text-slate-300 hover:bg-slate-800',
            )}
          >
            <Icon className="h-4 w-4" /> {t(`admin.tabs.${key}`)}
          </button>
        ))}
      </div>
      {tab === 'overview' && <Overview />}
      {tab === 'requests' && <Requests />}
      {tab === 'users' && <UsersTab />}
      {tab === 'vouchers' && <Vouchers />}
    </div>
  );
}

function Overview() {
  const { t, num, ago, reason } = useI18n();
  const { data, error, loading } = usePoll(() => api.admin.stats(), 5000);
  if (loading && !data) return <Loading />;
  if (!data) return <ErrorBox error={error} />;
  const s = data.totals;
  const maxGroup = Math.max(1, ...data.demand_by_blood_group.map((d) => d.count), ...data.supply_by_blood_group.map((d) => d.count));
  const maxCity = Math.max(1, ...data.demand_by_city.map((c) => c.count));

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Users} label={t('admin.donors')} value={num(s.donors)} hint={t('admin.donorsHint', { available: num(s.available_donors), telegram: num(s.telegram_linked) })} />
        <StatCard icon={Siren} label={t('admin.active')} value={s.active_requests} hint={t('admin.fulfilledHint', { n: num(s.fulfilled_requests) })} accent="text-orange-400" />
        <StatCard
          icon={Timer}
          label={t('admin.response')}
          value={data.avg_response_minutes != null ? t('home.minutes', { n: num(data.avg_response_minutes) }) : '—'}
          accent="text-emerald-400"
        />
        <StatCard icon={Gift} label={t('admin.vouchersIssued')} value={num(s.vouchers_issued)} hint={t('admin.circulation', { n: num(s.points_in_circulation) })} accent="text-fuchsia-300" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div className="card p-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <h2 className="font-bold">{t('admin.demandSupply')}</h2>
            <div className="flex gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm bg-red-500" /> {t('admin.requests')}
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm bg-sky-500" /> {t('admin.availableDonors')}
              </span>
            </div>
          </div>
          <div className="space-y-3">
            {data.demand_by_blood_group.map((d, i) => {
              const sup = data.supply_by_blood_group[i];
              const shortage = d.count > sup.count;
              return (
                <div key={d.blood_group} className="grid grid-cols-[3rem_1fr_auto] items-center gap-3">
                  <BloodTag group={d.blood_group} size="sm" />
                  <div className="space-y-1">
                    <Bar value={d.count} max={maxGroup} color="bg-red-500" />
                    <Bar value={sup.count} max={maxGroup} color="bg-sky-500" />
                  </div>
                  <span className={cx('w-20 text-right text-xs', shortage ? 'font-bold text-red-400' : 'text-slate-500')}>
                    {shortage ? t('admin.shortage') : t('admin.ok')}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card p-6">
            <h2 className="mb-4 font-bold">{t('admin.heatmap')}</h2>
            <div className="space-y-2.5">
              {data.demand_by_city.map((c) => (
                <div key={c.city} className="flex items-center gap-3 text-sm">
                  <span className="w-28 truncate text-slate-300">{c.city}</span>
                  <div className="h-6 flex-1 overflow-hidden rounded bg-slate-800">
                    <div
                      className="flex h-full items-center justify-end rounded px-2 text-xs font-bold text-white"
                      style={{ width: `${Math.max(12, (c.count / maxCity) * 100)}%`, background: `rgba(220,38,38,${0.45 + 0.55 * (c.count / maxCity)})` }}
                    >
                      {c.count}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="card p-6">
            <h2 className="mb-3 font-bold">{t('admin.recent')}</h2>
            <ul className="max-h-64 space-y-2 overflow-y-auto text-sm">
              {data.recent_activity.map((r, i) => (
                <li key={i} className="flex justify-between gap-3">
                  <span className="text-slate-300">
                    <b>{r.name}</b>: {reason(r.reason)}
                    <span className="block text-xs text-slate-500">{ago(r.created_at)}</span>
                  </span>
                  <span className={cx('shrink-0 font-bold', r.amount >= 0 ? 'text-emerald-400' : 'text-red-400')}>
                    {r.amount >= 0 ? '+' : ''}
                    {r.amount}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function Bar({ value, max, color }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-800">
        <div className={cx('h-full rounded-full', color)} style={{ width: `${(value / max) * 100}%` }} />
      </div>
      <span className="w-6 text-right text-xs tabular-nums text-slate-400">{value}</span>
    </div>
  );
}

function Th({ children }) {
  return <th className="whitespace-nowrap px-4 py-3 font-semibold">{children}</th>;
}

function Requests() {
  const { t, ago } = useI18n();
  const toast = useToast();
  const [status, setStatus] = useState('all');
  const { data, error, loading, reload } = usePoll(() => api.requests(status), 5000, status);

  const act = async (fn, msg) => {
    try {
      await fn();
      toast(msg);
      reload();
    } catch (e) {
      toast(e.message, 'error');
    }
  };

  return (
    <div className="card overflow-hidden">
      <div className="flex flex-wrap gap-2 border-b border-slate-800 p-4">
        {['all', 'Active', 'Fulfilled', 'Cancelled'].map((s) => (
          <button
            key={s}
            onClick={() => setStatus(s)}
            aria-pressed={status === s}
            className={cx('min-h-9 rounded-lg px-3 py-1 text-sm font-semibold', status === s ? 'bg-slate-700 text-slate-50' : 'text-slate-400 hover:text-slate-50')}
          >
            {s === 'all' ? t('common.all') : t(`status.${s}`)}
          </button>
        ))}
      </div>
      <ErrorBox error={error} />
      {loading && !data ? (
        <Loading rows={5} />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <Th>#</Th>
                {['group', 'hospitalCity', 'requester', 'units', 'urgency', 'status', 'alerted', 'actions'].map((h) => (
                  <Th key={h}>{t(`admin.cols.${h}`)}</Th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {data?.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30">
                  <td className="px-4 py-3 text-slate-500">{r.id}</td>
                  <td className="px-4 py-3">
                    <BloodTag group={r.blood_group} size="sm" />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5 font-medium">
                      {r.hospital}
                      {r.is_verified && <BadgeCheck className="h-4 w-4 text-sky-400" aria-label={t('common.verified')} />}
                    </div>
                    <div className="text-xs text-slate-500">
                      {r.city} · {ago(r.created_at)}
                    </div>
                  </td>
                  <td className="px-4 py-3">{r.requester_name}</td>
                  <td className="px-4 py-3 tabular-nums">
                    {r.units_fulfilled}/{r.units_needed}
                  </td>
                  <td className="px-4 py-3">
                    <span className={cx('whitespace-nowrap rounded px-2 py-0.5 text-xs font-bold', URGENCY[r.urgency]?.chip)}>{t(`urgency.${r.urgency}`)}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={cx('font-semibold', { Active: 'text-orange-300', Fulfilled: 'text-emerald-400', Cancelled: 'text-slate-500' }[r.status])}>
                      {t(`status.${r.status}`)}
                    </span>
                    {r.fulfilled_by && <div className="max-w-40 truncate text-xs text-slate-500">{t('admin.by', { name: r.fulfilled_by })}</div>}
                  </td>
                  <td className="px-4 py-3 text-slate-400">
                    <span className="flex items-center gap-1">
                      <Send className="h-3.5 w-3.5 text-sky-400" />
                      {r.notified_count}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1.5">
                      <IconBtn
                        title={r.is_verified ? t('admin.unverify') : t('admin.verifyRequest')}
                        onClick={() =>
                          act(() => api.admin.verifyRequest(r.id, !r.is_verified), r.is_verified ? t('admin.verificationRemoved') : t('admin.requestVerified', { id: r.id }))
                        }
                        className={r.is_verified ? 'text-sky-400' : ''}
                      >
                        <BadgeCheck className="h-4 w-4" />
                      </IconBtn>
                      {r.status === 'Active' ? (
                        <>
                          <IconBtn title={t('admin.markFulfilled')} onClick={() => act(() => api.admin.setStatus(r.id, 'Fulfilled'), t('admin.markedFulfilled', { id: r.id }))}>
                            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          </IconBtn>
                          <IconBtn title={t('admin.cancel')} onClick={() => act(() => api.admin.setStatus(r.id, 'Cancelled'), t('admin.cancelled', { id: r.id }))}>
                            <XCircle className="h-4 w-4 text-red-400" />
                          </IconBtn>
                        </>
                      ) : (
                        <IconBtn title={t('admin.reopen')} onClick={() => act(() => api.admin.setStatus(r.id, 'Active'), t('admin.reopened', { id: r.id }))}>
                          <Siren className="h-4 w-4 text-orange-300" />
                        </IconBtn>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!data?.length && <p className="py-10 text-center text-slate-500">{t('admin.noRequests')}</p>}
        </div>
      )}
    </div>
  );
}

function IconBtn({ children, className, title, ...rest }) {
  return (
    <button
      title={title}
      aria-label={title}
      className={cx('flex h-9 w-9 items-center justify-center rounded-lg border border-slate-700 text-slate-400 hover:border-slate-500 hover:bg-slate-800', className)}
      {...rest}
    >
      {children}
    </button>
  );
}

function UsersTab() {
  const { t, num } = useI18n();
  const toast = useToast();
  const [q, setQ] = useState('');
  const { data, error, loading, reload } = usePoll(() => api.admin.users(), 0);

  const toggle = async (u) => {
    try {
      await api.admin.verifyUser(u.id, !u.is_verified);
      toast(u.is_verified ? t('admin.userUnverified', { name: u.name }) : t('admin.userVerified', { name: u.name }));
      reload();
    } catch (e) {
      toast(e.message, 'error');
    }
  };

  const star = async (u) => {
    try {
      const res = await api.admin.favorite(u.id);
      toast(res.status === 'success' ? t('admin.favoriteGiven', { name: u.name }) : t('admin.favoriteAlready', { name: u.name }));
    } catch (e) {
      toast(e.message, 'error');
    }
  };

  const rows = (data || []).filter((u) => `${u.name} ${u.city} ${u.blood_group} ${u.referral_code}`.toLowerCase().includes(q.toLowerCase()));

  return (
    <div className="card overflow-hidden">
      <div className="border-b border-slate-800 p-4">
        <input className="input max-w-sm" placeholder={t('admin.search')} aria-label={t('admin.search')} value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <ErrorBox error={error} />
      {loading && !data ? (
        <Loading rows={6} />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                {['name', 'group', 'city', 'role', 'points', 'donations', 'telegram', 'code', 'verified', 'recognise'].map((h) => (
                  <Th key={h}>{t(`admin.cols.${h}`)}</Th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {rows.map((u) => (
                <tr key={u.id} className="hover:bg-slate-800/30">
                  <td className="px-4 py-3">
                    <div className="font-medium">{u.name}</div>
                    {u.phone && <div className="text-xs text-slate-500">{u.phone}</div>}
                  </td>
                  <td className="px-4 py-3">
                    <BloodTag group={u.blood_group} size="sm" />
                  </td>
                  <td className="px-4 py-3">{u.city}</td>
                  <td className="px-4 py-3">
                    {u.role === 'hospital' ? (
                      <span className="flex items-center gap-1 text-sky-300">
                        <Hospital className="h-4 w-4" /> {t('common.hospital')}
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-slate-300">
                        <Droplet className="h-4 w-4 text-red-400" /> {t('common.donor')}
                      </span>
                    )}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3">
                    <span className="font-bold tabular-nums">{num(u.points)}</span> <BadgeChip badge={u.badge} />
                  </td>
                  <td className="px-4 py-3 tabular-nums">{u.total_donations}</td>
                  <td className="px-4 py-3">{u.telegram_linked ? <Send className="h-4 w-4 text-sky-400" aria-label="Telegram" /> : <span className="text-slate-600">—</span>}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">{u.referral_code}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggle(u)}
                      className={cx(
                        'flex min-h-9 items-center gap-1 whitespace-nowrap rounded-lg border px-2.5 py-1 text-xs font-semibold',
                        u.is_verified ? 'border-sky-500/50 bg-sky-500/10 text-sky-300' : 'border-slate-700 text-slate-400 hover:border-slate-500',
                      )}
                    >
                      <BadgeCheck className="h-3.5 w-3.5" /> {u.is_verified ? t('common.verified') : t('admin.verify')}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    {u.role === 'donor' && (
                      <button
                        onClick={() => star(u)}
                        title={t('admin.favoriteTitle')}
                        className="min-h-9 whitespace-nowrap rounded-lg border border-slate-700 px-2.5 py-1 text-xs font-semibold text-amber-300 hover:border-amber-400/60"
                      >
                        {t('admin.favorite')}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Vouchers() {
  const { t, tOr, ago } = useI18n();
  const { data, error, loading } = usePoll(() => api.admin.vouchers(), 5000);
  if (loading && !data) return <Loading rows={5} />;
  return (
    <div className="card overflow-hidden">
      <ErrorBox error={error} />
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              {['user', 'reward', 'cost', 'code', 'status', 'issued'].map((h) => (
                <Th key={h}>{t(`admin.cols.${h}`)}</Th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {data?.map((v) => (
              <tr key={v.id}>
                <td className="px-4 py-3 font-medium">{v.user}</td>
                <td className="px-4 py-3">{v.reward_name}</td>
                <td className="whitespace-nowrap px-4 py-3 tabular-nums">{v.points_cost ? `${v.points_cost} BLP` : t('admin.referralBonus')}</td>
                <td className="px-4 py-3 font-mono text-red-300">{v.voucher_code}</td>
                <td className="px-4 py-3 text-emerald-400">{tOr(`admin.voucherStatus.${v.status}`, v.status)}</td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-400">{ago(v.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!data?.length && <p className="py-10 text-center text-slate-500">{t('admin.noVouchers')}</p>}
      </div>
    </div>
  );
}
