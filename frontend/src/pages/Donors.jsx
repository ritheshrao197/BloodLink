import { useState } from 'react';
import { BadgeCheck, Search, Send, Users } from 'lucide-react';
import { api } from '../lib/api';
import { usePoll } from '../lib/usePoll';
import { BLOOD_GROUPS, COMPATIBILITY, cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { BadgeChip, BloodTag, Empty, ErrorBox, Loading, PageHeader } from '../components/ui';

export default function Donors() {
  const { t, ago, num } = useI18n();
  const [mode, setMode] = useState('compatible'); // compatible | exact
  const [group, setGroup] = useState('');
  const [city, setCity] = useState('');
  const [availableOnly, setAvailableOnly] = useState(true);

  const params = {
    compatible_for: mode === 'compatible' ? group : '',
    blood_group: mode === 'exact' ? group : '',
    city,
    available: availableOnly ? true : '',
  };
  const key = JSON.stringify(params);
  const { data, error, loading } = usePoll(() => api.donors(params), 0, key);

  return (
    <div>
      <PageHeader icon={Search} title={t('donors.title')} subtitle={t('donors.subtitle')} />

      <div className="card mb-6 grid gap-4 p-5 md:grid-cols-[auto_1fr_1fr_auto] md:items-end">
        <div>
          <span className="label">{t('donors.mode')}</span>
          <div className="flex rounded-lg bg-slate-800 p-1 text-sm" role="group" aria-label={t('donors.mode')}>
            {[
              ['compatible', t('donors.canDonateTo')],
              ['exact', t('donors.exact')],
            ].map(([m, label]) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                aria-pressed={mode === m}
                className={cx('min-h-9 rounded-md px-3 py-1.5 font-semibold', mode === m ? 'bg-red-600 text-white' : 'text-slate-300')}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="label" htmlFor="donor-group">
            {mode === 'compatible' ? t('donors.patientGroup') : t('donors.donorGroup')}
          </label>
          <select id="donor-group" className="input" value={group} onChange={(e) => setGroup(e.target.value)}>
            <option value="">{t('common.any')}</option>
            {BLOOD_GROUPS.map((g) => (
              <option key={g}>{g}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="donor-city">
            {t('donors.city')}
          </label>
          <input id="donor-city" className="input" placeholder={t('donors.anyCity')} value={city} onChange={(e) => setCity(e.target.value)} />
        </div>
        <label className="flex min-h-11 cursor-pointer items-center gap-2 pb-1 text-sm text-slate-300">
          <input type="checkbox" className="h-4 w-4 accent-red-600" checked={availableOnly} onChange={(e) => setAvailableOnly(e.target.checked)} />
          {t('donors.availableOnly')}
        </label>
      </div>

      {mode === 'compatible' && group && (
        <p className="mb-4 flex flex-wrap items-center gap-1 text-sm text-slate-400">
          {t('donors.canReceive', { group })}{' '}
          {COMPATIBILITY[group].map((g) => (
            <BloodTag key={g} group={g} size="sm" />
          ))}
        </p>
      )}

      <ErrorBox error={error} />
      {loading && !data ? (
        <Loading rows={4} />
      ) : !data?.length ? (
        <Empty icon={Users} title={t('donors.none')}>
          {t('donors.widen')}
        </Empty>
      ) : (
        <>
          <p className="mb-3 text-sm text-slate-400">{t('donors.count', { n: num(data.length) })}</p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.map((d) => (
              <div key={d.id} className="card card-hover flex items-center gap-4 p-4">
                <BloodTag group={d.blood_group} size="lg" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className="truncate font-bold">{d.name}</span>
                    {d.is_verified && <BadgeCheck className="h-4 w-4 shrink-0 text-sky-400" aria-label={t('common.verified')} />}
                    {d.telegram_linked && <Send className="h-3.5 w-3.5 shrink-0 text-sky-400" aria-label="Telegram" />}
                  </div>
                  <div className="text-sm text-slate-400">
                    {d.city} · {t('donors.donations', { n: d.total_donations })}
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-x-3 text-xs">
                    <BadgeChip badge={d.badge} />
                    <span className={d.is_available ? 'text-emerald-400' : 'text-slate-500'}>
                      {d.is_available ? `● ${t('common.available')}` : `○ ${t('common.unavailable')}`}
                    </span>
                  </div>
                  {d.last_donation_at && <div className="mt-0.5 text-xs text-slate-500">{t('donors.lastDonated', { when: ago(d.last_donation_at) })}</div>}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
