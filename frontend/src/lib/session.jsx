import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api, hasToken, setToken } from './api';

const SessionContext = createContext(null);

/** The signed-in user, backed by a session token (Telegram login, registration, demo code or admin password). */
export function SessionProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(!hasToken());
  const [config, setConfig] = useState(null);

  useEffect(() => {
    api.config().then(setConfig).catch(() => {});
    try {
      localStorage.removeItem('bloodlink_user_id'); // pre-login builds stored only an id: no longer trusted
    } catch {
      /* ignore */
    }
  }, []);

  const refresh = useCallback(async () => {
    if (!hasToken()) {
      setUser(null);
      setReady(true);
      return null;
    }
    try {
      const u = await api.auth.me();
      setUser(u);
      return u;
    } catch (e) {
      if (e.status === 401) {
        setToken(null);
        setUser(null);
      }
      return null;
    } finally {
      setReady(true);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const signIn = (u, token) => {
    if (token) setToken(token);
    setUser(u);
  };
  const signOut = () => {
    api.auth.logout().catch(() => {});
    setToken(null);
    setUser(null);
  };

  return <SessionContext.Provider value={{ user, setUser, refresh, signIn, signOut, config, ready }}>{children}</SessionContext.Provider>;
}

export const useSession = () => useContext(SessionContext);
