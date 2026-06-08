import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { AnalyzeResponse } from '../../shared/types';

type TrendTimelineProps = {
  trends: AnalyzeResponse['trends'];
};

type ChartPoint = AnalyzeResponse['trends']['timeline'][number] & {
  label: string;
  negative_pct: number;
};

const formatDateLabel = (isoDate: string): string => {
  const [, month, day] = isoDate.split('-');
  return `${month}/${day}`;
};

const buildChartData = (timeline: AnalyzeResponse['trends']['timeline']): ChartPoint[] =>
  timeline.map((point) => ({
    ...point,
    label: formatDateLabel(point.date),
    negative_pct: Math.round(point.negative_ratio * 100),
  }));

type TooltipPayload = {
  payload?: ChartPoint;
};

const TimelineTooltip = ({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) => {
  if (!active || !payload?.[0]?.payload) {
    return null;
  }
  const point = payload[0].payload;
  return (
    <div className="rounded border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 p-2 text-xs shadow">
      <p className="font-medium text-gray-900 dark:text-gray-100">{point.date}</p>
      <p className="text-gray-600 dark:text-gray-300">Posts: {point.post_count}</p>
      <p className="text-gray-600 dark:text-gray-300">Negative: {point.negative_count}</p>
      <p className="text-gray-600 dark:text-gray-300">Negative %: {point.negative_pct}%</p>
      <p className="text-gray-600 dark:text-gray-300">
        Risk keywords: {point.risk_keyword_count}
      </p>
    </div>
  );
};

export const TrendTimeline = ({ trends }: TrendTimelineProps) => {
  const chartData = buildChartData(trends.timeline);
  const maxPosts = Math.max(...chartData.map((p) => p.post_count), 1);
  const yMax = Math.max(maxPosts + 1, 4);
  const peakDay = [...chartData].sort((a, b) => b.post_count - a.post_count)[0];
  const totalPosts = chartData.reduce((sum, p) => sum + p.post_count, 0);

  return (
    <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">
        Trend timeline
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">{trends.spike_message}</p>

      {chartData.length === 0 ? (
        <p className="text-sm text-gray-500">No timeline data available.</p>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-2 mb-4 text-center">
            <div className="rounded bg-gray-100 dark:bg-gray-800 p-2">
              <p className="text-xs text-gray-500">Total posts</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {totalPosts}
              </p>
            </div>
            <div className="rounded bg-gray-100 dark:bg-gray-800 p-2">
              <p className="text-xs text-gray-500">Peak day</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {peakDay ? `${peakDay.label} (${peakDay.post_count})` : '—'}
              </p>
            </div>
            <div className="rounded bg-gray-100 dark:bg-gray-800 p-2">
              <p className="text-xs text-gray-500">Avg negative</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {Math.round(trends.avg_negative_ratio * 100)}%
              </p>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 10, fill: '#9ca3af' }}
                  interval={chartData.length > 10 ? Math.floor(chartData.length / 7) : 0}
                />
                <YAxis
                  yAxisId="posts"
                  allowDecimals={false}
                  domain={[0, yMax]}
                  tick={{ fontSize: 10, fill: '#9ca3af' }}
                  width={28}
                />
                <YAxis
                  yAxisId="pct"
                  orientation="right"
                  domain={[0, 100]}
                  tick={{ fontSize: 10, fill: '#9ca3af' }}
                  tickFormatter={(v) => `${v}%`}
                  width={36}
                />
                <Tooltip content={<TimelineTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar
                  yAxisId="posts"
                  dataKey="post_count"
                  fill="#3b82f6"
                  name="Posts"
                  barSize={chartData.length > 12 ? 8 : 16}
                  radius={[2, 2, 0, 0]}
                />
                <Bar
                  yAxisId="posts"
                  dataKey="negative_count"
                  fill="#ef4444"
                  name="Negative"
                  barSize={chartData.length > 12 ? 8 : 16}
                  radius={[2, 2, 0, 0]}
                />
                <Line
                  yAxisId="pct"
                  type="monotone"
                  dataKey="negative_pct"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  name="Negative %"
                  dot={{ r: 3 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Bars show daily post volume; orange line shows share of negative posts that day.
          </p>
        </>
      )}
    </section>
  );
};
