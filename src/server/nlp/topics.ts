import type { KeywordCount } from '../../shared/types';
import type { EnrichedPost } from './types';
import type { AnalyzeResponse } from '../../shared/types';

export const buildTopics = (
  posts: EnrichedPost[],
  topKeywords: KeywordCount[]
): AnalyzeResponse['topics'] => {
  if (posts.length === 0 || topKeywords.length === 0) {
    return [];
  }

  const topicKeywords = topKeywords.slice(0, 5);
  const topics: AnalyzeResponse['topics'] = [];

  for (const [index, kw] of topicKeywords.entries()) {
    const members = posts.filter((post) =>
      post.cleanedText.includes(kw.keyword)
    );
    if (members.length === 0) {
      continue;
    }

    const sentimentCounts = { positive: 0, neutral: 0, negative: 0 };
    for (const post of members) {
      sentimentCounts[post.sentiment] += 1;
    }
    const dominant = (Object.entries(sentimentCounts).sort(
      (a, b) => b[1] - a[1]
    )[0]?.[0] ?? 'neutral') as EnrichedPost['sentiment'];

    const representative = [...members].sort(
      (a, b) => b.score + b.numberOfComments - (a.score + a.numberOfComments)
    )[0];

    topics.push({
      topic_id: index + 1,
      label: kw.keyword,
      size: members.length,
      keywords: [kw.keyword, ...topKeywords.slice(1, 4).map((k) => k.keyword)],
      average_sentiment: dominant,
      representative_post: representative
        ? {
            id: representative.id,
            title: representative.title,
            sentiment: representative.sentiment,
            permalink: representative.permalink,
          }
        : null,
    });
  }

  return topics;
};
