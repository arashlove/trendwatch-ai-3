import type { CollectedPost, EnrichedPost } from './types';
import { scoreSentiment } from './sentiment';
import { extractRiskKeywords } from './crisis';

export const cleanText = (text: string): string =>
  text
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/[^\w\s#@]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();

export const preprocessAndScoreSentiment = (post: CollectedPost): EnrichedPost => {
  const cleanedText = cleanText(`${post.title} ${post.body}`);
  const { sentiment, sentimentScore } = scoreSentiment(cleanedText);
  const riskKeywords = extractRiskKeywords(cleanedText);

  return {
    ...post,
    cleanedText,
    sentiment,
    sentimentScore,
    riskKeywords,
  };
};

export const preprocessPosts = (posts: CollectedPost[]): EnrichedPost[] =>
  posts.map(preprocessAndScoreSentiment);
