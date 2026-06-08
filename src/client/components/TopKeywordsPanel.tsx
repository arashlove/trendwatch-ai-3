import type { KeywordCount } from '../../shared/types';

type TopKeywordsPanelProps = {
  keywords: KeywordCount[];
};

export const TopKeywordsPanel = ({ keywords }: TopKeywordsPanelProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
      Top 10 keywords
    </h2>
    {keywords.length === 0 ? (
      <p className="text-sm text-gray-500">No keywords extracted from this sample.</p>
    ) : (
      <ol className="space-y-2">
        {keywords.map((kw, index) => (
          <li
            key={kw.keyword}
            className="flex items-center justify-between rounded border border-gray-200 dark:border-gray-600 px-3 py-2 text-sm"
          >
            <span className="text-gray-900 dark:text-gray-100">
              <span className="text-gray-400 mr-2">{index + 1}.</span>
              {kw.keyword}
            </span>
            <span className="text-gray-500 dark:text-gray-400">
              {kw.post_count} posts · {kw.count} mentions
            </span>
          </li>
        ))}
      </ol>
    )}
  </section>
);
