import { useState } from 'react';
import { BadgeCheck, Search, Send, Users } from 'lucide-react';
import { api } from '../lib/api';
import { usePoll } from '../lib/usePoll';
import { BLOOD_GROUPS, COMPATIBILITY, cx, timeAgo } from '../lib/utils';
import { BadgeChip, BloodTag, Empty, ErrorBox, Loading, PageHeader } from '../components/ui';

export default function Donors() {
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
      <PageHeader icon={Search} title="Find Donors" subtitle="Search registered donors by blood group, city and availability, using rule-based ABO/Rh matching." />

      <div className="card mb-6 grid gap-4 p-5 md:grid-cols-[auto_1fr_1fr_auto] md:items-end">
        <div>
          <span className="label">Match mode</span>
          <div className="flex rounded-lg bg-slate-800 p-1 text-sm">
            {[
              ['compatible', 'Can donate to'],
              ['exact', 'Exact group'],
            ].map(([m, label]) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={cx('rounded-md px-3 py-1.5 font-semibold', mode === m ? 'bg-red-600 text-white' : 'text-slate-300')}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="label" htmlFor="donor-group">{mode === 'compatible' ? 'Patient blood group' : 'Donor blood group'}</label>
          <select id="donor-group" className="input" value={group} onChange={(e) => setGroup(e.target.value)}>
            <option value="">Any</option>
            {BLOOD_GROUPS.map((g) => (
              <option key={g}>{g}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="donor-city">City</label>
          <input id="donor-city" className="input" placeholder="Any city" value={city} onChange={(e) => setCity(e.target.value)} />
        </div>
        <label className="flex cursor-pointer items-center gap-2 pb-2.5 text-sm text-slate-300">
          <input type="checkbox" className="h-4 w-4 accent-red-600" checked={availableOnly} onChange={(e) => setAvailableOnly(e.target.checked)} />
          Available only
        </label>
      </div>

      {mode === 'compatible' && group && (
        <p className="mb-4 text-sm text-slate-400">
          A <b className="text-slate-200">{group}</b> patient can receive from:{' '}
          {COMPATIBILITY[group].map((g) => (
            <BloodTag key={g} group={g} size="sm" className="mr-1" />
          ))}
        </p>
      )}

      <ErrorBox error={error} />
      {loading && !data ? (
        <Loading />
      ) : !data?.length ? (
        <Empty icon={Users} title="No donors found">
          Try widening the search.
        </Empty>
      ) : (
        <>
          <p className="mb-3 text-sm text-slate-400">{data.length} donor(s)</p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.map((d) => (
              <div key={d.id} className="card flex items-center gap-4 p-4">
                <BloodTag group={d.blood_group} size="lg" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className="truncate font-bold">{d.name}</span>
                    {d.is_verified && <BadgeCheck className="h-4 w-4 shrink-0 text-sky-400" />}
                    {d.telegram_linked && <Send className="h-3.5 w-3.5 shrink-0 text-sky-400" />}
                  </div>
                  <div className="text-sm text-slate-400">
                    {d.city} · {d.total_donations} donation(s)
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs">
                    <BadgeChip badge={d.badge} />
                    <span className={d.is_available ? 'text-emerald-400' : 'text-slate-500'}>
                      {d.is_available ? '● Available' : '○ Unavailable'}
                    </span>
                  </div>
                  {d.last_donation_at && <div className="mt-0.5 text-xs text-slate-500">Last donated {timeAgo(d.last_donation_at)}</div>}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
