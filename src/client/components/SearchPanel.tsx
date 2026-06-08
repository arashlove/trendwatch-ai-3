import type { TrendWatchSearchParams } from '../../shared/types';
import {
  DEFAULT_POST_LIMIT,
  DEFAULT_SCAN_LIMIT,
  MAX_POST_LIMIT,
  MAX_SCAN_LIMIT,
  MIN_POST_LIMIT,
  MIN_SCAN_LIMIT,
} from '../../shared/types';

type SearchPanelProps = {
  params: TrendWatchSearchParams;
  onChange: (params: TrendWatchSearchParams) => void;
  onCollect: () => void;
  onAnalyze: () => void;
  onCopyReport?: () => void;
  reportUploadUrl?: string;
  collecting: boolean;
  analysing: boolean;
  reporting?: boolean;
  canAnalyze: boolean;
  canCopyReport?: boolean;
};

const inputClass =
  'rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 w-full';

const labelClass =
  'block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1';

const stepLabelClass =
  'text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400';

export const SearchPanel = ({
  params,
  onChange,
  onCollect,
  onAnalyze,
  onCopyReport,
  reportUploadUrl,
  collecting,
  analysing,
  reporting = false,
  canAnalyze,
  canCopyReport = false,
}: SearchPanelProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-4">
    <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-1">
      TrendWatch
    </h1>
    <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
      Step 1 collects keywords from live Reddit. Step 2 runs a lightweight in-app preview.
      Step 3 copies JSON for the full Python NLP report on your PC.
    </p>
    <div className="grid gap-4 sm:grid-cols-2">
      <div>
        <label className={labelClass} htmlFor="tw-query">
          Keyword
        </label>
        <input
          id="tw-query"
          className={inputClass}
          value={params.query}
          onChange={(e) => onChange({ ...params, query: e.target.value })}
          placeholder="Optional — leave blank for all posts"
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Filter posts before extracting keywords
        </p>
      </div>
      <div>
        <label className={labelClass} htmlFor="tw-subreddit">
          Subreddit
        </label>
        <input
          id="tw-subreddit"
          className={inputClass}
          value={params.subreddit}
          onChange={(e) => onChange({ ...params, subreddit: e.target.value })}
          placeholder="e.g. technology or all"
        />
      </div>
      <div>
        <label className={labelClass} htmlFor="tw-scan-limit">
          Scan limit
        </label>
        <input
          id="tw-scan-limit"
          className={inputClass}
          type="number"
          min={MIN_SCAN_LIMIT}
          max={MAX_SCAN_LIMIT}
          value={params.scan_limit}
          onChange={(e) =>
            onChange({ ...params, scan_limit: Number(e.target.value) || DEFAULT_SCAN_LIMIT })
          }
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Recent posts to fetch ({MIN_SCAN_LIMIT}–{MAX_SCAN_LIMIT})
        </p>
      </div>
      <div>
        <label className={labelClass} htmlFor="tw-post-limit">
          Post limit
        </label>
        <input
          id="tw-post-limit"
          className={inputClass}
          type="number"
          min={MIN_POST_LIMIT}
          max={MAX_POST_LIMIT}
          value={params.limit}
          onChange={(e) =>
            onChange({ ...params, limit: Number(e.target.value) || DEFAULT_POST_LIMIT })
          }
        />
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Matched posts to analyze ({MIN_POST_LIMIT}–{MAX_POST_LIMIT})
        </p>
      </div>
    </div>
    <div className="flex flex-wrap gap-4 mt-4">
      <div className="flex flex-col gap-1">
        <span className={stepLabelClass}>Step 1</span>
        <button
          className="rounded bg-[#d93900] dark:bg-orange-600 px-4 py-2 text-sm text-white disabled:opacity-50"
          onClick={onCollect}
          disabled={collecting || analysing || reporting}
        >
          {collecting ? 'Finding keywords…' : 'Find keywords'}
        </button>
        <p className="text-xs text-gray-500 dark:text-gray-400 max-w-[11rem]">
          Collect posts and top 10 keywords
        </p>
      </div>
      <div className="flex flex-col gap-1">
        <span className={stepLabelClass}>Step 2</span>
        <button
          className="rounded border border-[#d93900] dark:border-orange-600 px-4 py-2 text-sm text-[#d93900] dark:text-orange-400 disabled:opacity-50"
          onClick={onAnalyze}
          disabled={!canAnalyze || collecting || analysing || reporting}
        >
          {analysing ? 'Running analysis…' : 'Run analysis'}
        </button>
        <p className="text-xs text-gray-500 dark:text-gray-400 max-w-[11rem]">
          Lightweight charts and preview briefing
        </p>
      </div>
      {onCopyReport ? (
        <div className="flex flex-col gap-1">
          <span className={stepLabelClass}>Step 3</span>
          <button
            className="rounded border border-gray-400 dark:border-gray-500 px-4 py-2 text-sm text-gray-800 dark:text-gray-200 disabled:opacity-50"
            onClick={onCopyReport}
            disabled={!canCopyReport || collecting || analysing || reporting}
          >
            {reporting ? 'Copying…' : 'Copy report data'}
          </button>
          <p className="text-xs text-gray-500 dark:text-gray-400 max-w-[12rem]">
            Paste at{' '}
            {reportUploadUrl ? (
              <span className="break-all">{reportUploadUrl}</span>
            ) : (
              'localhost:8000/upload'
            )}
          </p>
        </div>
      ) : null}
    </div>
  </section>
);
