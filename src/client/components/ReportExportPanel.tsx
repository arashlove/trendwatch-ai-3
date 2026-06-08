type ReportExportPanelProps = {
  uploadUrl: string;
  json: string;
  copiedToClipboard: boolean;
};

export const ReportExportPanel = ({
  uploadUrl,
  json,
  copiedToClipboard,
}: ReportExportPanelProps) => (
  <div className="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/30 p-3 text-sm text-green-900 dark:text-green-200 space-y-2">
    <p className="font-medium">
      {copiedToClipboard
        ? 'Report JSON copied to clipboard.'
        : 'Copy the JSON below manually (Ctrl+A, then Ctrl+C).'}
    </p>
    <p>
      Open{' '}
      <code className="text-xs bg-white/60 dark:bg-black/20 px-1 rounded break-all">
        {uploadUrl}
      </code>{' '}
      in a normal browser tab, paste the JSON, and run the full Python NLP report.
    </p>
    {!copiedToClipboard ? (
      <div>
        <label
          className="block text-xs font-medium text-green-800 dark:text-green-300 mb-1"
          htmlFor="tw-report-json"
        >
          Report JSON
        </label>
        <textarea
          id="tw-report-json"
          readOnly
          className="w-full h-32 text-xs font-mono rounded border border-green-300 dark:border-green-700 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 p-2"
          value={json}
          onFocus={(e) => e.target.select()}
        />
      </div>
    ) : null}
  </div>
);
