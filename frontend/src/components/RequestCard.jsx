import { BadgeCheck, Clock, Hospital, MapPin } from 'lucide-react';
import { BloodTag } from './ui';
import { URGENCY, cx } from '../lib/utils';
import { useI18n } from '../i18n';

export default function RequestCard({ request: r, onRespond, highlight }) {
  const { t, ago } = useI18n();
  const u = URGENCY[r.urgency] || URGENCY.High;
  const pct = Math.min(100, Math.round((r.units_fulfilled / r.units_needed) * 100));
  const active = r.status === 'Active';
  return (
    <article
      className={cx(
        'card card-hover relative flex flex-col overflow-hidden p-5',
        active && r.urgency === 'Critical' ? 'card-emergency' : u.border,
        highlight && 'ring-2 ring-blood-500',
      )}
      aria-label={t('request.aria', { urgency: t(`urgency.${r.urgency}`), group: r.blood_group, hospital: r.hospital })}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {active && (
            <span className="relative flex h-2.5 w-2.5">
              <span className={cx('absolute inline-flex h-full w-full animate-pulse-ring rounded-full', u.dot)} />
              <span className={cx('relative inline-flex h-2.5 w-2.5 rounded-full', u.dot)} />
            </span>
          )}
          <span className={cx('rounded-md px-2 py-0.5 text-xs font-bold uppercase tracking-wide', active ? u.chip : 'bg-emerald-600 text-white')}>
            {active ? t(`urgency.${r.urgency}`) : t(`status.${r.status}`)}
          </span>
          {r.is_verified && (
            <span className="inline-flex items-center gap-1 text-xs text-sky-400" title={t('request.verifiedTitle')}>
              <BadgeCheck className="h-3.5 w-3.5" /> {t('common.verified')}
            </span>
          )}
        </div>
        <span className="flex shrink-0 items-center gap-1 text-xs text-slate-500">
          <Clock className="h-3.5 w-3.5" />
          {ago(r.created_at)}
        </span>
      </div>

      <div className="mt-4 flex items-center gap-3">
        <BloodTag group={r.blood_group} size="lg" />
        <div className="min-w-0">
          <h3 className="text-lg font-bold leading-tight">{t('request.needed', { group: r.blood_group })}</h3>
          <p className="truncate text-sm text-slate-400">{t('request.for', { name: r.requester_name })}</p>
        </div>
      </div>

      <div className="mt-4 space-y-1.5 text-sm text-slate-300">
        <p className="flex items-center gap-2">
          <Hospital className="h-4 w-4 shrink-0 text-slate-500" /> {r.hospital}
        </p>
        <p className="flex items-center gap-2">
          <MapPin className="h-4 w-4 shrink-0 text-slate-500" />
          <span>
            {r.city}
            {r.state && <span className="text-slate-500">, {r.state}</span>}
          </span>
        </p>
      </div>

      <div className="mt-4">
        <div className="mb-1 flex flex-wrap justify-between gap-x-2 text-xs text-slate-400">
          <span>{t('request.pledged', { done: r.units_fulfilled, total: r.units_needed })}</span>
          <span>{t('request.accepts', { groups: r.compatible_donor_groups.join(' ') })}</span>
        </div>
        <div className="progress-bar h-1.5" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <div className="progress-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>

      {active && onRespond && (
        <button onClick={() => onRespond(r)} className="btn-primary mt-5 w-full">
          🩸 {t('common.iCanDonate')}
        </button>
      )}
      {!active && r.fulfilled_by && <p className="mt-4 text-sm text-emerald-400">{t('request.fulfilledBy', { name: r.fulfilled_by })}</p>}
    </article>
  );
}
