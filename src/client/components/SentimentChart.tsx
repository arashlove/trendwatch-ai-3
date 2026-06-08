import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { AnalyzeResponse } from '../../shared/types';

type SentimentChartProps = {
  distribution: AnalyzeResponse['sentiment_distribution'];
};

const COLORS = ['#22c55e', '#94a3b8', '#ef4444'];

export const SentimentChart = ({ distribution }: SentimentChartProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
      Sentiment distribution
    </h2>
    <div className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={distribution}
            dataKey="count"
            nameKey="label"
            cx="50%"
            cy="50%"
            outerRadius={80}
            label
          >
            {distribution.map((entry, index) => (
              <Cell
                key={entry.label}
                fill={COLORS[index % COLORS.length] ?? '#94a3b8'}
              />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
    <div className="h-40 mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={distribution}>
          <XAxis dataKey="label" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="count" fill="#d93900" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  </section>
);
