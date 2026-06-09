import { Hono } from 'hono';
import type {
  BackendHealthResponse,
  CollectResponse,
  AnalyzeResponse,
} from '../../shared/types';
import {
  DEFAULT_POST_LIMIT,
  DEFAULT_SCAN_LIMIT,
  MAX_POST_LIMIT,
  MAX_SCAN_LIMIT,
  MIN_POST_LIMIT,
  MIN_SCAN_LIMIT,
} from '../../shared/types';
import { collectRedditPostsForQuery } from '../nlp/redditCollect';
import { extractTopKeywords } from '../nlp/keywords';
import { toPostPayload } from '../nlp/postPayload';
import { runPipeline } from '../nlp/pipeline';
import type { CollectParams } from '../nlp/types';

type ErrorResponse = {
  status: 'error';
  message: string;
};

const parseParams = (c: {
  req: { query: (key: string) => string | undefined };
}): CollectParams | ErrorResponse => {
  const query = c.req.query('query')?.trim() ?? '';

  const subreddit = (c.req.query('subreddit')?.trim() || 'all').replace(/^r\//i, '');
  const scanLimitRaw = Number(c.req.query('scan_limit'));
  const postLimitRaw = Number(c.req.query('limit'));

  const scanLimit = Math.min(
    MAX_SCAN_LIMIT,
    Math.max(MIN_SCAN_LIMIT, Number.isFinite(scanLimitRaw) ? scanLimitRaw : DEFAULT_SCAN_LIMIT)
  );
  const postLimit = Math.min(
    MAX_POST_LIMIT,
    Math.max(MIN_POST_LIMIT, Number.isFinite(postLimitRaw) ? postLimitRaw : DEFAULT_POST_LIMIT)
  );

  return { query, subreddit, scanLimit, postLimit };
};

export const trendwatch = new Hono();

trendwatch.get('/health', (c) => {
  const response: BackendHealthResponse = {
    connected: true,
    mode: 'embedded',
    message: 'Live Reddit keyword collection',
    checked_at: new Date().toISOString(),
  };
  return c.json(response);
});

trendwatch.get('/collect', async (c) => {
  const params = parseParams(c);
  if ('status' in params) {
    return c.json<ErrorResponse>(params, 400);
  }

  try {
    const collected = await collectRedditPostsForQuery(params);
    const topKeywords = extractTopKeywords(collected.posts, params.query, 10);

    const response: CollectResponse = {
      query: params.query,
      subreddit: params.subreddit,
      data_source: collected.dataSource,
      posts_scanned: collected.postsScanned,
      posts_matched: collected.postsMatched,
      top_keywords: topKeywords,
      posts: collected.posts.map((post) => ({
        id: post.id,
        title: post.title,
        subreddit: post.subreddit,
        score: post.score,
        permalink: post.permalink,
      })),
      export_posts: collected.posts.map(toPostPayload),
    };

    return c.json(response);
  } catch (error) {
    console.error('TrendWatch collect error:', error);
    const message = error instanceof Error ? error.message : 'Collect failed';
    return c.json<ErrorResponse>({ status: 'error', message }, 400);
  }
});

trendwatch.get('/analyze', async (c) => {
  const params = parseParams(c);
  if ('status' in params) {
    return c.json<ErrorResponse>(params, 400);
  }

  try {
    const response: AnalyzeResponse = await runPipeline(params);
    return c.json(response);
  } catch (error) {
    console.error('TrendWatch analyze error:', error);
    const message = error instanceof Error ? error.message : 'Analysis failed';
    return c.json<ErrorResponse>({ status: 'error', message }, 400);
  }
});
