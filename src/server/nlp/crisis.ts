import type { EnrichedPost, SentimentLabel } from './types';
import type { AnalyzeResponse } from '../../shared/types';

export const RISK_KEYWORD_LIST = [
  'scam', 'fraud', 'refund', 'lawsuit', 'boycott', 'unsafe', 'danger', 'crisis',
  'outage', 'hack', 'breach', 'leak', 'recall', 'warning', 'complaint', 'delay',
  'broken', 'misleading', 'overpriced', 'ripoff', 'disaster', 'unacceptable',
];

export const extractRiskKeywords = (text: string): string[] => {
  const tokens = new Set(text.split(/\s+/));
  return RISK_KEYWORD_LIST.filter((word) => tokens.has(word));
};

export const riskLevelFromScore = (score: number): string => {
  if (score >= 81) return 'Critical';
  if (score >= 61) return 'High';
  if (score >= 31) return 'Medium';
  return 'Low';
};

export const scoreCrisis = (
  posts: EnrichedPost[],
  spikeDetected: boolean
): AnalyzeResponse['crisis'] => {
  const total = posts.length || 1;
  const negativePosts = posts.filter((p) => p.sentiment === 'negative');
  const negativeRatio = negativePosts.length / total;

  const riskKeywordCount = posts.reduce((sum, p) => sum + p.riskKeywords.length, 0);
  const riskKeywordDensity = riskKeywordCount / total;

  const highImpactNegative = negativePosts.filter(
    (p) => p.score + p.numberOfComments >= 50
  ).length;

  const negativeComponent = negativeRatio * 40;
  const riskComponent = Math.min(riskKeywordDensity * 10, 1) * 25;
  const impactComponent = Math.min(highImpactNegative / 10, 1) * 20;
  const spikeComponent = spikeDetected ? 10 : 0;

  const crisisScore = Math.min(
    100,
    Math.round(negativeComponent + riskComponent + impactComponent + spikeComponent)
  );

  const reasons: string[] = [];
  if (negativeRatio > 0.4) {
    reasons.push(`${Math.round(negativeRatio * 100)}% of posts are negative`);
  }
  if (riskKeywordCount > 0) {
    reasons.push(`${riskKeywordCount} risk keyword mentions detected`);
  }
  if (highImpactNegative > 0) {
    reasons.push(`${highImpactNegative} high-engagement negative posts`);
  }
  if (spikeDetected) {
    reasons.push('Negative sentiment spike detected in recent timeline');
  }
  if (reasons.length === 0) {
    reasons.push('No major crisis signals detected in this sample');
  }

  return {
    crisis_score: crisisScore,
    risk_level: riskLevelFromScore(crisisScore),
    components: {
      negative_ratio: Math.round(negativeComponent),
      risk_keywords: Math.round(riskComponent),
      high_impact_negative: Math.round(impactComponent),
      trend_spike: spikeComponent,
    },
    reasons,
  };
};

export const aggregateRiskKeywords = (
  posts: EnrichedPost[]
): { keyword: string; count: number }[] => {
  const counts = new Map<string, number>();
  for (const post of posts) {
    for (const keyword of post.riskKeywords) {
      counts.set(keyword, (counts.get(keyword) ?? 0) + 1);
    }
  }
  return [...counts.entries()]
    .map(([keyword, count]) => ({ keyword, count }))
    .sort((a, b) => b.count - a.count);
};

export const sentimentCounts = (
  posts: EnrichedPost[]
): Record<SentimentLabel, number> => ({
  positive: posts.filter((p) => p.sentiment === 'positive').length,
  neutral: posts.filter((p) => p.sentiment === 'neutral').length,
  negative: posts.filter((p) => p.sentiment === 'negative').length,
});
