import type { PostPayload } from '../../shared/types';
import type { CollectedPost } from './types';

export const toPostPayload = (post: CollectedPost): PostPayload => ({
  id: post.id,
  title: post.title,
  selftext: post.body,
  author: post.authorName,
  subreddit: post.subreddit,
  score: post.score,
  num_comments: post.numberOfComments,
  created_utc: Math.floor(post.createdAt.getTime() / 1000),
  permalink: post.permalink,
});
