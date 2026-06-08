import type { EnrichedPost } from './types';
import type { AnalyzeResponse } from '../../shared/types';

const toDateKey = (date: Date): string => date.toISOString().slice(0, 10);

export const buildTrends = (posts: EnrichedPost[]): AnalyzeResponse['trends'] => {
  const buckets = new Map<
    string,
    { post_count: number; negative_count: number; risk_keyword_count: number }
  >();

  for (const post of posts) {
    const date = toDateKey(post.createdAt);
    const bucket = buckets.get(date) ?? {
      post_count: 0,
      negative_count: 0,
      risk_keyword_count: 0,
    };
    bucket.post_count += 1;
    if (post.sentiment === 'negative') {
      bucket.negative_count += 1;
    }
    bucket.risk_keyword_count += post.riskKeywords.length;
    buckets.set(date, bucket);
  }

  const timeline = [...buckets.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, stats]) => ({
      date,
      post_count: stats.post_count,
      negative_count: stats.negative_count,
      negative_ratio:
        stats.post_count > 0 ? stats.negative_count / stats.post_count : 0,
      risk_keyword_count: stats.risk_keyword_count,
    }));

  const ratios = timeline.map((t) => t.negative_ratio);
  const avgNegativeRatio =
    ratios.length > 0 ? ratios.reduce((a, b) => a + b, 0) / ratios.length : 0;

  const latest = timeline.at(-1);
  const spikeDetected =
    latest !== undefined &&
    latest.post_count >= 3 &&
    latest.negative_ratio > avgNegativeRatio + 0.25;

  const spikeMessage = spikeDetected
    ? `Negative ratio on ${latest.date} (${Math.round(latest.negative_ratio * 100)}%) exceeds the average (${Math.round(avgNegativeRatio * 100)}%)`
    : 'No significant negative spike detected';

  return {
    timeline,
    spike_detected: spikeDetected,
    spike_message: spikeMessage,
    avg_negative_ratio: avgNegativeRatio,
  };
};
