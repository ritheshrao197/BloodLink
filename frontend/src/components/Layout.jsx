import { useState } from 'react';
import { Award, Droplet, Gift, Menu, Monitor, Moon, Search, Shield, Siren, Sun, Trophy, UserRound, X } from 'lucide-react';
import { Link, useRouter } from '../lib/router';
import { useSession } from '../lib/session';
import { useTheme } from '../lib/theme';
import { cx } from '../lib/utils';

const NAV = [
  { to: '/', label: 'Live Feed', icon: Droplet },
  { to: '/donors', label: 'Find Donors', icon: Search },
  { to: '/leaderboard', label: 'Leaderboard', icon: Trophy },
  { to: '/achievements', label: 'Achievements', icon: Award },
  { to: '/rewards', label: 'Rewards', icon: Gift },
  { to: '/admin', label: 'Admin', icon: Shield },
];

const THEME = {
  light: { icon: Sun, label: 'Light theme' },
  dark: { icon: Moon, label: 'Dark theme' },
  system: { icon: Monitor, label: 'System theme' },
};

export default function Layout({ children }) {
  const { path } = useRouter();
  const { user } = useSession();
  const { mode, cycle } = useTheme();
  const [open, setOpen] = useState(false);
  const ThemeIcon = THEME[mode].icon;

  const navLink = ({ to, label, icon: Icon }) => {
    const active = to === '/' ? path === '/' : path.startsWith(to);
    return (
      <Link
        key={to}
        to={to}
        onClick={() => setOpen(false)}
        aria-current={active ? 'page' : undefined}
        className={cx(
          'flex min-h-10 items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition',
          active ? 'bg-blood-600/10 text-blood-600 dark:bg-blood-500/15 dark:text-blood-400' : 'text-slate-300 hover:bg-slate-800 hover:text-slate-50',
        )}
      >
        <Icon className="h-4 w-4" />
        {label}
      </Link>
    );
  };

  return (
    <div className="flex min-h-screen flex-col bg-[radial-gradient(ellipse_at_top,_rgba(220,38,38,0.08),_transparent_55%)] dark:bg-[radial-gradient(ellipse_at_top,_rgba(220,38,38,0.14),_transparent_55%)]">
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-blood-600 focus:px-4 focus:py-2 focus:text-white">
        Skip to content
      </a>
      <header className="glass-nav">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4">
          <Link to="/" className="flex items-center gap-2 text-xl font-black tracking-tight" aria-label="BLOODLINK home">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blood-500 to-blood-700 shadow-lg shadow-blood-600/30">
              <Droplet className="h-5 w-5 fill-white text-white" />
            </span>
            <span>
              <span className="text-gradient-blood">BLOOD</span>LINK
            </span>
          </Link>
          <nav className="hidden items-center gap-0.5 xl:flex" aria-label="Main">
            {NAV.map(navLink)}
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/sos" className={cx('btn-sos hidden min-h-10 px-4 py-2 text-sm sm:inline-flex', path === '/sos' && 'animate-none')}>
              <Siren className="h-4 w-4" /> SOS
            </Link>
            <button
              onClick={cycle}
              className="flex h-10 w-10 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-800 hover:text-slate-50"
              aria-label={`${THEME[mode].label}. Click to change`}
              title={THEME[mode].label}
            >
              <ThemeIcon className="h-5 w-5" />
            </button>
            {user ? (
              <Link
                to="/profile"
                className="flex min-h-10 items-center gap-2 rounded-full border border-slate-800 bg-white py-1 pl-1 pr-3 text-sm transition hover:border-blood-400 dark:border-slate-700 dark:bg-slate-900"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blood-500 to-blood-700 text-xs font-bold text-white">
                  {user.blood_group}
                </span>
                <span className="hidden font-medium md:inline">{user.name.split(' ')[0]}</span>
                <span className="font-bold text-blood-600 dark:text-blood-400">{user.points} BLP</span>
              </Link>
            ) : (
              <Link to="/register" className="btn-primary hidden min-h-10 px-4 py-2 text-sm md:inline-flex">
                <UserRound className="h-4 w-4" /> Become a Donor
              </Link>
            )}
            <button
              className="flex h-10 w-10 items-center justify-center rounded-lg text-slate-300 hover:bg-slate-800 xl:hidden"
              onClick={() => setOpen(!open)}
              aria-label={open ? 'Close menu' : 'Open menu'}
              aria-expanded={open}
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
        {open && (
          <nav className="grid gap-1 border-t border-slate-800 p-3 xl:hidden" aria-label="Mobile">
            <Link to="/sos" onClick={() => setOpen(false)} className="btn-sos mb-2 w-full animate-none sm:hidden">
              <Siren className="h-4 w-4" /> Request Emergency SOS
            </Link>
            {NAV.map(navLink)}
            {!user && navLink({ to: '/register', label: 'Become a Donor', icon: UserRound })}
          </nav>
        )}
      </header>

      <main id="main" className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:py-10">
        {children}
      </main>

      <footer className="border-t border-slate-800/80 py-10 text-center text-xs text-slate-500">
        <p className="text-sm font-semibold text-slate-400">Every drop counts. Every second matters.</p>
        <p className="mx-auto mt-2 max-w-2xl px-4">
          Compatibility shown is preliminary (rule-based ABO/Rh). Medical eligibility is always confirmed by hospital staff. Vouchers are
          demo-only.
        </p>
      </footer>
    </div>
  );
}
