import type { AnalyzeResponse } from '../../shared/types';

type InsightReportProps = {
  briefing: AnalyzeResponse['briefing'];
  techniques: AnalyzeResponse['techniques_used'];
};

export const InsightReport = ({ briefing, techniques }: InsightReportProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
      Insight briefing (in-app preview)
    </h2>
    <p className="text-xs text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 rounded p-2">
      This summary uses lightweight rule-based NLP in Devvit. For spaCy, VADER, TF-IDF+LR,
      embeddings, RAG, and the full assignment report, use{' '}
      <strong>Step 3 — Copy report data</strong> after Step 1, then paste at local FastAPI.
    </p>
    <div>
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Executive summary</h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
        {briefing.executive_summary}
      </p>
    </div>
    <div>
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Main concerns</h3>
      <ul className="text-sm text-gray-600 dark:text-gray-400 mt-1 list-disc pl-5">
        {briefing.main_concerns.map((c) => (
          <li key={c}>{c}</li>
        ))}
      </ul>
    </div>
    <div>
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Recommended actions
      </h3>
      <ul className="text-sm text-gray-600 dark:text-gray-400 mt-1 list-disc pl-5">
        {briefing.recommended_actions.map((a) => (
          <li key={a}>{a}</li>
        ))}
      </ul>
    </div>
    <p className="text-xs text-gray-400 italic">{briefing.ethics_notice}</p>
    <div className="grid gap-3 sm:grid-cols-2 text-xs text-gray-500 dark:text-gray-400">
      <div>
        <p className="font-medium text-gray-700 dark:text-gray-300 mb-1">In-app (preview)</p>
        <ul className="list-disc pl-4 space-y-0.5">
          {techniques.in_app.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      </div>
      <div>
        <p className="font-medium text-gray-700 dark:text-gray-300 mb-1">
          Full report (local Python)
        </p>
        <ul className="list-disc pl-4 space-y-0.5">
          {techniques.full_report.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      </div>
    </div>
  </section>
);
