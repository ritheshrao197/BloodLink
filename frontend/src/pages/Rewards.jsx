import { useState } from 'react';
import { Coffee, Film, Gift, Shirt, ShoppingBag, Ticket } from 'lucide-react';
import { api } from '../lib/api';
import { Link } from '../lib/router';
import { useSession } from '../lib/session';
import { usePoll } from '../lib/usePoll';
import { cx } from '../lib/utils';
import { useToast } from '../components/Toast';
import { CopyField, ErrorBox, Loading, Modal, PageHeader, Spinner } from '../components/ui';
import SignInByCode from '../components/SignInByCode';

const ICONS = { coffee: Coffee, film: Film, 'shopping-bag': ShoppingBag, shirt: Shirt };

export default function Rewards() {
  const { user, refresh } = useSession();
  const toast = useToast();
  const catalog = usePoll(() => api.rewards(), 0);
  const [busyId, setBusyId] = useState(null);
  const [voucher, setVoucher] = useState(null);

  const redeem = async (r) => {
    setBusyId(r.id);
    try {
      const res = await api.redeem(r.id, user.id);
      setVoucher(res);
      refresh();
    } catch (e) {
      toast(e.message, 'error');
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div>
      <PageHeader icon={Gift} title="Rewards Store" subtitle="Turn your BloodLink Points into real-world thank-yous. (Demo vouchers for the hackathon prototype.)">
        {user && (
          <div className="card px-5 py-3 text-right">
            <div className="text-xs text-slate-400">Your balance</div>
            <div className="text-2xl font-extrabold text-red-400">{user.points} BLP</div>
          </div>
        )}
      </PageHeader>

      {!user && (
        <div className="card mb-6 flex flex-wrap items-center justify-between gap-4 p-5">
          <p className="text-slate-300">Sign in with your referral code to redeem, or register to earn your first 50 BLP.</p>
          <div className="flex flex-wrap items-start gap-3">
            <SignInByCode />
            <Link to="/register" className="btn-primary">
              Register
            </Link>
          </div>
        </div>
      )}

      <ErrorBox error={catalog.error} />
      {catalog.loading ? (
        <Loading />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {catalog.data?.map((r) => {
            const Icon = ICONS[r.icon] || Ticket;
            const affordable = user && user.points >= r.cost;
            const pct = user ? Math.min(100, Math.round((user.points / r.cost) * 100)) : 0;
            return (
              <div key={r.id} className={cx('card flex flex-col p-6', affordable && 'border-red-500/40')}>
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-600/15">
                  <Icon className="h-7 w-7 text-red-400" />
                </div>
                <h3 className="mt-4 text-lg font-bold">{r.name}</h3>
                <p className="mt-1 flex-1 text-sm text-slate-400">{r.description}</p>
                <div className="mt-4 text-2xl font-extrabold">
                  {r.cost} <span className="text-sm font-semibold text-slate-400">BLP</span>
                </div>
                {user && (
                  <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-800">
                    <div className="h-full rounded-full bg-red-500" style={{ width: `${pct}%` }} />
                  </div>
                )}
                <button className="btn-primary mt-4" disabled={!affordable || busyId != null} onClick={() => redeem(r)}>
                  {busyId === r.id ? <Spinner /> : <Gift className="h-4 w-4" />}
                  {!user ? 'Sign in to redeem' : affordable ? 'Redeem' : `Need ${r.cost - user.points} more`}
                </button>
              </div>
            );
          })}
        </div>
      )}

      <div className="card mt-8 p-6">
        <h2 className="text-lg font-bold">How to earn BLP</h2>
        <div className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
          {[
            ['Register', '+50'],
            ['Successful donation', '+100'],
            ['Quick response (< 5 min)', '+20'],
            ['Friend registers with your code', '+50'],
            ['Friend makes first donation', '+200 + voucher'],
            ['Streak: donate again after 3 months', '+50'],
          ].map(([a, p]) => (
            <div key={a} className="flex items-center justify-between rounded-lg bg-slate-800/50 px-4 py-3">
              <span className="text-slate-300">{a}</span>
              <span className="font-bold text-red-400">{p}</span>
            </div>
          ))}
        </div>
      </div>

      <Modal open={!!voucher} onClose={() => setVoucher(null)} title="🎁 Reward redeemed!">
        {voucher && (
          <div className="space-y-4 text-center">
            <p className="text-slate-300">{voucher.reward}</p>
            <div className="rounded-xl border-2 border-dashed border-red-500/50 bg-slate-800/60 p-5 font-mono text-3xl font-extrabold tracking-widest text-red-400">
              {voucher.voucher_code}
            </div>
            <CopyField value={voucher.voucher_code} />
            <p className="text-sm text-slate-400">
              {voucher.points_remaining} BLP remaining. The code was also sent to your Telegram if it's linked. Demo voucher, not redeemable.
            </p>
            <button className="btn-primary w-full" onClick={() => setVoucher(null)}>
              Awesome
            </button>
          </div>
        )}
      </Modal>
    </div>
  );
}
