import type { KeywordCount } from '../../shared/types';
import type { CollectedPost } from './types';

const STOPWORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
  'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
  'will', 'with', 'you', 'your', 'this', 'but', 'they', 'have', 'had', 'what',
  'when', 'where', 'who', 'which', 'why', 'how', 'all', 'each', 'few', 'more',
  'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
  'so', 'than', 'too', 'very', 'can', 'just', 'don', 'now', 'im', 'ive', 'been',
  'being', 'would', 'could', 'should', 'about', 'into', 'through', 'during',
  'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over', 'under',
  'again', 'further', 'then', 'once', 'here', 'there', 'any', 'both', 'each',
  'our', 'ours', 'their', 'them', 'these', 'those', 'my', 'me', 'we', 'us',
  'his', 'her', 'she', 'him', 'also', 'get', 'got', 'like', 'one', 'two',
  'new', 'said', 'say', 'says', 'really', 'even', 'still', 'way', 'want',
  'know', 'think', 'going', 'goes', 'went', 'come', 'came', 'make', 'made',
]);

const tokenize = (text: string): string[] =>
  text
    .toLowerCase()
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/[^a-z0-9#@]+/g, ' ')
    .split(/\s+/)
    .filter((token) => token.length >= 3 && !STOPWORDS.has(token));

export const extractTopKeywords = (
  posts: CollectedPost[],
  query: string,
  maxKeywords = 10
): KeywordCount[] => {
  const queryTokens = new Set(tokenize(query));
  const termCounts = new Map<string, number>();
  const postCounts = new Map<string, number>();

  for (const post of posts) {
    const text = `${post.title} ${post.body}`;
    const tokens = [...new Set(tokenize(text))];
    const seenInPost = new Set<string>();

    for (const token of tokens) {
      if (queryTokens.has(token)) {
        continue;
      }
      termCounts.set(token, (termCounts.get(token) ?? 0) + 1);
      if (!seenInPost.has(token)) {
        seenInPost.add(token);
        postCounts.set(token, (postCounts.get(token) ?? 0) + 1);
      }
    }
  }

  return [...termCounts.entries()]
    .map(([keyword, count]) => ({
      keyword,
      count,
      post_count: postCounts.get(keyword) ?? 0,
    }))
    .sort((a, b) => b.post_count - a.post_count || b.count - a.count)
    .slice(0, maxKeywords);
};

export const extractTopEntities = (
  posts: CollectedPost[],
  maxEntities = 10
): { entity: string; count: number }[] => {
  const counts = new Map<string, number>();

  for (const post of posts) {
    const text = `${post.title} ${post.body}`;
    const mentions = text.match(/@[a-zA-Z0-9_]+/g) ?? [];
    const hashtags = text.match(/#[a-zA-Z0-9_]+/g) ?? [];
    const entities = [...mentions, ...hashtags].map((e) => e.toLowerCase());

    for (const entity of new Set(entities)) {
      counts.set(entity, (counts.get(entity) ?? 0) + 1);
    }
  }

  return [...counts.entries()]
    .map(([entity, count]) => ({ entity, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, maxEntities);
};
