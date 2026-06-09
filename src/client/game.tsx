import './index.css';

import { StrictMode, useState } from 'react';
import { createRoot } from 'react-dom/client';
import type { TrendWatchSearchParams } from '../shared/types';
import {
  DEFAULT_POST_LIMIT,
  DEFAULT_SCAN_LIMIT,
} from '../shared/types';
import { BackendStatus } from './components/BackendStatus';
import { DataSourceBanner } from './components/DataSourceBanner';
import { FilteredPostsPanel } from './components/FilteredPostsPanel';
import { KeywordFilterPanel } from './components/KeywordFilterPanel';
import { KeywordFrequencyChart } from './components/KeywordFrequencyChart';
import { ReportExportPanel } from './components/ReportExportPanel';
import { SearchPanel } from './components/SearchPanel';
import { TopKeywordsPanel } from './components/TopKeywordsPanel';
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
    discoverData,
    filterData,
    reportData,
    discovering,
    filtering,
    discoverError,
    filterError,
    discover,
    filterByKeyword,
  } = useTrendWatch();

  const [reporting, setReporting] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [filterKeyword, setFilterKeyword] = useState('');
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

  const baseParams = (): TrendWatchSearchParams => ({
    ...params,
    query: '',
    subreddit: params.subreddit.trim().replace(/^r\//i, '') || 'all',
  });

  const handleDiscover = () => {
    setReportExport(null);
    setFilterKeyword('');
    void discover(baseParams());
  };

  const handleFilter = () => {
    setReportExport(null);
    void filterByKeyword(baseParams(), filterKeyword);
  };

  const canCopyReport =
    reportData !== null && reportData.export_posts.length >= 5;

  const handleCopyReport = () => {
    if (!reportData) {
      return;
    }
    setReporting(true);
    setReportError(null);
    setReportExport(null);
    void (async () => {
      try {
        const payload = buildReportRequest(
          reportData.query,
          reportData.subreddit,
          reportData.export_posts
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
          onCollect={handleDiscover}
          collecting={discovering}
        />

        {discoverError ? (
          <p className="text-sm text-red-600 dark:text-red-400">{discoverError}</p>
        ) : null}
        {filterError ? (
          <p className="text-sm text-red-600 dark:text-red-400">{filterError}</p>
        ) : null}
        {reportError ? (
          <p className="text-sm text-red-600 dark:text-red-400">{reportError}</p>
        ) : null}

        {discoverData ? (
          <>
            <DataSourceBanner data={discoverData} />
            <TopKeywordsPanel
              keywords={discoverData.top_keywords}
              onKeywordSelect={setFilterKeyword}
              selectedKeyword={filterKeyword}
            />
            <KeywordFrequencyChart keywords={discoverData.top_keywords} />

            <KeywordFilterPanel
              keyword={filterKeyword}
              onKeywordChange={setFilterKeyword}
              onFilter={handleFilter}
              onCopyReport={handleCopyReport}
              reportUploadUrl={reportUploadUrl()}
              filtering={filtering}
              reporting={reporting}
              canFilter={discoverData !== null}
              canCopyReport={canCopyReport}
              {...(filterData
                ? {
                    filterQuery: filterData.query,
                    postsMatched: filterData.posts_matched,
                  }
                : {})}
            />

            {filterData ? (
              <>
                <DataSourceBanner data={filterData} />
                <FilteredPostsPanel
                  query={filterData.query}
                  posts={filterData.posts}
                />
              </>
            ) : null}
          </>
        ) : null}

        {reportExport ? (
          <ReportExportPanel
            uploadUrl={reportUploadUrl()}
            json={reportExport.json}
            copiedToClipboard={reportExport.copiedToClipboard}
          />
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
