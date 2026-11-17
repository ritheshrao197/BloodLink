import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api } from './api';

const KEY = 'bloodlink_user_id';
const SessionContext = createContext(null);

function readId() {
  try {
    return Number(localStorage.getItem(KEY)) || null;
  } catch {
    return null;
  }
}
function writeId(id) {
  try {
    if (id) localStorage.setItem(KEY, String(id));
    else localStorage.removeItem(KEY);
  } catch {
    /* storage unavailable: session lasts for this tab only */
  }
}

/** No passwords in the hackathon build: the "session" is just the selected user id. */
export function SessionProvider({ children }) {
  const [userId, setUserId] = useState(readId);
  const [user, setUser] = useState(null);
  const [config, setConfig] = useState(null);

  useEffect(() => {
    api.config().then(setConfig).catch(() => {});
  }, []);

  const refresh = useCallback(async () => {
    if (!userId) {
      setUser(null);
      return null;
    }
    try {
      const u = await api.user(userId);
      setUser(u);
      return u;
    } catch (e) {
      if (/not found/i.test(e.message)) {
        writeId(null);
        setUserId(null);
        setUser(null);
      }
      return null;
    }
  }, [userId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const signIn = (u) => {
    writeId(u.id);
    setUserId(u.id);
    setUser(u);
  };
  const signOut = () => {
    writeId(null);
    setUserId(null);
    setUser(null);
  };

  return (
    <SessionContext.Provider value={{ user, setUser, refresh, signIn, signOut, config }}>
      {children}
    </SessionContext.Provider>
  );
}

export const useSession = () => useContext(SessionContext);
