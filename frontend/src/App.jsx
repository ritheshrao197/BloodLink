import { useEffect } from 'react';
import { RouterProvider, useRouter, Link } from './lib/router';
import { SessionProvider, useSession } from './lib/session';
import { I18nProvider, useI18n } from './i18n';
import { ToastProvider } from './components/Toast';
import Layout from './components/Layout';
import Home from './pages/Home';
import SOS from './pages/SOS';
import Donors from './pages/Donors';
import Register from './pages/Register';
import Leaderboard from './pages/Leaderboard';
import Rewards from './pages/Rewards';
import Profile from './pages/Profile';
import Admin from './pages/Admin';
import Achievements from './pages/Achievements';
import Teams from './pages/Teams';
import Camps from './pages/Camps';

const ROUTES = {
  '/': Home,
  '/sos': SOS,
  '/donors': Donors,
  '/register': Register,
  '/leaderboard': Leaderboard,
  '/achievements': Achievements,
  '/teams': Teams,
  '/camps': Camps,
  '/rewards': Rewards,
  '/profile': Profile,
  '/admin': Admin,
};

function NotFound() {
  const { t } = useI18n();
  return (
    <div className="py-24 text-center">
      <div className="text-6xl">🩸</div>
      <h1 className="mt-4 text-3xl font-bold">{t('notFound.title')}</h1>
      <Link to="/" className="btn-primary mt-6">
        {t('notFound.back')}
      </Link>
    </div>
  );
}

/** A signed-in user's saved language applies until they pick one on this device. */
function LanguageSync() {
  const { user } = useSession();
  const { lang, setLang, explicit } = useI18n();
  useEffect(() => {
    if (user?.language && !explicit && user.language !== lang) setLang(user.language, { remember: false });
  }, [user?.language, explicit]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
}

function Routes() {
  const { path } = useRouter();
  const Page = ROUTES[path.replace(/\/+$/, '') || '/'] || NotFound;
  return <Page key={path} />;
}

export default function App() {
  return (
    <I18nProvider>
      <RouterProvider>
        <SessionProvider>
          <LanguageSync />
          <ToastProvider>
            <Layout>
              <Routes />
            </Layout>
          </ToastProvider>
        </SessionProvider>
      </RouterProvider>
    </I18nProvider>
  );
}
