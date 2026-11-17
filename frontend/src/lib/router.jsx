import { createContext, useContext, useEffect, useState } from 'react';

const RouterContext = createContext(null);

const current = () => ({ path: window.location.pathname, search: window.location.search });

export function RouterProvider({ children }) {
  const [location, setLocation] = useState(current);

  useEffect(() => {
    const onPop = () => setLocation(current());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const navigate = (to) => {
    window.history.pushState({}, '', to);
    setLocation(current());
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return <RouterContext.Provider value={{ ...location, navigate }}>{children}</RouterContext.Provider>;
}

export const useRouter = () => useContext(RouterContext);

export function Link({ to, className, children, ...rest }) {
  const { navigate } = useRouter();
  return (
    <a
      href={to}
      className={className}
      onClick={(e) => {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
        e.preventDefault();
        navigate(to);
      }}
      {...rest}
    >
      {children}
    </a>
  );
}
