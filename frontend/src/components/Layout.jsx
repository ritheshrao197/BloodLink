import { useState } from 'react';
import { Droplet, Gift, Menu, Search, Shield, Siren, Trophy, UserRound, X } from 'lucide-react';
import { Link, useRouter } from '../lib/router';
import { useSession } from '../lib/session';
import { cx } from '../lib/utils';

const NAV = [
  { to: '/', label: 'Live Feed', icon: Droplet },
  { to: '/sos', label: 'SOS', icon: Siren },
  { to: '/donors', label: 'Donors', icon: Search },
  { to: '/leaderboard', label: 'Leaderboard', icon: Trophy },
  { to: '/rewards', label: 'Rewards', icon: Gift },
  { to: '/admin', label: 'Admin', icon: Shield },
];

export default function Layout({ children }) {
  const { path } = useRouter();
  const { user } = useSession();
  const [open, setOpen] = useState(false);

  const navLink = ({ to, label, icon: Icon }) => {
    const active = to === '/' ? path === '/' : path.startsWith(to);
    return (
      <Link
        key={to}
        to={to}
        onClick={() => setOpen(false)}
        className={cx(
          'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition',
          active ? 'bg-red-600/15 text-red-400' : 'text-slate-300 hover:bg-slate-800 hover:text-white',
          to === '/sos' && !active && 'text-red-400',
        )}
      >
        <Icon className="h-4 w-4" />
        {label}
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_rgba(220,38,38,0.12),_transparent_55%)]">
      <header className="sticky top-0 z-40 border-b border-red-500/20 bg-slate-950/85 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4">
          <Link to="/" className="flex items-center gap-2 text-xl font-extrabold tracking-tight">
            <span className="text-2xl">🩸</span>
            <span className="text-red-500">BLOOD</span>
            <span className="-ml-2">LINK</span>
          </Link>
          <nav className="hidden items-center gap-1 lg:flex">{NAV.map(navLink)}</nav>
          <div className="flex items-center gap-2">
            {user ? (
              <Link to="/profile" className="flex items-center gap-2 rounded-full border border-slate-700 py-1 pl-1 pr-3 text-sm hover:border-red-500/60">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-red-600 text-xs font-bold">
                  {user.blood_group}
                </span>
                <span className="hidden font-medium sm:inline">{user.name.split(' ')[0]}</span>
                <span className="font-bold text-red-400">{user.points} BLP</span>
              </Link>
            ) : (
              <Link to="/register" className="btn-primary px-3 py-2 text-sm">
                <UserRound className="h-4 w-4" /> Become a Donor
              </Link>
            )}
            <button className="rounded-lg p-2 text-slate-300 hover:bg-slate-800 lg:hidden" onClick={() => setOpen(!open)} aria-label="Menu">
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
        {open && <nav className="grid gap-1 border-t border-slate-800 p-3 lg:hidden">{NAV.map(navLink)}</nav>}
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:py-10">{children}</main>

      <footer className="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500">
        <p className="font-semibold text-slate-400">Every Drop Counts. Every Second Matters.</p>
        <p className="mt-1">
          ⚠️ Compatibility shown is preliminary (rule-based ABO/Rh). Medical eligibility is confirmed by hospitals. Vouchers are demo-only.
        </p>
      </footer>
    </div>
  );
}
