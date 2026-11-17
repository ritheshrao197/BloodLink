import { useCallback, useEffect, useRef, useState } from 'react';

/** Fetch now, then every `ms` while the tab is visible. Returns { data, error, loading, reload }. */
export function usePoll(fetcher, ms = 5000, key = '') {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const fetchRef = useRef(fetcher);
  fetchRef.current = fetcher;

  const reload = useCallback(async () => {
    try {
      const data = await fetchRef.current();
      setState({ data, error: null, loading: false });
    } catch (error) {
      setState((s) => ({ ...s, error, loading: false }));
    }
  }, []);

  useEffect(() => {
    setState((s) => ({ ...s, loading: true }));
    reload();
    if (!ms) return undefined;
    const t = setInterval(() => {
      if (!document.hidden) reload();
    }, ms);
    return () => clearInterval(t);
  }, [reload, ms, key]);

  return { ...state, reload };
}
