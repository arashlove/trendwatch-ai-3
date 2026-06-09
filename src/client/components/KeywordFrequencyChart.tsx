import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { KeywordCount } from '../../shared/types';

type KeywordFrequencyChartProps = {
  keywords: KeywordCount[];
};

export const KeywordFrequencyChart = ({ keywords }: KeywordFrequencyChartProps) => {
  const chartData = keywords.map((kw) => ({
    keyword: kw.keyword,
    posts: kw.post_count,
    mentions: kw.count,
  }));

  if (chartData.length === 0) {
    return null;
  }

  const chartHeight = Math.max(220, chartData.length * 36);

  return (
    <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
        Keyword frequency comparison
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
        Posts containing each term vs total mention count across the corpus.
      </p>
      <div style={{ height: chartHeight }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 4, right: 16, left: 4, bottom: 4 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.25} />
            <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
            <YAxis
              type="category"
              dataKey="keyword"
              width={88}
              tick={{ fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--tw-bg-opacity, #111827)',
                border: '1px solid #374151',
                borderRadius: 6,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="posts" name="Posts" fill="#3b82f6" radius={[0, 3, 3, 0]} />
            <Bar dataKey="mentions" name="Mentions" fill="#d93900" radius={[0, 3, 3, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
};
