import { useLayoutEffect, useRef, useState } from 'react';
import { Award, ClipboardCheck, Package, Droplet, Gift, Languages, Menu, Monitor, Moon, Search, Shield, Siren, Sun, Tent, Trophy, UserRound, Users, X } from 'lucide-react';
import { api } from '../lib/api';
import { Link, useRouter } from '../lib/router';
import { useSession } from '../lib/session';
import { useTheme } from '../lib/theme';
import { cx } from '../lib/utils';
import { LANGUAGES, useI18n } from '../i18n';

const NAV = [
  { to: '/', key: 'feed', icon: Droplet },
  { to: '/donors', key: 'donors', icon: Search },
  { to: '/stock', key: 'stock', icon: Package },
  { to: '/leaderboard', key: 'leaderboard', icon: Trophy },
  { to: '/teams', key: 'teams', icon: Users },
  { to: '/camps', key: 'camps', icon: Tent },
  { to: '/achievements', key: 'achievements', icon: Award },
  { to: '/rewards', key: 'rewards', icon: Gift },
];

const THEME_ICON = { light: Sun, dark: Moon, system: Monitor };

/** Phone tab bar: the main sections within thumb reach, with SOS always one tap away in the middle. */
function BottomBar({ path }) {
  const { t } = useI18n();
  const tab = (to, key, Icon) => {
    const active = to === '/' ? path === '/' : path.startsWith(to);
    return (
      <Link
        to={to}
        aria-current={active ? 'page' : undefined}
        className={cx('flex min-w-0 flex-1 flex-col items-center gap-0.5 py-2 text-[11px] font-semibold', active ? 'text-brand-700 dark:text-brand-300' : 'text-slate-400')}
      >
        <Icon className="h-6 w-6" aria-hidden />
        <span className="max-w-full truncate px-1">{t(key)}</span>
      </Link>
    );
  };
  return (
    <nav
      aria-label={t('nav.main')}
      className="fixed inset-x-0 bottom-0 z-40 border-t border-slate-800 bg-white/95 backdrop-blur-xl lg:hidden dark:bg-slate-950/95"
      style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
    >
      <div className="mx-auto flex max-w-lg items-end">
        {tab('/', 'nav.feed', Droplet)}
        {tab('/camps', 'nav.camps', Tent)}
        <Link to="/sos" className="flex flex-1 flex-col items-center" aria-label={t('nav.sosLong')}>
          <span className={cx('-mt-6 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blood-500 to-blood-700 text-white shadow-md ring-4 ring-white dark:ring-slate-950', path !== '/sos' && 'animate-pulse-sos')}>
            <Siren className="h-7 w-7" />
          </span>
          <span className="pb-2 pt-0.5 text-[11px] font-extrabold text-blood-600 dark:text-blood-400">{t('nav.sos')}</span>
        </Link>
        {tab('/achievements', 'nav.achievements', Award)}
        {tab('/profile', 'nav.me', UserRound)}
      </div>
    </nav>
  );
}

function LanguagePicker() {
  const { lang, setLang, t } = useI18n();
  const { user, setUser } = useSession();
  const change = (code) => {
    setLang(code);
    // keep the account (and its Telegram messages) in the same language
    if (user && user.language !== code) api.setLanguage(user.id, code).then(setUser).catch(() => {});
  };
  return (
    <label className="relative flex h-10 items-center rounded-lg text-slate-400 transition focus-within:ring-4 focus-within:ring-brand-500/30 hover:bg-slate-800 hover:text-slate-50">
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
  const staff = !!user && (user.is_admin || ['hospital', 'blood_bank'].includes(user.role));
  // staff get the page in the menu, and as an icon in the header (the full nav has no room for a ninth link)
  const nav = staff ? [...NAV, { to: '/staff', key: 'staff', icon: ClipboardCheck }] : NAV;
  const { mode, cycle } = useTheme();
  const { t, lang } = useI18n();
  const [open, setOpen] = useState(false);
  const ThemeIcon = THEME_ICON[mode];
  const themeLabel = t(`nav.theme.${mode}`);

  // The header shows as much nav as fits: icon + label in a row, then icon over a small label, then the ☰ menu.
  // Measured rather than a fixed breakpoint, because the width depends on the language and on being signed in.
  const [navMode, setNavMode] = useState('menu'); // 'full' | 'stacked' | 'menu'
  const rowRef = useRef(null);
  const logoRef = useRef(null);
  const rightRef = useRef(null);
  const menuBtnRef = useRef(null);
  const fullRef = useRef(null);
  const compactRef = useRef(null);
  useLayoutEffect(() => {
    const measure = () => {
      const row = rowRef.current;
      if (!row || !fullRef.current) return;
      const s = getComputedStyle(row);
      const gap = parseFloat(s.columnGap) || 0;
      const inner = row.clientWidth - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
      const btn = menuBtnRef.current;
      const right = rightRef.current.offsetWidth - (btn && btn.offsetParent ? btn.offsetWidth + 6 : 0); // 6 = gap-1.5
      const avail = inner - logoRef.current.offsetWidth - right - 2 * gap;
      setNavMode(fullRef.current.offsetWidth <= avail ? 'full' : compactRef.current.offsetWidth <= avail ? 'stacked' : 'menu');
    };
    measure();
    const ro = new ResizeObserver(measure);
    [rowRef, logoRef, rightRef, fullRef, compactRef].forEach((r) => r.current && ro.observe(r.current));
    return () => ro.disconnect();
  }, []);

  // stacked = icon over a small label: every section stays named, in about half the width of the inline row
  const navLink = ({ to, key, icon: Icon }, stacked = false) => {
    const active = to === '/' ? path === '/' : path.startsWith(to);
    return (
      <Link
        key={to}
        to={to}
        onClick={() => setOpen(false)}
        aria-current={active ? 'page' : undefined}
        className={cx(
          'flex items-center whitespace-nowrap rounded-lg font-medium transition',
          stacked ? 'min-h-12 min-w-12 flex-col justify-center gap-1 px-2 py-1 text-[11px] leading-none' : 'min-h-10 gap-2 px-3 py-2 text-sm',
          active ? 'bg-brand-600/10 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300' : 'text-slate-300 hover:bg-slate-800 hover:text-slate-50',
        )}
      >
        <Icon className={cx('shrink-0', stacked ? 'h-5 w-5' : 'h-4 w-4')} aria-hidden />
        {t(`nav.${key}`)}
      </Link>
    );
  };

  return (
    <div className="flex min-h-screen flex-col bg-slate-950">
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-brand-700 focus:px-4 focus:py-2 focus:text-white">
        {t('nav.skip')}
      </a>
      <header className="glass-nav">
        {/* invisible copies of both nav styles, used only to measure how wide each one is */}
        <div aria-hidden className="pointer-events-none invisible absolute inset-x-0 top-0 -z-10 h-0 overflow-hidden">
          <div ref={fullRef} className="flex w-max items-center gap-0.5">{NAV.map((n) => navLink(n))}</div>
          <div ref={compactRef} className="flex w-max items-center gap-0.5">{NAV.map((n) => navLink(n, true))}</div>
        </div>
        <div ref={rowRef} className="mx-auto flex h-16 max-w-screen-2xl items-center justify-between gap-3 px-4">
          <span ref={logoRef} className="shrink-0">
            <Link to="/" className="flex shrink-0 items-center gap-2 text-xl font-black tracking-tight" aria-label={t('nav.home')}>
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blood-600 shadow-sm">
                <Droplet className="h-5 w-5 fill-white text-white" />
              </span>
              <span className="hidden sm:inline">
                <span className="text-brand-700 dark:text-brand-300">BLOOD</span>LINK
              </span>
            </Link>
          </span>
          {navMode !== 'menu' && (
            <nav className="flex items-center gap-0.5" aria-label={t('nav.main')}>
              {NAV.map((n) => navLink(n, navMode === 'stacked'))}
            </nav>
          )}
          <div ref={rightRef} className="flex shrink-0 items-center gap-1.5">
            <Link to="/sos" className={cx('btn-sos hidden min-h-10 px-4 py-2 text-sm sm:inline-flex', path === '/sos' && 'animate-none')}>
              <Siren className="h-4 w-4" /> {t('nav.sos')}
            </Link>
            {staff && (
              <Link
                to="/staff"
                aria-label={t('nav.staff')}
                title={t('nav.staff')}
                aria-current={path.startsWith('/staff') ? 'page' : undefined}
                className={cx(
                  'flex h-10 w-10 items-center justify-center rounded-lg transition',
                  path.startsWith('/staff') ? 'bg-brand-600/10 text-brand-700 dark:text-brand-300' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-50',
                )}
              >
                <ClipboardCheck className="h-5 w-5" />
              </Link>
            )}
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
                className="flex min-h-10 items-center gap-2 rounded-full border border-slate-800 bg-white p-1 text-sm min-[400px]:pr-3 transition hover:border-brand-400 dark:border-slate-700 dark:bg-slate-900"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white">
                  {user.blood_group}
                </span>
                <span className="hidden font-medium 2xl:inline">{user.name.split(' ')[0]}</span>
                <span className="hidden whitespace-nowrap font-bold text-brand-700 min-[400px]:inline dark:text-brand-300">{user.points} BLP</span>
              </Link>
            ) : (
              <Link to="/register" className="btn-primary hidden min-h-10 px-4 py-2 text-sm lg:inline-flex">
                <UserRound className="h-4 w-4" /> {t('nav.becomeDonor')}
              </Link>
            )}
            <button
              ref={menuBtnRef}
              className={cx('h-10 w-10 items-center justify-center rounded-lg text-slate-300 hover:bg-slate-800', navMode === 'menu' ? 'flex' : 'hidden')}
              onClick={() => setOpen(!open)}
              aria-label={open ? t('nav.closeMenu') : t('nav.openMenu')}
              aria-expanded={open}
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
        {open && navMode === 'menu' && (
          <nav className="mx-auto grid max-w-screen-2xl gap-1 border-t border-slate-800 p-3 sm:grid-cols-2" aria-label={t('nav.main')}>
            <Link to="/sos" onClick={() => setOpen(false)} className="btn-sos mb-2 w-full animate-none sm:col-span-2 sm:hidden">
              <Siren className="h-4 w-4" /> {t('nav.sosLong')}
            </Link>
            {nav.map((n) => navLink(n))}
            {!user && navLink({ to: '/register', key: 'becomeDonor', icon: UserRound })}
          </nav>
        )}
      </header>

      <main id="main" className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:py-10">
        {children}
      </main>

      <BottomBar path={path} />

      <footer className="border-t border-slate-800/80 pb-28 pt-10 text-center text-xs text-slate-500 lg:pb-10">
        <p className="text-sm font-semibold text-slate-400">{t('footer.tagline')}</p>
        <p className="mx-auto mt-2 max-w-2xl px-4">{t('footer.disclaimer')}</p>
        <Link to="/admin" className="mt-3 inline-flex items-center gap-1.5 text-slate-500 hover:text-slate-300">
          <Shield className="h-3.5 w-3.5" /> {t('nav.admin')}
        </Link>
      </footer>
    </div>
  );
}
