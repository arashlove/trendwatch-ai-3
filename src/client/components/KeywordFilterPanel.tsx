type KeywordFilterPanelProps = {
  keyword: string;
  onKeywordChange: (keyword: string) => void;
  onFilter: () => void;
  onCopyReport?: () => void;
  reportUploadUrl?: string;
  filtering: boolean;
  reporting?: boolean;
  canFilter: boolean;
  canCopyReport?: boolean;
  filterQuery?: string;
  postsMatched?: number;
};

const inputClass =
  'rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 w-full';

const labelClass =
  'block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1';

const stepLabelClass =
  'text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400';

export const KeywordFilterPanel = ({
  keyword,
  onKeywordChange,
  onFilter,
  onCopyReport,
  reportUploadUrl,
  filtering,
  reporting = false,
  canFilter,
  canCopyReport = false,
  filterQuery,
  postsMatched,
}: KeywordFilterPanelProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
      Step 2 — Filter by keyword
    </h2>
    <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
      Pick a term from the chart above or type one. This re-runs collect with the API keyword
      filter and prepares posts for the full Python report.
    </p>
    <div className="max-w-md">
      <label className={labelClass} htmlFor="tw-filter-keyword">
        Keyword
      </label>
      <input
        id="tw-filter-keyword"
        className={inputClass}
        value={keyword}
        onChange={(e) => onKeywordChange(e.target.value)}
        placeholder="e.g. privacy, ai, refund"
      />
      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
        Click a keyword in the list above to fill this field
      </p>
    </div>
    <div className="flex flex-wrap gap-4 mt-4">
      <div className="flex flex-col gap-1">
        <span className={stepLabelClass}>Filter</span>
        <button
          className="rounded border border-[#d93900] dark:border-orange-600 px-4 py-2 text-sm text-[#d93900] dark:text-orange-400 disabled:opacity-50"
          onClick={onFilter}
          disabled={!canFilter || !keyword.trim() || filtering || reporting}
        >
          {filtering ? 'Filtering…' : 'Get keyword results'}
        </button>
      </div>
      {onCopyReport ? (
        <div className="flex flex-col gap-1">
          <span className={stepLabelClass}>Step 3</span>
          <button
            className="rounded border border-gray-400 dark:border-gray-500 px-4 py-2 text-sm text-gray-800 dark:text-gray-200 disabled:opacity-50"
            onClick={onCopyReport}
            disabled={!canCopyReport || filtering || reporting}
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
    {filterQuery && postsMatched !== undefined ? (
      <p className="mt-3 text-sm text-green-800 dark:text-green-300 bg-green-50 dark:bg-green-950/30 rounded px-3 py-2">
        Filtered on <strong>&quot;{filterQuery}&quot;</strong> —{' '}
        <strong>{postsMatched}</strong> posts ready for export.
      </p>
    ) : null}
  </section>
);
