import './index.css';

import { lazy, StrictMode, Suspense, useState } from 'react';
import { createRoot } from 'react-dom/client';
import type { TrendWatchSearchParams } from '../shared/types';
import {
  DEFAULT_POST_LIMIT,
  DEFAULT_SCAN_LIMIT,
} from '../shared/types';
import { BackendStatus } from './components/BackendStatus';
import { CrisisPanel } from './components/CrisisPanel';
import { DataSourceBanner } from './components/DataSourceBanner';
import { HighImpactPosts } from './components/HighImpactPosts';
import { InsightReport } from './components/InsightReport';
import { OverviewCards } from './components/OverviewCards';
import { ReportExportPanel } from './components/ReportExportPanel';
import { SearchPanel } from './components/SearchPanel';
import { TopKeywordsPanel } from './components/TopKeywordsPanel';
import { TopicCards } from './components/TopicCards';

const SentimentChart = lazy(() =>
  import('./components/SentimentChart').then((m) => ({ default: m.SentimentChart }))
);
const TrendTimeline = lazy(() =>
  import('./components/TrendTimeline').then((m) => ({ default: m.TrendTimeline }))
);
import {
  buildReportRequest,
  copyReportDataToClipboard,
  reportUploadUrl,
} from './lib/reportExport';
import { useBackendHealth } from './hooks/useBackendHealth';
import { useTrendWatch } from './hooks/useTrendWatch';

export const App = () => {
  const { health } = useBackendHealth();
  const {
    collectData,
    analyzeData,
    collecting,
    analysing,
    collectError,
    analyzeError,
    collect,
    analyze,
  } = useTrendWatch();

  const [reporting, setReporting] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [reportExport, setReportExport] = useState<{
    json: string;
    copiedToClipboard: boolean;
  } | null>(null);

  const [params, setParams] = useState<TrendWatchSearchParams>({
    query: '',
    subreddit: 'technology',
    scan_limit: DEFAULT_SCAN_LIMIT,
    limit: DEFAULT_POST_LIMIT,
  });

  const normalizedParams = (): TrendWatchSearchParams => ({
    ...params,
    query: params.query.trim(),
    subreddit: params.subreddit.trim().replace(/^r\//i, '') || 'all',
  });

  const handleCollect = () => {
    setReportExport(null);
    void collect(normalizedParams());
  };

  const handleAnalyze = () => {
    void analyze(normalizedParams());
  };

  const canAnalyze =
    collectData !== null &&
    (collectData.posts_matched > 0 || collectData.posts.length > 0);

  const canFullReport =
    collectData !== null &&
    collectData.export_posts.length >= 5;

  const handleCopyReport = () => {
    if (!collectData) {
      return;
    }
    setReporting(true);
    setReportError(null);
    setReportExport(null);
    void (async () => {
      try {
        const payload = buildReportRequest(
          collectData.query,
          collectData.subreddit,
          collectData.export_posts
        );
        const result = await copyReportDataToClipboard(payload);
        setReportExport(result);
      } catch (err) {
        setReportError(err instanceof Error ? err.message : 'Failed to copy report data');
      } finally {
        setReporting(false);
      }
    })();
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 px-4 py-6">
      <div className="max-w-4xl mx-auto space-y-4">
        <BackendStatus
          connected={health?.connected ?? false}
          message={health?.message ?? 'Checking…'}
          checkedAt={health?.checked_at ?? null}
        />

        <SearchPanel
          params={params}
          onChange={setParams}
          onCollect={handleCollect}
          onAnalyze={handleAnalyze}
          onCopyReport={handleCopyReport}
          reportUploadUrl={reportUploadUrl()}
          collecting={collecting}
          analysing={analysing}
          reporting={reporting}
          canAnalyze={canAnalyze}
          canCopyReport={canFullReport}
        />

        {collectError ? (
          <p className="text-sm text-red-600 dark:text-red-400">{collectError}</p>
        ) : null}
        {analyzeError ? (
          <p className="text-sm text-red-600 dark:text-red-400">{analyzeError}</p>
        ) : null}
        {reportError ? (
          <p className="text-sm text-red-600 dark:text-red-400">{reportError}</p>
        ) : null}
        {reportExport ? (
          <ReportExportPanel
            uploadUrl={reportUploadUrl()}
            json={reportExport.json}
            copiedToClipboard={reportExport.copiedToClipboard}
          />
        ) : null}

        {collectData ? (
          <>
            <DataSourceBanner data={collectData} />
            <TopKeywordsPanel keywords={collectData.top_keywords} />
          </>
        ) : null}

        {analyzeData ? (
          <div className="space-y-4">
            <OverviewCards summary={analyzeData.summary} />
            <Suspense
              fallback={
                <p className="text-sm text-gray-500 dark:text-gray-400">Loading charts…</p>
              }
            >
              <div className="grid gap-4 lg:grid-cols-2">
                <SentimentChart distribution={analyzeData.sentiment_distribution} />
                <CrisisPanel crisis={analyzeData.crisis} />
              </div>
              <TrendTimeline trends={analyzeData.trends} />
            </Suspense>
            <TopicCards topics={analyzeData.topics} />
            <HighImpactPosts posts={analyzeData.high_impact_posts} />
            <InsightReport
              briefing={analyzeData.briefing}
              techniques={analyzeData.techniques_used}
            />
          </div>
        ) : null}
      </div>
    </div>
  );
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
