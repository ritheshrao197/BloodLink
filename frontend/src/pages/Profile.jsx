import { useState } from 'react';
import { BadgeCheck, CheckCircle2, Droplet, Gift, History, LogOut, Send, UserRound, Users } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { BADGES, cx } from '../lib/utils';
import { useI18n } from '../i18n';
import { useToast } from '../components/Toast';
import { BloodTag, CopyField, PageHeader, StatCard, Toggle } from '../components/ui';
import SignInByCode from '../components/SignInByCode';
import { Showcase } from '../components/Achievements';

// Voucher names are stored in English; map them back to catalog ids so they can be translated
const REWARD_IDS = { 'Coffee Voucher': 1, 'Movie Ticket': 2, 'Shopping Voucher': 3, 'College Merch': 4 };

export default function Profile() {
  const { user, setUser, signOut, refresh } = useSession();
  const { t, tOr, num, ago, date, reason } = useI18n();
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const activity = usePoll(() => (user ? api.activity(user.id) : Promise.resolve(null)), 8000, user?.id);

  // keep header points in sync with background events (e.g. Telegram donations)
  usePoll(() => refresh(), 8000, user?.id);

  if (!user) {
    return (
      <div className="mx-auto max-w-md">
        <PageHeader icon={UserRound} title={t('profile.title')} subtitle={t('profile.signInSubtitle')} />
        <div className="card space-y-4 p-6">
          <SignInByCode />
          <p className="text-center text-sm text-slate-400">
            {t('profile.newHere')}{' '}
            <Link to="/register" className="font-semibold text-red-400 hover:underline">
              {t('profile.registerLink')}
            </Link>
          </p>
        </div>
      </div>
    );
  }

  const info = user.badge_info;
  const next = info.next;
  const progress = next ? Math.min(100, Math.round(((user.points - info.min_points) / (next.min_points - info.min_points)) * 100)) : 100;
  const a = activity.data;
  const rewardName = (name) => (REWARD_IDS[name] ? tOr(`reward.${REWARD_IDS[name]}.name`, name) : name);

  const toggleAvailability = async (value) => {
    setSaving(true);
    try {
      setUser(await api.setAvailability(user.id, value));
      toast(value ? t('profile.availableOn') : t('profile.availableOff'));
    } catch (e) {
      toast(e.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="card flex flex-wrap items-center gap-6 p-6 sm:p-8">
        <BloodTag group={user.blood_group} size="lg" className="h-20 min-w-20 text-3xl" />
        <div className="min-w-0 flex-1">
          <h1 className="flex items-center gap-2 text-3xl font-extrabold">
            {user.name}
            {user.is_verified && <BadgeCheck className="h-6 w-6 text-sky-400" aria-label={t('common.verified')} />}
          </h1>
          <p className="text-slate-400">
            {user.city} · {user.role === 'hospital' ? t('common.hospital') : t('common.donor')} · {t('profile.since', { date: date(user.created_at) })}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
            <span className={cx('font-bold', BADGES[user.badge]?.text)}>
              {info.icon} {t(`badge.${user.badge}`)}: {t(`badge.title.${user.badge}`)}
            </span>
            {user.extra_badges.includes('Influencer') && <span className="font-bold text-fuchsia-300">{t('profile.champion')}</span>}
          </div>
          {user.achievements?.count > 0 && (
            <Link to="/achievements" className="mt-2 inline-flex items-center gap-2 rounded-lg bg-slate-800/60 px-3 py-1.5 text-sm hover:bg-slate-800">
              <Showcase data={user.achievements} />
              <span className="text-slate-400">{t('profile.achievements')}</span>
            </Link>
          )}
        </div>
        <div className="flex flex-col items-end gap-3">
          <label className="flex items-center gap-3 text-sm">
            <span className={user.is_available ? 'text-emerald-400' : 'text-slate-400'}>
              {user.is_available ? t('profile.availableToDonate') : t('profile.notAvailable')}
            </span>
            <Toggle checked={user.is_available} onChange={toggleAvailability} disabled={saving} />
          </label>
          <button onClick={signOut} className="flex min-h-10 items-center gap-1.5 text-sm text-slate-400 hover:text-slate-50">
            <LogOut className="h-4 w-4" /> {t('common.signOut')}
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Droplet} label={t('profile.points')} value={num(user.points)} hint="BLP" />
        <StatCard
          icon={History}
          label={t('profile.donations')}
          value={user.total_donations}
          hint={user.last_donation_at ? t('profile.lastAgo', { when: ago(user.last_donation_at) }) : t('profile.noneYet')}
        />
        <StatCard icon={Users} label={t('profile.referrals')} value={user.referrals.total} hint={t('profile.referralsDonated', { n: user.referrals.donated })} accent="text-sky-400" />
        <StatCard icon={Gift} label={t('profile.referralPoints')} value={num(user.referrals.points_earned)} accent="text-fuchsia-300" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="text-lg font-bold">{t('profile.badgeProgress')}</h2>
          <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-sm">
            <span>
              {info.icon} {t(`badge.${user.badge}`)}
            </span>
            <span className="text-slate-400">
              {next ? t('profile.toNext', { n: num(next.min_points - user.points), icon: next.icon, name: t(`badge.${next.name}`) }) : t('profile.max')}
            </span>
          </div>
          <div className="progress-bar mt-2 h-3">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>

          <h2 className="mt-8 text-lg font-bold">{t('profile.telegram')}</h2>
          {user.telegram_linked ? (
            <p className="mt-2 flex items-center gap-2 text-sm text-emerald-400">
              <CheckCircle2 className="h-4 w-4 shrink-0" /> {t('profile.linked', { as: user.telegram_username ? ` (@${user.telegram_username})` : '' })}
            </p>
          ) : (
            <>
              <p className="mt-2 text-sm text-slate-400">{t('profile.linkPrompt')}</p>
              <a href={user.telegram_link_url} target="_blank" rel="noreferrer" className="btn-primary mt-3 from-sky-600 to-sky-700 shadow-sky-900/40">
                <Send className="h-4 w-4" /> {t('profile.linkBtn')}
              </a>
            </>
          )}
        </div>

        <div className="card space-y-4 p-6">
          <h2 className="text-lg font-bold">{t('profile.invite')}</h2>
          <div className="rounded-xl bg-slate-800/60 p-4 text-center">
            <div className="text-xs text-slate-400">{t('profile.codeLabel')}</div>
            <div className="font-mono text-2xl font-extrabold tracking-wider text-red-400">{user.referral_code}</div>
          </div>
          <CopyField label={t('profile.tgLink')} value={user.referral_link} />
          <CopyField label={t('profile.webLink')} value={user.web_referral_link} />
          <div className="grid grid-cols-3 gap-2 text-center text-sm">
            {[
              [t('profile.invited'), user.referrals.total],
              [t('profile.registered'), user.referrals.registered],
              [t('profile.donated'), user.referrals.donated],
            ].map(([k, v]) => (
              <div key={k} className="rounded-lg bg-slate-800/50 py-2">
                <div className="text-xl font-bold">{v}</div>
                <div className="text-xs text-slate-400">{k}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Panel title={t('profile.history')} rows={a?.points_log} empty={t('profile.noActivity')}>
          {(l) => (
            <>
              <span className="text-slate-300">
                {reason(l.reason)}
                <span className="block text-xs text-slate-500">{ago(l.created_at)}</span>
              </span>
              <span className={cx('shrink-0 font-bold tabular-nums', l.amount >= 0 ? 'text-emerald-400' : 'text-red-400')}>
                {l.amount >= 0 ? '+' : ''}
                {l.amount}
              </span>
            </>
          )}
        </Panel>
        <Panel title={t('profile.donationsPanel')} rows={a?.donations} empty={t('profile.noDonations')}>
          {(d) => (
            <>
              <span className="text-slate-300">
                {d.blood_group} · {d.hospital}, {d.city}
                <span className="block text-xs text-slate-500">
                  {ago(d.created_at)}
                  {d.quick_response && t('profile.quick')}
                </span>
              </span>
              <span className="shrink-0 font-bold text-emerald-400">+{d.points_awarded}</span>
            </>
          )}
        </Panel>
        <Panel title={t('profile.vouchers')} rows={[...(a?.vouchers || []), ...(a?.referrals || [])]} empty={t('profile.noVouchers')}>
          {(v) =>
            v.voucher_code ? (
              <>
                <span className="text-slate-300">
                  🎁 {rewardName(v.reward_name)}
                  <span className="block text-xs text-slate-500">{ago(v.created_at)}</span>
                </span>
                <code className="shrink-0 rounded bg-slate-800 px-2 py-0.5 text-sm text-red-300">{v.voucher_code}</code>
              </>
            ) : (
              <>
                <span className="text-slate-300">
                  🤝 {v.name} ({v.blood_group})<span className="block text-xs text-slate-500">{tOr(`profile.refStatus.${v.status}`, v.status)}</span>
                </span>
                <span className="shrink-0 font-bold text-emerald-400">+{v.points_awarded}</span>
              </>
            )
          }
        </Panel>
      </div>
    </div>
  );
}

function Panel({ title, rows, empty, children }) {
  return (
    <div className="card p-5">
      <h2 className="mb-3 font-bold">{title}</h2>
      {!rows?.length ? (
        <p className="py-6 text-center text-sm text-slate-500">{empty}</p>
      ) : (
        <ul className="max-h-80 divide-y divide-slate-800 overflow-y-auto pr-1 text-sm">
          {rows.map((r, i) => (
            <li key={i} className="flex items-start justify-between gap-3 py-2.5">
              {children(r)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
