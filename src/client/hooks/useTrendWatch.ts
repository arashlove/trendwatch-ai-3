import { useCallback, useState } from 'react';
import type { CollectResponse, TrendWatchSearchParams } from '../../shared/types';

const toQueryString = (params: TrendWatchSearchParams): string =>
  new URLSearchParams({
    query: params.query,
    subreddit: params.subreddit,
    scan_limit: String(params.scan_limit),
    limit: String(params.limit),
  }).toString();

const fetchCollect = async (params: TrendWatchSearchParams): Promise<CollectResponse> => {
  const res = await fetch(`/api/trendwatch/collect?${toQueryString(params)}`);
  const data = await res.json();
  if (!res.ok) {
    const message = typeof data.message === 'string' ? data.message : `HTTP ${res.status}`;
    throw new Error(message);
  }
  return data as CollectResponse;
};

export const useTrendWatch = () => {
  const [discoverData, setDiscoverData] = useState<CollectResponse | null>(null);
  const [filterData, setFilterData] = useState<CollectResponse | null>(null);
  const [discovering, setDiscovering] = useState(false);
  const [filtering, setFiltering] = useState(false);
  const [discoverError, setDiscoverError] = useState<string | null>(null);
  const [filterError, setFilterError] = useState<string | null>(null);

  const discover = useCallback(async (params: TrendWatchSearchParams) => {
    setDiscovering(true);
    setDiscoverError(null);
    setFilterData(null);
    setFilterError(null);

    try {
      const data = await fetchCollect({ ...params, query: '' });
      setDiscoverData(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Collect failed';
      setDiscoverError(message);
      setDiscoverData(null);
      throw err;
    } finally {
      setDiscovering(false);
    }
  }, []);

  const filterByKeyword = useCallback(
    async (params: TrendWatchSearchParams, keyword: string) => {
      const trimmed = keyword.trim();
      if (!trimmed) {
        throw new Error('Enter a keyword to filter');
      }

      setFiltering(true);
      setFilterError(null);

      try {
        const data = await fetchCollect({ ...params, query: trimmed });
        setFilterData(data);
        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Filter failed';
        setFilterError(message);
        setFilterData(null);
        throw err;
      } finally {
        setFiltering(false);
      }
    },
    []
  );

  const reportData = filterData ?? discoverData;

  return {
    discoverData,
    filterData,
    reportData,
    discovering,
    filtering,
    discoverError,
    filterError,
    discover,
    filterByKeyword,
  };
};
