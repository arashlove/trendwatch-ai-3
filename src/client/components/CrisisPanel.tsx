import type { AnalyzeResponse } from '../../shared/types';

type CrisisPanelProps = {
  crisis: AnalyzeResponse['crisis'];
};

const levelColor = (level: string): string => {
  if (level === 'Critical') return 'text-red-600';
  if (level === 'High') return 'text-orange-600';
  if (level === 'Medium') return 'text-yellow-600';
  return 'text-green-600';
};

export const CrisisPanel = ({ crisis }: CrisisPanelProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
      Crisis assessment
    </h2>
    <p className={`text-3xl font-bold ${levelColor(crisis.risk_level)}`}>
      {crisis.crisis_score} — {crisis.risk_level}
    </p>
    <ul className="mt-3 space-y-1 text-sm text-gray-700 dark:text-gray-300">
      {crisis.reasons.map((reason) => (
        <li key={reason}>• {reason}</li>
      ))}
    </ul>
  </section>
);
