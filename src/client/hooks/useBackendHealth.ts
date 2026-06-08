import { useEffect, useState } from 'react';
import type { BackendHealthResponse } from '../../shared/types';

export const useBackendHealth = () => {
  const [health, setHealth] = useState<BackendHealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('/api/trendwatch/health');
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data: BackendHealthResponse = await res.json();
        setHealth(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Health check failed');
        setHealth(null);
      }
    };

    void check();
    const interval = setInterval(() => void check(), 30000);
    return () => clearInterval(interval);
  }, []);

  return { health, error };
};
