import { reddit } from '@devvit/web/server';
import type { CollectParams, CollectResult, CollectedPost } from './types';

const BATCH_SIZE = 100;

const toCollectedPost = (post: {
  id: string;
  title: string;
  body?: string;
  subredditName: string;
  authorName: string;
  score: number;
  numberOfComments: number;
  permalink: string;
  createdAt: Date;
}): CollectedPost => ({
  id: post.id,
  title: post.title,
  body: post.body ?? '',
  subreddit: post.subredditName,
  authorName: post.authorName,
  score: post.score,
  numberOfComments: post.numberOfComments,
  permalink: `https://reddit.com${post.permalink}`,
  createdAt: post.createdAt,
});

const postMatchesQuery = (post: CollectedPost, query: string): boolean => {
  const haystack = `${post.title} ${post.body}`.toLowerCase();
  return haystack.includes(query.toLowerCase());
};

const fetchListing = async (
  subreddit: string,
  scanLimit: number
): Promise<{ posts: CollectedPost[]; dataSource: CollectResult['dataSource'] }> => {
  const posts: CollectedPost[] = [];
  let after: string | undefined;
  const useBest = subreddit.toLowerCase() === 'all';
  const dataSource: CollectResult['dataSource'] = useBest
    ? 'reddit_devvit_best'
    : 'reddit_devvit_new';

  while (posts.length < scanLimit) {
    const batchSize = Math.min(BATCH_SIZE, scanLimit - posts.length);
    const listing = useBest
      ? reddit.getBestPosts({ limit: batchSize, pageSize: batchSize, after })
      : reddit.getNewPosts({
          subredditName: subreddit,
          limit: batchSize,
          pageSize: batchSize,
          after,
        });

    const batch = await listing.all();
    if (batch.length === 0) {
      break;
    }

    for (const post of batch) {
      posts.push(toCollectedPost(post));
    }

    after = batch.at(-1)?.id;
    if (!listing.hasMore || batch.length < batchSize) {
      break;
    }
  }

  return { posts, dataSource };
};

export const collectRedditPostsForQuery = async (
  params: CollectParams
): Promise<CollectResult> => {
  const { query, subreddit, scanLimit, postLimit } = params;
  const { posts: listing, dataSource } = await fetchListing(subreddit, scanLimit);
  const normalizedQuery = query.trim().toLowerCase();
  const hasQueryFilter = normalizedQuery.length > 0;

  const matched = hasQueryFilter
    ? listing.filter((post) => postMatchesQuery(post, normalizedQuery))
    : listing;

  const selected = (
    hasQueryFilter && matched.length > 0 ? matched : listing
  ).slice(0, postLimit);

  return {
    posts: selected,
    postsScanned: listing.length,
    postsMatched: hasQueryFilter ? matched.length : selected.length,
    dataSource,
  };
};
