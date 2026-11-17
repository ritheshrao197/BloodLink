import { Trophy } from 'lucide-react';
import { api } from '../lib/api';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { BADGES, cx } from '../lib/utils';
import { BadgeChip, BloodTag, ErrorBox, Loading, PageHeader } from '../components/ui';
import { Showcase } from '../components/Achievements';

const PODIUM = [
  { place: 2, height: 'h-28', ring: 'ring-slate-300/60', medal: '🥈' },
  { place: 1, height: 'h-36', ring: 'ring-yellow-400/70', medal: '🥇' },
  { place: 3, height: 'h-20', ring: 'ring-amber-700/70', medal: '🥉' },
];

export default function Leaderboard() {
  const { user } = useSession();
  const { data, error, loading } = usePoll(() => api.leaderboard(10), 4000);

  return (
    <div className="mx-auto max-w-4xl">
      <PageHeader icon={Trophy} title="Top Heroes" subtitle="Live ranking by BloodLink Points (BLP). Updates automatically as donations happen.">
        <span className="flex items-center gap-2 text-sm text-emerald-400">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" /> Live
        </span>
      </PageHeader>
      <ErrorBox error={error} />
      {loading && !data ? (
        <Loading />
      ) : (
        data && (
          <>
            {data.length >= 3 && (
              <div className="mb-8 grid grid-cols-3 items-end gap-3">
                {PODIUM.map(({ place, height, ring, medal }) => {
                  const u = data[place - 1];
                  return (
                    <div key={place} className="flex flex-col items-center text-center">
                      <div className={cx('flex h-16 w-16 items-center justify-center rounded-full bg-slate-800 text-3xl ring-4', ring)}>{medal}</div>
                      <div className="mt-2 max-w-full truncate font-bold">{u.name}</div>
                      <div className="text-sm text-red-400">{u.points} BLP</div>
                      <div className={cx('mt-2 flex w-full items-start justify-center rounded-t-xl bg-gradient-to-b from-red-600/30 to-slate-900 pt-3 text-3xl font-extrabold text-slate-300', height)}>
                        #{place}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            <div className="card divide-y divide-slate-800 overflow-hidden">
              {data.map((u, i) => (
                <div key={u.id} className={cx('flex items-center gap-3 px-4 py-3.5 sm:gap-4 sm:px-6', user?.id === u.id && 'bg-red-600/10')}>
                  <span className={cx('w-8 text-lg font-extrabold', i < 3 ? 'text-yellow-400' : 'text-slate-500')}>#{i + 1}</span>
                  <span className="text-2xl">{BADGES[u.badge]?.icon}</span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="truncate font-bold">{u.name}</span>
                      {user?.id === u.id && <span className="rounded bg-red-600 px-1.5 text-xs font-bold">YOU</span>}
                      {u.influencer && <span title="Community Champion (5+ referrals)">🗣️</span>}
                    </div>
                    <div className="flex flex-wrap items-center gap-x-2 text-xs text-slate-400">
                      <span>
                        {u.city} · {u.total_donations} donations · {u.referrals} referrals
                      </span>
                      <Showcase data={u.achievements} size="text-sm" />
                    </div>
                  </div>
                  <BloodTag group={u.blood_group} size="sm" />
                  <div className="hidden w-28 sm:block">
                    <BadgeChip badge={u.badge} />
                  </div>
                  <span className="w-24 text-right text-lg font-extrabold tabular-nums text-red-400">{u.points} BLP</span>
                </div>
              ))}
            </div>
          </>
        )
      )}

      <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {Object.entries(BADGES).map(([name, b]) => (
          <div key={name} className="card p-4 text-center">
            <div className="text-3xl">{b.icon}</div>
            <div className={cx('mt-1 font-bold', b.text)}>{name}</div>
            <div className="text-xs text-slate-400">{b.title}</div>
            <div className="mt-1 text-xs text-slate-500">{name === 'Platinum' ? '1000+ BLP' : `${b.min}+ BLP`}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
