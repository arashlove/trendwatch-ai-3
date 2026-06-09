import type { KeywordCount } from '../../shared/types';

type TopKeywordsPanelProps = {
  keywords: KeywordCount[];
  onKeywordSelect?: (keyword: string) => void;
  selectedKeyword?: string;
};

export const TopKeywordsPanel = ({
  keywords,
  onKeywordSelect,
  selectedKeyword,
}: TopKeywordsPanelProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
      Top 10 keywords
    </h2>
    {keywords.length === 0 ? (
      <p className="text-sm text-gray-500">No keywords extracted from this sample.</p>
    ) : (
      <ol className="space-y-2">
        {keywords.map((kw, index) => {
          const isSelected = selectedKeyword === kw.keyword;
          return (
            <li key={kw.keyword}>
              <button
                type="button"
                className={`w-full flex items-center justify-between rounded border px-3 py-2 text-sm text-left transition-colors ${
                  isSelected
                    ? 'border-[#d93900] dark:border-orange-500 bg-orange-50 dark:bg-orange-950/30'
                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                }`}
                onClick={() => onKeywordSelect?.(kw.keyword)}
              >
                <span className="text-gray-900 dark:text-gray-100">
                  <span className="text-gray-400 mr-2">{index + 1}.</span>
                  {kw.keyword}
                </span>
                <span className="text-gray-500 dark:text-gray-400">
                  {kw.post_count} posts · {kw.count} mentions
                </span>
              </button>
            </li>
          );
        })}
      </ol>
    )}
  </section>
);
