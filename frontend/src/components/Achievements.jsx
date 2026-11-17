import { Lock, Share2 } from 'lucide-react';
import { cx } from '../lib/utils';
import { useI18n } from '../i18n';

// Full class strings so Tailwind keeps them
export const RARITY = {
  Common: { text: 'text-slate-300', card: 'border-slate-500/60 bg-slate-800/60', glow: '', dot: 'bg-rarity-common' },
  Uncommon: { text: 'text-emerald-300', card: 'border-emerald-400/60 bg-emerald-950/30', glow: 'shadow-lg shadow-emerald-500/20', dot: 'bg-rarity-uncommon' },
  Rare: { text: 'text-blue-300', card: 'border-blue-400/60 bg-blue-950/30', glow: 'shadow-lg shadow-blue-500/30', dot: 'bg-rarity-rare' },
  Epic: { text: 'text-violet-300', card: 'border-violet-400/70 bg-violet-950/30', glow: 'shadow-glow-purple', dot: 'bg-rarity-epic' },
  Legendary: { text: 'text-amber-300', card: 'border-amber-400/80 bg-amber-950/30', glow: 'animate-glow', dot: 'bg-rarity-legendary' },
  Mythic: { text: 'text-red-300', card: 'border-red-500/80 bg-red-950/40', glow: 'animate-glow-red', dot: 'bg-rarity-mythic' },
};

export const TIER = {
  Bronze: { bar: 'bg-amber-700', ring: 'ring-amber-700', bg: 'from-amber-800/50 to-amber-950/40', text: 'text-amber-500', glow: '' },
  Silver: { bar: 'bg-slate-300', ring: 'ring-slate-300', bg: 'from-slate-500/40 to-slate-800/40', text: 'text-slate-200', glow: 'shadow-lg shadow-slate-300/20' },
  Gold: { bar: 'bg-yellow-400', ring: 'ring-yellow-400', bg: 'from-yellow-600/40 to-amber-900/30', text: 'text-yellow-300', glow: 'shadow-xl shadow-yellow-400/40' },
  Platinum: { bar: 'bg-cyan-300', ring: 'ring-cyan-300', bg: 'from-cyan-500/40 to-indigo-900/40', text: 'text-cyan-200', glow: 'shadow-2xl shadow-cyan-300/50' },
};

/**
 * Translated description / requirement for an achievement. Names stay as-is (they are proper names, like GitHub's);
 * texts fall back to the English sent by the API when a language has no override.
 */
export function achText({ tOr }, a) {
  if (a.family) {
    const unit = tOr(`achv.${a.family}.unit`, a.unit || a.requirement?.replace(/^\d+ /, ''));
    return { description: tOr(`achv.${a.family}.d`, a.description), requirement: `${a.target} ${unit}`, unit };
  }
  return { description: tOr(`achv.${a.key}.d`, a.description), requirement: tOr(`achv.${a.key}.r`, a.requirement) };
}

export function RarityTag({ rarity, className }) {
  const { t } = useI18n();
  const r = RARITY[rarity] || RARITY.Common;
  return (
    <span className={cx('inline-flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wide', r.text, className)}>
      <span className={cx('h-1.5 w-1.5 rounded-full', r.dot)} />
      {t(`achievements.rarityName.${rarity}`)}
    </span>
  );
}

function NewTag() {
  const { t } = useI18n();
  return <span className="absolute right-2 top-2 rounded-full bg-blood-600 px-2 py-0.5 text-[10px] font-bold text-white">{t('achievements.new')}</span>;
}

export function AchievementCard({ a, isNew, onShare }) {
  const i18n = useI18n();
  const { t, ago } = i18n;
  const { description, requirement } = achText(i18n, a);
  const r = RARITY[a.rarity] || RARITY.Common;
  const unlocked = a.unlocked !== false;
  const pct = a.target ? Math.round((100 * Math.min(a.progress ?? 0, a.target)) / a.target) : 0;
  return (
    <div
      className={cx(
        'relative flex flex-col rounded-xl border-2 p-4 transition',
        unlocked ? cx(r.card, r.glow, 'hover:-translate-y-0.5') : 'border-slate-800 bg-slate-900/60',
      )}
      title={requirement}
    >
      {isNew && <NewTag />}
      <div className={cx('text-4xl', !unlocked && 'opacity-30 grayscale')}>{a.icon}</div>
      <h3 className={cx('mt-2 font-bold leading-tight', !unlocked && 'text-slate-400')}>{a.name}</h3>
      <RarityTag rarity={a.rarity} className="mt-1" />
      <p className={cx('mt-2 flex-1 text-xs', unlocked ? 'text-slate-300' : 'text-slate-500')}>{unlocked ? description : requirement}</p>
      {unlocked ? (
        <div className="mt-3 flex flex-wrap items-center justify-between gap-x-2 text-[11px] text-slate-400">
          <span>{a.unlocked_at ? ago(a.unlocked_at) : `+${a.points} BLP`}</span>
          {a.percent_of_donors != null && <span>{t('achievements.pctDonors', { pct: a.percent_of_donors })}</span>}
          {onShare && (
            <button onClick={() => onShare(a)} className="-mr-1 flex h-8 w-8 items-center justify-center rounded-lg hover:bg-slate-800" aria-label={t('card.cta')} title={t('card.cta')}>
              <Share2 className="h-4 w-4" />
            </button>
          )}
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
  const i18n = useI18n();
  const { t } = i18n;
  const { description, unit } = achText(i18n, { family: f.key, description: f.description, unit: f.unit, target: 0 });
  const tier = f.tier && TIER[f.tier];
  const nextPct = f.next ? Math.min(100, Math.round((100 * f.value) / f.next.target)) : 100;
  return (
    <div className={cx('relative flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4', tier?.glow)}>
      {isNew && <NewTag />}
      <div
        className={cx(
          'flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-gradient-to-br text-3xl ring-4',
          tier ? cx(tier.bg, tier.ring) : 'from-slate-800 to-slate-900 opacity-40 ring-slate-700 grayscale',
        )}
      >
        {f.icon}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline gap-x-2">
          <h3 className="font-bold">{f.name}</h3>
          <span className={cx('text-xs font-bold uppercase tracking-wide', tier ? tier.text : 'text-slate-500')}>
            {f.tier ? t(`achievements.tier.${f.tier}`) : t('achievements.locked')}
          </span>
        </div>
        <p className="text-xs text-slate-400">{description}</p>
        <div className="mt-2 flex gap-1">
          {f.tiers.map((x) => (
            <span
              key={x.tier}
              title={`${t(`achievements.tier.${x.tier}`)}: ${x.target} ${unit} (+${x.points} BLP) · ${t('achievements.pctDonors', { pct: x.percent_of_donors })}`}
              className={cx('h-1.5 flex-1 rounded-full', x.unlocked_at ? TIER[x.tier].bar : 'bg-slate-800')}
            />
          ))}
        </div>
        <p className="mt-1 text-[11px] text-slate-500">
          {f.next
            ? t('achievements.toTier', { value: f.value, target: f.next.target, unit, tier: t(`achievements.tier.${f.next.tier}`), pct: nextPct })
            : t('achievements.maxTier')}
        </p>
      </div>
    </div>
  );
}

/** Compact row of a user's rarest achievement icons (leaderboard, profile header). */
export function Showcase({ data, size = 'text-lg' }) {
  const { t } = useI18n();
  if (!data?.count) return null;
  return (
    <span className="inline-flex items-center gap-0.5" title={t('achievements.count', { n: data.count })}>
      {data.top.map((a) => (
        <span key={a.name} className={size} title={`${a.name}${a.tier ? ` (${t(`achievements.tier.${a.tier}`)})` : ''} · ${t(`achievements.rarityName.${a.rarity}`)}`}>
          {a.icon}
        </span>
      ))}
      <span className="ml-1 text-xs font-semibold text-slate-400">{data.count}</span>
    </span>
  );
}
