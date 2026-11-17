import { useState } from 'react';
import { Activity, Droplet, HeartHandshake, Radio, Send, Siren, Timer, Users } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { BLOOD_GROUPS, canDonate, cx } from '../lib/utils';
import RequestCard from '../components/RequestCard';
import DonateModal from '../components/DonateModal';
import { Empty, ErrorBox, Loading, StatCard } from '../components/ui';

export default function Home() {
  const { user, config } = useSession();
  const [filter, setFilter] = useState('All');
  const [respondTo, setRespondTo] = useState(null);
  const feed = usePoll(() => api.requests('Active'), 4000);
  const stats = usePoll(() => api.admin.stats(), 10000);

  const requests = (feed.data || []).filter((r) =>
    filter === 'All' ? true : filter === 'Mine' ? user && canDonate(user.blood_group, r.blood_group) : r.blood_group === filter,
  );
  const t = stats.data?.totals;
  const bot = config?.bot_username || 'BloodLinkBot';

  return (
    <div className="space-y-12">
      <section className="grid items-center gap-10 lg:grid-cols-[1.2fr_1fr]">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-300">
            <Radio className="h-3.5 w-3.5" /> Live emergency network
          </span>
          <h1 className="mt-4 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">
            Request blood as easily as <span className="text-red-500">sending a message.</span>
          </h1>
          <p className="mt-4 max-w-xl text-lg text-slate-400">
            BLOODLINK matches patients with compatible donors in seconds using ABO/Rh rules, alerts them instantly on Telegram, and rewards
            every hero who shows up.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/sos" className="btn-primary px-5 py-3 text-base">
              <Siren className="h-5 w-5" /> Send SOS
            </Link>
            <a href={`https://t.me/${bot}`} target="_blank" rel="noreferrer" className="btn-ghost px-5 py-3 text-base">
              <Send className="h-5 w-5 text-sky-400" /> Open @{bot}
            </a>
            {!user && (
              <Link to="/register" className="btn-ghost px-5 py-3 text-base">
                <HeartHandshake className="h-5 w-5" /> Become a donor
              </Link>
            )}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <StatCard icon={Users} label="Registered donors" value={t?.donors} hint={t && `${t.available_donors} available now`} />
          <StatCard icon={Siren} label="Active SOS" value={t?.active_requests} accent="text-orange-400" />
          <StatCard icon={Droplet} label="Donations made" value={t?.donations} hint={t && `${t.fulfilled_requests} requests fulfilled`} />
          <StatCard
            icon={Timer}
            label="Avg. first response"
            value={stats.data?.avg_response_minutes != null ? `${stats.data.avg_response_minutes}m` : '—'}
            accent="text-emerald-400"
            hint="vs. 2–6 h on social media"
          />
        </div>
      </section>

      <section>
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <h2 className="flex items-center gap-2 text-2xl font-bold">
            <Activity className="h-6 w-6 text-red-500" /> Live Emergency Requests
            <span className="rounded-full bg-red-600 px-2 py-0.5 text-sm">{feed.data?.length ?? 0}</span>
          </h2>
          <div className="flex flex-wrap gap-1.5">
            {['All', ...(user ? ['Mine'] : []), ...BLOOD_GROUPS].map((g) => (
              <button
                key={g}
                onClick={() => setFilter(g)}
                className={cx(
                  'rounded-lg px-2.5 py-1 text-sm font-semibold transition',
                  filter === g ? 'bg-red-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700',
                )}
              >
                {g === 'Mine' ? 'I can help' : g}
              </button>
            ))}
          </div>
        </div>
        <ErrorBox error={feed.error} />
        {feed.loading && !feed.data ? (
          <Loading />
        ) : requests.length === 0 ? (
          <Empty icon={HeartHandshake} title="No active requests here">
            {filter === 'All' ? 'All emergencies are covered right now. 🎉' : 'Try another filter.'}
          </Empty>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {requests.map((r) => (
              <RequestCard key={r.id} request={r} onRespond={setRespondTo} />
            ))}
          </div>
        )}
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ['1. Send /sos', 'Pick a blood group, type the hospital — done in 3 taps on Telegram or one form here.', Siren],
          ['2. Instant match', 'Our ABO/Rh rules alert every compatible, available donor in the city.', Radio],
          ['3. One-tap donate', 'Donors tap “I Can Donate”, earn BLP and badges, and recruit friends.', HeartHandshake],
        ].map(([title, text, Icon]) => (
          <div key={title} className="card p-6">
            <Icon className="h-7 w-7 text-red-500" />
            <h3 className="mt-3 text-lg font-bold">{title}</h3>
            <p className="mt-1 text-sm text-slate-400">{text}</p>
          </div>
        ))}
      </section>

      <DonateModal
        request={respondTo}
        onClose={() => setRespondTo(null)}
        onDone={() => {
          feed.reload();
          stats.reload();
        }}
      />
    </div>
  );
}
