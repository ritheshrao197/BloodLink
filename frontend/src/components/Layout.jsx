import { useState } from 'react';
import { Award, Droplet, Gift, Languages, Menu, Monitor, Moon, Search, Shield, Siren, Sun, Trophy, UserRound, X } from 'lucide-react';
import { api } from '../lib/api';
import { Link, useRouter } from '../lib/router';
import { useSession } from '../lib/session';
import { useTheme } from '../lib/theme';
import { cx } from '../lib/utils';
import { LANGUAGES, useI18n } from '../i18n';

const NAV = [
  { to: '/', key: 'feed', icon: Droplet },
  { to: '/donors', key: 'donors', icon: Search },
  { to: '/leaderboard', key: 'leaderboard', icon: Trophy },
  { to: '/achievements', key: 'achievements', icon: Award },
  { to: '/rewards', key: 'rewards', icon: Gift },
  { to: '/admin', key: 'admin', icon: Shield },
];

const THEME_ICON = { light: Sun, dark: Moon, system: Monitor };

function LanguagePicker() {
  const { lang, setLang, t } = useI18n();
  const { user, setUser } = useSession();
  const change = (code) => {
    setLang(code);
    // keep the account (and its Telegram messages) in the same language
    if (user && user.language !== code) api.setLanguage(user.id, code).then(setUser).catch(() => {});
  };
  return (
    <label className="relative flex h-10 items-center rounded-lg text-slate-400 transition focus-within:ring-4 focus-within:ring-blood-500/30 hover:bg-slate-800 hover:text-slate-50">
      <Languages className="pointer-events-none absolute left-2.5 h-4 w-4" aria-hidden />
      <span className="sr-only">{t('common.language')}</span>
      <select
        value={lang}
        onChange={(e) => change(e.target.value)}
        className="h-10 cursor-pointer appearance-none rounded-lg bg-transparent pl-8 pr-2 text-sm font-semibold text-slate-300 outline-none"
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code} className="bg-white text-slate-50 dark:bg-slate-900">
            {l.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function Layout({ children }) {
  const { path } = useRouter();
  const { user } = useSession();
  const { mode, cycle } = useTheme();
  const { t, lang } = useI18n();
  const [open, setOpen] = useState(false);
  const wide = lang === 'en'; // translated labels are longer: collapse the nav earlier
  const ThemeIcon = THEME_ICON[mode];
  const themeLabel = t(`nav.theme.${mode}`);

  const navLink = ({ to, key, icon: Icon }) => {
    const active = to === '/' ? path === '/' : path.startsWith(to);
    return (
      <Link
        key={to}
        to={to}
        onClick={() => setOpen(false)}
        aria-current={active ? 'page' : undefined}
        className={cx(
          'flex min-h-10 items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition',
          active ? 'bg-blood-600/10 text-blood-600 dark:bg-blood-500/15 dark:text-blood-400' : 'text-slate-300 hover:bg-slate-800 hover:text-slate-50',
        )}
      >
        <Icon className="h-4 w-4 shrink-0" />
        {t(`nav.${key}`)}
      </Link>
    );
  };

  return (
    <div className="flex min-h-screen flex-col bg-[radial-gradient(ellipse_at_top,_rgba(220,38,38,0.08),_transparent_55%)] dark:bg-[radial-gradient(ellipse_at_top,_rgba(220,38,38,0.14),_transparent_55%)]">
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-blood-600 focus:px-4 focus:py-2 focus:text-white">
        {t('nav.skip')}
      </a>
      <header className="glass-nav">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4">
          <Link to="/" className="flex shrink-0 items-center gap-2 text-xl font-black tracking-tight" aria-label={t('nav.home')}>
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blood-500 to-blood-700 shadow-lg shadow-blood-600/30">
              <Droplet className="h-5 w-5 fill-white text-white" />
            </span>
            <span className="hidden sm:inline">
              <span className="text-gradient-blood">BLOOD</span>LINK
            </span>
          </Link>
          <nav className={cx('hidden items-center gap-0.5', wide ? 'xl:flex' : '2xl:flex')} aria-label={t('nav.main')}>
            {NAV.map(navLink)}
          </nav>
          <div className="flex items-center gap-1.5">
            <Link to="/sos" className={cx('btn-sos hidden min-h-10 px-4 py-2 text-sm sm:inline-flex', path === '/sos' && 'animate-none')}>
              <Siren className="h-4 w-4" /> {t('nav.sos')}
            </Link>
            <LanguagePicker />
            <button
              onClick={cycle}
              className="flex h-10 w-10 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-800 hover:text-slate-50"
              aria-label={t('nav.theme.change', { mode: themeLabel })}
              title={themeLabel}
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
              <Link to="/register" className="btn-primary hidden min-h-10 px-4 py-2 text-sm lg:inline-flex">
                <UserRound className="h-4 w-4" /> {t('nav.becomeDonor')}
              </Link>
            )}
            <button
              className={cx('flex h-10 w-10 items-center justify-center rounded-lg text-slate-300 hover:bg-slate-800', wide ? 'xl:hidden' : '2xl:hidden')}
              onClick={() => setOpen(!open)}
              aria-label={open ? t('nav.closeMenu') : t('nav.openMenu')}
              aria-expanded={open}
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
        {open && (
          <nav className={cx('grid gap-1 border-t border-slate-800 p-3 sm:grid-cols-2', wide ? 'xl:hidden' : '2xl:hidden')} aria-label={t('nav.main')}>
            <Link to="/sos" onClick={() => setOpen(false)} className="btn-sos mb-2 w-full animate-none sm:col-span-2 sm:hidden">
              <Siren className="h-4 w-4" /> {t('nav.sosLong')}
            </Link>
            {NAV.map(navLink)}
            {!user && navLink({ to: '/register', key: 'becomeDonor', icon: UserRound })}
          </nav>
        )}
      </header>

      <main id="main" className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:py-10">
        {children}
      </main>

      <footer className="border-t border-slate-800/80 py-10 text-center text-xs text-slate-500">
        <p className="text-sm font-semibold text-slate-400">{t('footer.tagline')}</p>
        <p className="mx-auto mt-2 max-w-2xl px-4">{t('footer.disclaimer')}</p>
      </footer>
    </div>
  );
}
