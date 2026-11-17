import { useState } from 'react';
import { Activity, BadgeCheck, CheckCircle2, Droplet, Gift, Hospital, Send, Shield, Siren, Timer, Users, XCircle } from 'lucide-react';
import { api } from '../lib/api';
import { usePoll } from '../lib/usePoll';
import { URGENCY, cx, timeAgo } from '../lib/utils';
import { useToast } from '../components/Toast';
import { BadgeChip, BloodTag, ErrorBox, Loading, PageHeader, StatCard } from '../components/ui';

const TABS = [
  ['overview', 'Analytics', Activity],
  ['requests', 'Requests', Siren],
  ['users', 'Donors & Hospitals', Users],
  ['vouchers', 'Vouchers', Gift],
];

export default function Admin() {
  const [tab, setTab] = useState('overview');
  return (
    <div>
      <PageHeader icon={Shield} title="Admin Portal" subtitle="Verify hospitals and donors, track SOS requests, and watch demand in real time.">
        <span className="rounded-full border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-xs text-amber-300">Demo mode · no authentication</span>
      </PageHeader>
      <div className="mb-6 flex flex-wrap gap-1 rounded-xl bg-slate-900 p-1">
        {TABS.map(([key, label, Icon]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={cx(
              'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition',
              tab === key ? 'bg-red-600 text-white' : 'text-slate-300 hover:bg-slate-800',
            )}
          >
            <Icon className="h-4 w-4" /> {label}
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
  const { data, error, loading } = usePoll(() => api.admin.stats(), 5000);
  if (loading && !data) return <Loading />;
  if (!data) return <ErrorBox error={error} />;
  const t = data.totals;
  const maxGroup = Math.max(1, ...data.demand_by_blood_group.map((d) => d.count), ...data.supply_by_blood_group.map((d) => d.count));
  const maxCity = Math.max(1, ...data.demand_by_city.map((c) => c.count));

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Users} label="Donors" value={t.donors} hint={`${t.available_donors} available · ${t.telegram_linked} on Telegram`} />
        <StatCard icon={Siren} label="Active requests" value={t.active_requests} hint={`${t.fulfilled_requests} fulfilled`} accent="text-orange-400" />
        <StatCard icon={Timer} label="Avg. first response" value={data.avg_response_minutes != null ? `${data.avg_response_minutes} min` : '—'} accent="text-emerald-400" />
        <StatCard icon={Gift} label="Vouchers issued" value={t.vouchers_issued} hint={`${t.points_in_circulation} BLP in circulation`} accent="text-fuchsia-300" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div className="card p-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <h2 className="font-bold">Demand vs. available supply by blood group</h2>
            <div className="flex gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm bg-red-500" /> Requests
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm bg-sky-500" /> Available donors
              </span>
            </div>
          </div>
          <div className="space-y-3">
            {data.demand_by_blood_group.map((d, i) => {
              const s = data.supply_by_blood_group[i];
              const shortage = d.count > s.count;
              return (
                <div key={d.blood_group} className="grid grid-cols-[3rem_1fr_auto] items-center gap-3">
                  <BloodTag group={d.blood_group} size="sm" />
                  <div className="space-y-1">
                    <Bar value={d.count} max={maxGroup} color="bg-red-500" />
                    <Bar value={s.count} max={maxGroup} color="bg-sky-500" />
                  </div>
                  <span className={cx('w-16 text-right text-xs', shortage ? 'font-bold text-red-400' : 'text-slate-500')}>{shortage ? '⚠ shortage' : 'ok'}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card p-6">
            <h2 className="mb-4 font-bold">Demand heatmap by city</h2>
            <div className="space-y-2.5">
              {data.demand_by_city.map((c) => (
                <div key={c.city} className="flex items-center gap-3 text-sm">
                  <span className="w-28 truncate text-slate-300">{c.city}</span>
                  <div className="h-6 flex-1 overflow-hidden rounded bg-slate-800">
                    <div
                      className="flex h-full items-center justify-end rounded px-2 text-xs font-bold"
                      style={{ width: `${Math.max(12, (c.count / maxCity) * 100)}%`, background: `rgba(239,68,68,${0.3 + 0.7 * (c.count / maxCity)})` }}
                    >
                      {c.count}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="card p-6">
            <h2 className="mb-3 font-bold">Recent activity</h2>
            <ul className="max-h-64 space-y-2 overflow-y-auto text-sm">
              {data.recent_activity.map((r, i) => (
                <li key={i} className="flex justify-between gap-3">
                  <span className="text-slate-300">
                    <b>{r.name}</b>: {r.reason}
                    <span className="block text-xs text-slate-500">{timeAgo(r.created_at)}</span>
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

function Requests() {
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
          <button key={s} onClick={() => setStatus(s)} className={cx('rounded-lg px-3 py-1 text-sm font-semibold', status === s ? 'bg-slate-700 text-slate-50' : 'text-slate-400 hover:text-slate-50')}>
            {s === 'all' ? 'All' : s}
          </button>
        ))}
      </div>
      <ErrorBox error={error} />
      {loading && !data ? (
        <Loading />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                {['#', 'Group', 'Hospital / City', 'Requester', 'Units', 'Urgency', 'Status', 'Alerted', 'Actions'].map((h) => (
                  <th key={h} className="whitespace-nowrap px-4 py-3 font-semibold">
                    {h}
                  </th>
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
                      {r.is_verified && <BadgeCheck className="h-4 w-4 text-sky-400" />}
                    </div>
                    <div className="text-xs text-slate-500">
                      {r.city} · {timeAgo(r.created_at)}
                    </div>
                  </td>
                  <td className="px-4 py-3">{r.requester_name}</td>
                  <td className="px-4 py-3 tabular-nums">
                    {r.units_fulfilled}/{r.units_needed}
                  </td>
                  <td className="px-4 py-3">
                    <span className={cx('rounded px-2 py-0.5 text-xs font-bold', URGENCY[r.urgency]?.chip)}>{r.urgency}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={cx('font-semibold', { Active: 'text-orange-300', Fulfilled: 'text-emerald-400', Cancelled: 'text-slate-500' }[r.status])}>{r.status}</span>
                    {r.fulfilled_by && <div className="max-w-40 truncate text-xs text-slate-500">by {r.fulfilled_by}</div>}
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
                        title={r.is_verified ? 'Unverify' : 'Verify hospital request'}
                        onClick={() => act(() => api.admin.verifyRequest(r.id, !r.is_verified), r.is_verified ? 'Verification removed' : `Request #${r.id} verified`)}
                        className={r.is_verified ? 'text-sky-400' : ''}
                      >
                        <BadgeCheck className="h-4 w-4" />
                      </IconBtn>
                      {r.status === 'Active' ? (
                        <>
                          <IconBtn title="Mark fulfilled" onClick={() => act(() => api.admin.setStatus(r.id, 'Fulfilled'), `#${r.id} marked fulfilled`)}>
                            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          </IconBtn>
                          <IconBtn title="Cancel" onClick={() => act(() => api.admin.setStatus(r.id, 'Cancelled'), `#${r.id} cancelled`)}>
                            <XCircle className="h-4 w-4 text-red-400" />
                          </IconBtn>
                        </>
                      ) : (
                        <IconBtn title="Re-open" onClick={() => act(() => api.admin.setStatus(r.id, 'Active'), `#${r.id} re-opened`)}>
                          <Siren className="h-4 w-4 text-orange-300" />
                        </IconBtn>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!data?.length && <p className="py-10 text-center text-slate-500">No requests.</p>}
        </div>
      )}
    </div>
  );
}

function IconBtn({ children, className, ...rest }) {
  return (
    <button className={cx('rounded-lg border border-slate-700 p-1.5 text-slate-400 hover:border-slate-500 hover:bg-slate-800', className)} {...rest}>
      {children}
    </button>
  );
}

function UsersTab() {
  const toast = useToast();
  const [q, setQ] = useState('');
  const { data, error, loading, reload } = usePoll(() => api.admin.users(), 0);

  const toggle = async (u) => {
    try {
      await api.admin.verifyUser(u.id, !u.is_verified);
      toast(`${u.name} ${u.is_verified ? 'unverified' : 'verified'}`);
      reload();
    } catch (e) {
      toast(e.message, 'error');
    }
  };

  const star = async (u) => {
    try {
      const res = await api.admin.favorite(u.id);
      toast(res.status === 'success' ? `⭐ ${u.name} received Admin's Favorite` : `${u.name} already has Admin's Favorite`);
    } catch (e) {
      toast(e.message, 'error');
    }
  };

  const rows = (data || []).filter((u) => `${u.name} ${u.city} ${u.blood_group} ${u.referral_code}`.toLowerCase().includes(q.toLowerCase()));

  return (
    <div className="card overflow-hidden">
      <div className="border-b border-slate-800 p-4">
        <input className="input max-w-sm" placeholder="Search name, city, group, code…" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      <ErrorBox error={error} />
      {loading && !data ? (
        <Loading />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                {['Name', 'Group', 'City', 'Role', 'Points', 'Donations', 'Telegram', 'Code', 'Verified', 'Recognise'].map((h) => (
                  <th key={h} className="whitespace-nowrap px-4 py-3 font-semibold">
                    {h}
                  </th>
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
                        <Hospital className="h-4 w-4" /> Hospital
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-slate-300">
                        <Droplet className="h-4 w-4 text-red-400" /> Donor
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className="font-bold tabular-nums">{u.points}</span> <BadgeChip badge={u.badge} />
                  </td>
                  <td className="px-4 py-3 tabular-nums">{u.total_donations}</td>
                  <td className="px-4 py-3">{u.telegram_linked ? <Send className="h-4 w-4 text-sky-400" /> : <span className="text-slate-600">—</span>}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">{u.referral_code}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggle(u)}
                      className={cx(
                        'flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs font-semibold',
                        u.is_verified ? 'border-sky-500/50 bg-sky-500/10 text-sky-300' : 'border-slate-700 text-slate-400 hover:border-slate-500',
                      )}
                    >
                      <BadgeCheck className="h-3.5 w-3.5" /> {u.is_verified ? 'Verified' : 'Verify'}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    {u.role === 'donor' && (
                      <button
                        onClick={() => star(u)}
                        title="Award the Admin's Favorite achievement (+300 BLP)"
                        className="rounded-lg border border-slate-700 px-2.5 py-1 text-xs font-semibold text-amber-300 hover:border-amber-400/60"
                      >
                        ⭐ Favorite
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
  const { data, error, loading } = usePoll(() => api.admin.vouchers(), 5000);
  if (loading && !data) return <Loading />;
  return (
    <div className="card overflow-hidden">
      <ErrorBox error={error} />
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              {['User', 'Reward', 'Cost', 'Code', 'Status', 'Issued'].map((h) => (
                <th key={h} className="px-4 py-3 font-semibold">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {data?.map((v) => (
              <tr key={v.id}>
                <td className="px-4 py-3 font-medium">{v.user}</td>
                <td className="px-4 py-3">{v.reward_name}</td>
                <td className="px-4 py-3 tabular-nums">{v.points_cost ? `${v.points_cost} BLP` : 'Referral bonus'}</td>
                <td className="px-4 py-3 font-mono text-red-300">{v.voucher_code}</td>
                <td className="px-4 py-3 text-emerald-400">{v.status}</td>
                <td className="px-4 py-3 text-slate-400">{timeAgo(v.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!data?.length && <p className="py-10 text-center text-slate-500">No vouchers issued yet.</p>}
      </div>
    </div>
  );
}
