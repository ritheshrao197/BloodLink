import { useEffect, useMemo, useRef, useState } from 'react';
import { Award } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { cx } from '../lib/utils';
import { ErrorBox, Loading, PageHeader, StatCard } from '../components/ui';
import { AchievementCard, RARITY, TierBadge } from '../components/Achievements';

const CATEGORY_ICON = { Donation: '🩸', Speed: '⚡', Referral: '🤝', Streak: '🔥', Location: '🌍', Fun: '🎮', Verification: '🛡️' };

export default function Achievements() {
  const { user } = useSession();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [category, setCategory] = useState('All');
  const [show, setShow] = useState('all'); // all | unlocked | locked
  const newKeys = useRef(new Set());

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
  }, [user?.id]);

  // Signed out, the catalog has no per-user fields; normalise both shapes
  const view = useMemo(() => {
    if (!data) return null;
    if (user) return data;
    const all = data.achievements;
    const families = {};
    for (const a of all.filter((x) => x.family)) {
      const f = (families[a.family] ||= { key: a.family, name: a.name, icon: a.icon, category: a.category, description: a.description, unit: a.requirement.replace(/^\d+ /, ''), tier: null, value: 0, tiers: [] });
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

  return (
    <div className="space-y-8">
      <PageHeader
        icon={Award}
        title="Achievements"
        subtitle="Permanent, collectible badges for how you show up. Separate from BLP: you can't spend them, only earn them."
      />

      {s ? (
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard icon={Award} label="Unlocked" value={`${s.unlocked}/${s.total}`} hint={`${Math.round((100 * s.unlocked) / s.total)}% complete`} />
          <StatCard icon={Award} label="BLP from achievements" value={s.points_earned} accent="text-amber-300" />
          <StatCard
            icon={Award}
            label="Rarest"
            value={rarest(view.singles)?.icon || '—'}
            hint={rarest(view.singles) ? `${rarest(view.singles).name} · ${rarest(view.singles).percent_of_donors}% of donors` : 'Donate to start your collection'}
            accent="text-fuchsia-300"
          />
        </div>
      ) : (
        <div className="card flex flex-wrap items-center justify-between gap-3 p-5 text-sm text-slate-300">
          <span>Sign in to see your collection and progress towards each achievement.</span>
          <Link to="/profile" className="btn-primary px-4 py-2 text-sm">
            Sign in
          </Link>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2">
        {['All', ...view.categories].map((c) => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            className={cx('rounded-full border px-3 py-1.5 text-sm transition', category === c ? 'border-red-500 bg-red-600/20 text-red-300' : 'border-slate-700 text-slate-300 hover:border-slate-500')}
          >
            {CATEGORY_ICON[c] || '🏆'} {c}
          </button>
        ))}
        {user && (
          <select className="input ml-auto w-auto py-1.5 text-sm" value={show} onChange={(e) => setShow(e.target.value)} aria-label="Filter">
            <option value="all">All</option>
            <option value="unlocked">Unlocked</option>
            <option value="locked">Locked</option>
          </select>
        )}
      </div>

      {families.length > 0 && show !== 'locked' && (
        <section>
          <h2 className="mb-3 text-lg font-bold">Tiered badges</h2>
          <div className="grid gap-3 md:grid-cols-2">
            {families.map((f) => (
              <TierBadge key={f.key} f={f} isNew={f.tiers.some((t) => newKeys.current.has(`${f.key}_${t.tier.toLowerCase()}`))} />
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-bold">Collection</h2>
        {singles.length ? (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {singles.map((a) => (
              <AchievementCard key={a.key} a={a} isNew={newKeys.current.has(a.key)} />
            ))}
          </div>
        ) : (
          <p className="py-8 text-center text-sm text-slate-500">Nothing here yet.</p>
        )}
      </section>

      <section className="card p-5">
        <h2 className="font-bold">Rarity</h2>
        <div className="mt-3 flex flex-wrap gap-4 text-sm">
          {Object.entries(RARITY).map(([name, r]) => (
            <span key={name} className={cx('flex items-center gap-1.5 font-semibold', r.text)}>
              <span className={cx('h-2 w-2 rounded-full', r.dot)} />
              {name}
            </span>
          ))}
        </div>
        <p className="mt-3 text-xs text-slate-500">
          Streaks count consecutive 3-month windows because whole-blood donors need at least 90 days between donations (120 for
          women). We never reward donating more often than is safe.
        </p>
      </section>
    </div>
  );
}

function rarest(singles) {
  return singles.filter((a) => a.unlocked).sort((a, b) => a.percent_of_donors - b.percent_of_donors)[0];
}
