import { Lock } from 'lucide-react';
import { cx, timeAgo } from '../lib/utils';

// Full class strings so Tailwind keeps them
export const RARITY = {
  Common: { text: 'text-slate-300', card: 'border-slate-500/60 bg-slate-800/60', glow: '', dot: 'bg-slate-400' },
  Uncommon: { text: 'text-emerald-300', card: 'border-emerald-400/60 bg-emerald-950/30', glow: 'shadow-lg shadow-emerald-500/20', dot: 'bg-emerald-400' },
  Rare: { text: 'text-sky-300', card: 'border-sky-400/60 bg-sky-950/30', glow: 'shadow-lg shadow-sky-500/30', dot: 'bg-sky-400' },
  Epic: { text: 'text-fuchsia-300', card: 'border-fuchsia-400/70 bg-fuchsia-950/30', glow: 'shadow-xl shadow-fuchsia-500/30', dot: 'bg-fuchsia-400' },
  Legendary: { text: 'text-amber-300', card: 'border-amber-400/80 bg-amber-950/30', glow: 'shadow-xl shadow-amber-400/40', dot: 'bg-amber-400' },
  Mythic: { text: 'text-red-300', card: 'border-red-500/80 bg-red-950/40', glow: 'shadow-2xl shadow-red-500/50 animate-glow', dot: 'bg-red-500' },
};

export const TIER = {
  Bronze: { bar: 'bg-amber-700', ring: 'ring-amber-700', bg: 'from-amber-800/50 to-amber-950/40', text: 'text-amber-500', glow: '' },
  Silver: { bar: 'bg-slate-300', ring: 'ring-slate-300', bg: 'from-slate-500/40 to-slate-800/40', text: 'text-slate-200', glow: 'shadow-lg shadow-slate-300/20' },
  Gold: { bar: 'bg-yellow-400', ring: 'ring-yellow-400', bg: 'from-yellow-600/40 to-amber-900/30', text: 'text-yellow-300', glow: 'shadow-xl shadow-yellow-400/40' },
  Platinum: { bar: 'bg-cyan-300', ring: 'ring-cyan-300', bg: 'from-cyan-500/40 to-indigo-900/40', text: 'text-cyan-200', glow: 'shadow-2xl shadow-cyan-300/50 animate-glow' },
};

export function RarityTag({ rarity, className }) {
  const r = RARITY[rarity] || RARITY.Common;
  return (
    <span className={cx('inline-flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wide', r.text, className)}>
      <span className={cx('h-1.5 w-1.5 rounded-full', r.dot)} />
      {rarity}
    </span>
  );
}

export function AchievementCard({ a, isNew }) {
  const r = RARITY[a.rarity] || RARITY.Common;
  const unlocked = a.unlocked !== false;
  const pct = a.target ? Math.round((100 * Math.min(a.progress ?? 0, a.target)) / a.target) : 0;
  return (
    <div
      className={cx(
        'relative flex flex-col rounded-xl border-2 p-4 transition',
        unlocked ? cx(r.card, r.glow, 'hover:-translate-y-0.5') : 'border-slate-800 bg-slate-900/60',
      )}
      title={a.requirement}
    >
      {isNew && <span className="absolute right-2 top-2 rounded-full bg-red-600 px-2 py-0.5 text-[10px] font-bold">NEW</span>}
      <div className={cx('text-4xl', !unlocked && 'opacity-30 grayscale')}>{a.icon}</div>
      <h3 className={cx('mt-2 font-bold leading-tight', !unlocked && 'text-slate-400')}>{a.name}</h3>
      <RarityTag rarity={a.rarity} className="mt-1" />
      <p className={cx('mt-2 flex-1 text-xs', unlocked ? 'text-slate-300' : 'text-slate-500')}>{unlocked ? a.description : a.requirement}</p>
      {unlocked ? (
        <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
          <span>{a.unlocked_at ? timeAgo(a.unlocked_at) : `+${a.points} BLP`}</span>
          {a.percent_of_donors != null && <span>{a.percent_of_donors}% of donors</span>}
        </div>
      ) : (
        <div className="mt-3">
          <div className="mb-1 flex justify-between text-[11px] text-slate-500">
            <span className="flex items-center gap-1">
              <Lock className="h-3 w-3" />
              {a.progress ?? 0}/{a.target}
            </span>
            <span>+{a.points} BLP</span>
          </div>
          <div className="h-1 overflow-hidden rounded-full bg-slate-800">
            <div className="h-full rounded-full bg-slate-500" style={{ width: `${pct}%` }} />
          </div>
        </div>
      )}
    </div>
  );
}

/** A GitHub-style tiered badge: one badge that levels up Bronze -> Platinum. */
export function TierBadge({ f, isNew }) {
  const t = f.tier && TIER[f.tier];
  const nextPct = f.next ? Math.min(100, Math.round((100 * f.value) / f.next.target)) : 100;
  return (
    <div className={cx('relative flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4', t?.glow)}>
      {isNew && <span className="absolute right-2 top-2 rounded-full bg-red-600 px-2 py-0.5 text-[10px] font-bold">NEW</span>}
      <div
        className={cx(
          'flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-gradient-to-br text-3xl ring-4',
          t ? cx(t.bg, t.ring) : 'from-slate-800 to-slate-900 opacity-40 ring-slate-700 grayscale',
        )}
      >
        {f.icon}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline gap-x-2">
          <h3 className="font-bold">{f.name}</h3>
          <span className={cx('text-xs font-bold uppercase tracking-wide', t ? t.text : 'text-slate-500')}>{f.tier || 'Locked'}</span>
        </div>
        <p className="text-xs text-slate-400">{f.description}</p>
        <div className="mt-2 flex gap-1">
          {f.tiers.map((x) => (
            <span
              key={x.tier}
              title={`${x.tier}: ${x.target} ${f.unit} (+${x.points} BLP) · ${x.percent_of_donors}% of donors`}
              className={cx('h-1.5 flex-1 rounded-full', x.unlocked_at ? TIER[x.tier].bar : 'bg-slate-800')}
            />
          ))}
        </div>
        <p className="mt-1 text-[11px] text-slate-500">
          {f.next ? (
            <>
              {f.value}/{f.next.target} {f.unit} to <b className={TIER[f.next.tier].text}>{f.next.tier}</b> ({nextPct}%)
            </>
          ) : (
            'Max tier reached'
          )}
        </p>
      </div>
    </div>
  );
}

/** Compact row of a user's rarest achievement icons (leaderboard, profile header). */
export function Showcase({ data, size = 'text-lg' }) {
  if (!data?.count) return null;
  return (
    <span className="inline-flex items-center gap-0.5" title={`${data.count} achievements`}>
      {data.top.map((a) => (
        <span key={a.name} className={size} title={`${a.name}${a.tier ? ` (${a.tier})` : ''} · ${a.rarity}`}>
          {a.icon}
        </span>
      ))}
      <span className="ml-1 text-xs font-semibold text-slate-400">{data.count}</span>
    </span>
  );
}
