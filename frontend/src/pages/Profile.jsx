import { useState } from 'react';
import { BadgeCheck, CheckCircle2, Droplet, Gift, History, LogOut, Send, UserRound, Users } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { BADGES, cx, timeAgo } from '../lib/utils';
import { useToast } from '../components/Toast';
import { BloodTag, CopyField, PageHeader, StatCard, Toggle } from '../components/ui';
import SignInByCode from '../components/SignInByCode';

export default function Profile() {
  const { user, setUser, signOut, refresh } = useSession();
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const activity = usePoll(() => (user ? api.activity(user.id) : Promise.resolve(null)), 8000, user?.id);

  // keep header points in sync with background events (e.g. Telegram donations)
  usePoll(() => refresh(), 8000, user?.id);

  if (!user) {
    return (
      <div className="mx-auto max-w-md">
        <PageHeader icon={UserRound} title="My Dashboard" subtitle="Sign in with your referral code to see your points, badges and referrals." />
        <div className="card space-y-4 p-6">
          <SignInByCode />
          <p className="text-center text-sm text-slate-400">
            New here?{' '}
            <Link to="/register" className="font-semibold text-red-400 hover:underline">
              Register as a donor
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

  const toggleAvailability = async (value) => {
    setSaving(true);
    try {
      setUser(await api.setAvailability(user.id, value));
      toast(value ? "You're available: SOS alerts are on." : 'Alerts paused. Toggle back on anytime.');
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
            {user.is_verified && <BadgeCheck className="h-6 w-6 text-sky-400" title="Verified" />}
          </h1>
          <p className="text-slate-400">
            {user.city} · {user.role === 'hospital' ? 'Hospital' : 'Donor'} · member since {new Date(user.created_at).toLocaleDateString()}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-sm">
            <span className={cx('font-bold', BADGES[user.badge]?.text)}>
              {info.icon} {user.badge}: {info.title}
            </span>
            {user.extra_badges.includes('Influencer') && <span className="font-bold text-fuchsia-300">🗣️ Community Champion</span>}
          </div>
        </div>
        <div className="flex flex-col items-end gap-3">
          <label className="flex items-center gap-3 text-sm">
            <span className={user.is_available ? 'text-emerald-400' : 'text-slate-400'}>{user.is_available ? 'Available to donate' : 'Not available'}</span>
            <Toggle checked={user.is_available} onChange={toggleAvailability} disabled={saving} />
          </label>
          <button onClick={signOut} className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white">
            <LogOut className="h-4 w-4" /> Sign out
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Droplet} label="BloodLink Points" value={`${user.points}`} hint="BLP" />
        <StatCard icon={History} label="Donations" value={user.total_donations} hint={user.last_donation_at ? `last ${timeAgo(user.last_donation_at)}` : 'none yet'} />
        <StatCard icon={Users} label="Referrals" value={user.referrals.total} hint={`${user.referrals.donated} donated`} accent="text-sky-400" />
        <StatCard icon={Gift} label="BLP from referrals" value={user.referrals.points_earned} accent="text-fuchsia-300" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="text-lg font-bold">Badge progress</h2>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span>
              {info.icon} {user.badge}
            </span>
            <span className="text-slate-400">{next ? `${next.min_points - user.points} BLP to ${next.icon} ${next.name}` : 'Max level reached! 💎'}</span>
          </div>
          <div className="mt-2 h-3 overflow-hidden rounded-full bg-slate-800">
            <div className="h-full rounded-full bg-gradient-to-r from-red-600 to-orange-400 transition-all" style={{ width: `${progress}%` }} />
          </div>

          <h2 className="mt-8 text-lg font-bold">Telegram</h2>
          {user.telegram_linked ? (
            <p className="mt-2 flex items-center gap-2 text-sm text-emerald-400">
              <CheckCircle2 className="h-4 w-4" /> Linked{user.telegram_username && ` as @${user.telegram_username}`}. You'll get instant SOS alerts.
            </p>
          ) : (
            <>
              <p className="mt-2 text-sm text-slate-400">Link Telegram to receive SOS alerts and donate with one tap.</p>
              <a href={user.telegram_link_url} target="_blank" rel="noreferrer" className="btn-primary mt-3 bg-sky-600 shadow-sky-900/40 hover:bg-sky-500">
                <Send className="h-4 w-4" /> Link Telegram
              </a>
            </>
          )}
        </div>

        <div className="card space-y-4 p-6">
          <h2 className="text-lg font-bold">Invite friends, earn vouchers</h2>
          <div className="rounded-xl bg-slate-800/60 p-4 text-center">
            <div className="text-xs text-slate-400">Your referral code (also your sign-in code)</div>
            <div className="font-mono text-2xl font-extrabold tracking-wider text-red-400">{user.referral_code}</div>
          </div>
          <CopyField label="Telegram link" value={user.referral_link} />
          <CopyField label="Web link" value={user.web_referral_link} />
          <div className="grid grid-cols-3 gap-2 text-center text-sm">
            {[
              ['Invited', user.referrals.total],
              ['Registered', user.referrals.registered],
              ['Donated', user.referrals.donated],
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
        <Panel title="Points history" rows={a?.points_log} empty="No activity yet.">
          {(l) => (
            <>
              <span className="text-slate-300">{l.reason}</span>
              <span className={cx('shrink-0 font-bold tabular-nums', l.amount >= 0 ? 'text-emerald-400' : 'text-red-400')}>
                {l.amount >= 0 ? '+' : ''}
                {l.amount}
              </span>
            </>
          )}
        </Panel>
        <Panel title="Donations" rows={a?.donations} empty="No donations yet. Check the live feed!">
          {(d) => (
            <>
              <span className="text-slate-300">
                {d.blood_group} · {d.hospital}, {d.city}
                <span className="block text-xs text-slate-500">
                  {timeAgo(d.created_at)}
                  {d.quick_response && ' · ⚡ quick response'}
                </span>
              </span>
              <span className="shrink-0 font-bold text-emerald-400">+{d.points_awarded}</span>
            </>
          )}
        </Panel>
        <Panel title="My vouchers & referrals" rows={[...(a?.vouchers || []), ...(a?.referrals || [])]} empty="Redeem rewards or invite friends.">
          {(v) =>
            v.voucher_code ? (
              <>
                <span className="text-slate-300">
                  🎁 {v.reward_name}
                  <span className="block text-xs text-slate-500">{timeAgo(v.created_at)}</span>
                </span>
                <code className="shrink-0 rounded bg-slate-800 px-2 py-0.5 text-sm text-red-300">{v.voucher_code}</code>
              </>
            ) : (
              <>
                <span className="text-slate-300">
                  🤝 {v.name} ({v.blood_group})<span className="block text-xs text-slate-500">{v.status}</span>
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
