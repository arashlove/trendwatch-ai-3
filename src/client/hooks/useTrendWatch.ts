import { useCallback, useState } from 'react';
import type {
  AnalyzeResponse,
  CollectResponse,
  TrendWatchSearchParams,
} from '../../shared/types';

const toQueryString = (params: TrendWatchSearchParams): string =>
  new URLSearchParams({
    query: params.query,
    subreddit: params.subreddit,
    scan_limit: String(params.scan_limit),
    limit: String(params.limit),
  }).toString();

export const useTrendWatch = () => {
  const [collectData, setCollectData] = useState<CollectResponse | null>(null);
  const [analyzeData, setAnalyzeData] = useState<AnalyzeResponse | null>(null);
  const [collecting, setCollecting] = useState(false);
  const [analysing, setAnalysing] = useState(false);
  const [collectError, setCollectError] = useState<string | null>(null);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  const collect = useCallback(async (params: TrendWatchSearchParams) => {
    setCollecting(true);
    setCollectError(null);
    setAnalyzeData(null);
    setAnalyzeError(null);

    try {
      const res = await fetch(`/api/trendwatch/collect?${toQueryString(params)}`);
      const data = await res.json();
      if (!res.ok) {
        const message =
          typeof data.message === 'string' ? data.message : `HTTP ${res.status}`;
        throw new Error(message);
      }
      setCollectData(data);
      return data as CollectResponse;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Collect failed';
      setCollectError(message);
      setCollectData(null);
      throw err;
    } finally {
      setCollecting(false);
    }
  }, []);

  const analyze = useCallback(async (params: TrendWatchSearchParams) => {
    setAnalysing(true);
    setAnalyzeError(null);

    try {
      const res = await fetch(`/api/trendwatch/analyze?${toQueryString(params)}`);
      const data = await res.json();
      if (!res.ok) {
        const message =
          typeof data.message === 'string' ? data.message : `HTTP ${res.status}`;
        throw new Error(message);
      }
      setAnalyzeData(data);
      return data as AnalyzeResponse;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setAnalyzeError(message);
      setAnalyzeData(null);
      throw err;
    } finally {
      setAnalysing(false);
    }
  }, []);

  return {
    collectData,
    analyzeData,
    collecting,
    analysing,
    collectError,
    analyzeError,
    collect,
    analyze,
  };
};
