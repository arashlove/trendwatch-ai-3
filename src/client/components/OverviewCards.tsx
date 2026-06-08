import type { AnalyzeResponse } from '../../shared/types';

type OverviewCardsProps = {
  summary: AnalyzeResponse['summary'];
};

export const OverviewCards = ({ summary }: OverviewCardsProps) => {
  const cards = [
    { label: 'Total posts', value: summary.total_posts },
    { label: 'Positive', value: `${summary.sentiment_percentages.positive}%` },
    { label: 'Neutral', value: `${summary.sentiment_percentages.neutral}%` },
    { label: 'Negative', value: `${summary.sentiment_percentages.negative}%` },
    { label: 'Crisis score', value: summary.crisis_score },
    { label: 'Risk level', value: summary.risk_level },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-lg border border-gray-200 dark:border-gray-700 p-3 bg-white dark:bg-gray-900"
        >
          <p className="text-xs text-gray-500 dark:text-gray-400">{card.label}</p>
          <p className="text-xl font-semibold text-gray-900 dark:text-gray-100 mt-1">
            {card.value}
          </p>
        </div>
      ))}
    </div>
  );
};
