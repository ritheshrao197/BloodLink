import { useEffect, useMemo, useRef, useState } from 'react';
import { Award } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { ErrorBox, Loading, PageHeader, StatCard } from '../components/ui';
import { AchievementCard, RARITY, TierBadge } from '../components/Achievements';
import ShareCardModal from '../components/ShareCard';

const CATEGORY_ICON = { Donation: '🩸', Speed: '⚡', Referral: '🤝', Streak: '🔥', Location: '🌍', Fun: '🎮', Verification: '🛡️' };

export default function Achievements() {
  const { user } = useSession();
  const { t } = useI18n();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [category, setCategory] = useState('All');
  const [show, setShow] = useState('all'); // all | unlocked | locked
  const newKeys = useRef(new Set());
  const [sharing, setSharing] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    (user ? api.userAchievements(user.id) : api.achievements())
      .then((d) => {
        if (cancelled) return;
        if (user) {
          newKeys.current = new Set(d.new);
          if (d.new.length) api.achievementsSeen(user.id).catch(() => {});
        }
        setData(d);
      })
      .catch(setError);
    return () => {
      cancelled = true;
    };
  }, [user?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Signed out, the catalog has no per-user fields; normalise both shapes
  const view = useMemo(() => {
    if (!data) return null;
    if (user) return data;
    const all = data.achievements;
    const families = {};
    for (const a of all.filter((x) => x.family)) {
      const f = (families[a.family] ||= {
        key: a.family,
        name: a.name,
        icon: a.icon,
        category: a.category,
        description: a.description,
        unit: a.requirement.replace(/^\d+ /, ''),
        tier: null,
        value: 0,
        tiers: [],
      });
      f.tiers.push({ tier: a.tier, target: a.target, points: a.points, unlocked_at: null, percent_of_donors: a.percent_of_donors });
    }
    for (const f of Object.values(families)) f.next = { tier: 'Bronze', target: f.tiers[0].target, points: f.tiers[0].points };
    return {
      singles: all.filter((x) => !x.family).map((a) => ({ ...a, unlocked: false, progress: 0 })),
      families: Object.values(families),
      categories: data.categories,
      summary: null,
    };
  }, [data, user]);

  if (error) return <ErrorBox error={error} />;
  if (!view) return <Loading />;

  const singles = view.singles
    .filter((a) => category === 'All' || a.category === category)
    .filter((a) => show === 'all' || (show === 'unlocked' ? a.unlocked : !a.unlocked))
    .sort((a, b) => Number(b.unlocked) - Number(a.unlocked) || (b.unlocked ? 0 : b.progress / b.target - a.progress / a.target));
  const families = view.families.filter((f) => category === 'All' || f.category === category);
  const s = view.summary;
  const rare = rarest(view.singles);

  return (
    <div className="space-y-8">
      <PageHeader icon={Award} title={t('achievements.title')} subtitle={t('achievements.subtitle')} />

      {s ? (
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard
            icon={Award}
            label={t('achievements.unlocked')}
            value={`${s.unlocked}/${s.total}`}
            hint={t('achievements.complete', { n: Math.round((100 * s.unlocked) / s.total) })}
          />
          <StatCard icon={Award} label={t('achievements.fromAchievements')} value={s.points_earned} accent="text-amber-300" />
          <StatCard
            icon={Award}
            label={t('achievements.rarest')}
            value={rare?.icon || '—'}
            hint={rare ? t('achievements.rarestHint', { name: rare.name, pct: rare.percent_of_donors }) : t('achievements.startHint')}
            accent="text-fuchsia-300"
          />
        </div>
      ) : (
        <div className="card flex flex-wrap items-center justify-between gap-3 p-5 text-sm text-slate-300">
          <span>{t('achievements.signInPrompt')}</span>
          <Link to="/profile" className="btn-primary px-4 py-2 text-sm">
            {t('common.signIn')}
          </Link>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2">
        {['All', ...view.categories].map((c) => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            aria-pressed={category === c}
            className={cx(
              'min-h-9 rounded-full border px-3 py-1.5 text-sm transition',
              category === c ? 'border-brand-500 bg-brand-600/15 text-brand-300' : 'border-slate-700 text-slate-300 hover:border-slate-500',
            )}
          >
            {CATEGORY_ICON[c] || '🏆'} {t(`achievements.category.${c}`)}
          </button>
        ))}
        {user && (
          <select className="input ml-auto w-auto py-1.5 text-sm" value={show} onChange={(e) => setShow(e.target.value)} aria-label={t('achievements.filter')}>
            <option value="all">{t('achievements.showAll')}</option>
            <option value="unlocked">{t('achievements.showUnlocked')}</option>
            <option value="locked">{t('achievements.showLocked')}</option>
          </select>
        )}
      </div>

      {families.length > 0 && show !== 'locked' && (
        <section>
          <h2 className="mb-3 text-lg font-bold">{t('achievements.tiered')}</h2>
          <div className="grid gap-3 md:grid-cols-2">
            {families.map((f) => (
              <TierBadge key={f.key} f={f} isNew={f.tiers.some((x) => newKeys.current.has(`${f.key}_${x.tier.toLowerCase()}`))} />
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-bold">{t('achievements.collection')}</h2>
        {singles.length ? (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {singles.map((a) => (
              <AchievementCard key={a.key} a={a} isNew={newKeys.current.has(a.key)} onShare={user && a.unlocked ? setSharing : undefined} />
            ))}
          </div>
        ) : (
          <p className="py-8 text-center text-sm text-slate-500">{t('achievements.empty')}</p>
        )}
      </section>

      <section className="card p-5">
        <h2 className="font-bold">{t('achievements.rarity')}</h2>
        <div className="mt-3 flex flex-wrap gap-4 text-sm">
          {Object.entries(RARITY).map(([name, r]) => (
            <span key={name} className={cx('flex items-center gap-1.5 font-semibold', r.text)}>
              <span className={cx('h-2 w-2 rounded-full', r.dot)} />
              {t(`achievements.rarityName.${name}`)}
            </span>
          ))}
        </div>
        <p className="mt-3 text-xs text-slate-500">{t('achievements.safety')}</p>
      </section>
      <ShareCardModal open={!!sharing} onClose={() => setSharing(null)} kind="achievement" user={user} achievement={sharing} />
    </div>
  );
}

function rarest(singles) {
  return singles.filter((a) => a.unlocked).sort((a, b) => a.percent_of_donors - b.percent_of_donors)[0];
}
