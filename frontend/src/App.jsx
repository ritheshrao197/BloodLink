import { RouterProvider, useRouter, Link } from './lib/router';
import { SessionProvider } from './lib/session';
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

const ROUTES = {
  '/': Home,
  '/sos': SOS,
  '/donors': Donors,
  '/register': Register,
  '/leaderboard': Leaderboard,
  '/rewards': Rewards,
  '/profile': Profile,
  '/admin': Admin,
};

function NotFound() {
  return (
    <div className="py-24 text-center">
      <div className="text-6xl">🩸</div>
      <h1 className="mt-4 text-3xl font-bold">Page not found</h1>
      <Link to="/" className="btn-primary mt-6">
        Back to live feed
      </Link>
    </div>
  );
}

function Routes() {
  const { path } = useRouter();
  const Page = ROUTES[path.replace(/\/+$/, '') || '/'] || NotFound;
  return <Page key={path} />;
}

export default function App() {
  return (
    <RouterProvider>
      <SessionProvider>
        <ToastProvider>
          <Layout>
            <Routes />
          </Layout>
        </ToastProvider>
      </SessionProvider>
    </RouterProvider>
  );
}
