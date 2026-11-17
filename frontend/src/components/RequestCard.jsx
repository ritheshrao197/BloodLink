import { BadgeCheck, Clock, Hospital, MapPin } from 'lucide-react';
import { BloodTag } from './ui';
import { URGENCY, cx, timeAgo } from '../lib/utils';

export default function RequestCard({ request: r, onRespond, highlight }) {
  const u = URGENCY[r.urgency] || URGENCY.High;
  const pct = Math.min(100, Math.round((r.units_fulfilled / r.units_needed) * 100));
  const active = r.status === 'Active';
  return (
    <div className={cx('card relative flex flex-col overflow-hidden p-5 transition hover:-translate-y-0.5', u.border, highlight && 'ring-2 ring-red-500')}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          {active && (
            <span className="relative flex h-2.5 w-2.5">
              <span className={cx('absolute inline-flex h-full w-full animate-pulse-ring rounded-full', u.dot)} />
              <span className={cx('relative inline-flex h-2.5 w-2.5 rounded-full', u.dot)} />
            </span>
          )}
          <span className={cx('rounded-md px-2 py-0.5 text-xs font-bold uppercase tracking-wide', active ? u.chip : 'bg-emerald-600 text-white')}>
            {active ? r.urgency : r.status}
          </span>
          {r.is_verified && (
            <span className="inline-flex items-center gap-1 text-xs text-sky-400" title="Verified by admin">
              <BadgeCheck className="h-3.5 w-3.5" /> Verified
            </span>
          )}
        </div>
        <span className="flex items-center gap-1 text-xs text-slate-500">
          <Clock className="h-3.5 w-3.5" />
          {timeAgo(r.created_at)}
        </span>
      </div>

      <div className="mt-4 flex items-center gap-3">
        <BloodTag group={r.blood_group} size="lg" />
        <div className="min-w-0">
          <h3 className="text-lg font-bold leading-tight">{r.blood_group} Needed</h3>
          <p className="truncate text-sm text-slate-400">for {r.requester_name}</p>
        </div>
      </div>

      <div className="mt-4 space-y-1.5 text-sm text-slate-300">
        <p className="flex items-center gap-2">
          <Hospital className="h-4 w-4 shrink-0 text-slate-500" /> {r.hospital}
        </p>
        <p className="flex items-center gap-2">
          <MapPin className="h-4 w-4 shrink-0 text-slate-500" /> {r.city}
          {r.state && <span className="text-slate-500">, {r.state}</span>}
        </p>
      </div>

      <div className="mt-4">
        <div className="mb-1 flex justify-between text-xs text-slate-400">
          <span>
            {r.units_fulfilled}/{r.units_needed} units pledged
          </span>
          <span>Accepts: {r.compatible_donor_groups.join(' ')}</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
          <div className="h-full rounded-full bg-red-500 transition-all" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {active && onRespond && (
        <button onClick={() => onRespond(r)} className="btn-primary mt-5 w-full">
          🩸 I Can Donate
        </button>
      )}
      {!active && r.fulfilled_by && <p className="mt-4 text-sm text-emerald-400">✓ Fulfilled by {r.fulfilled_by}</p>}
    </div>
  );
}
