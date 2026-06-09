import type { AnalyzeResponse } from '../../shared/types';
import { extractTopEntities, extractTopKeywords } from './keywords';
import { collectRedditPostsForQuery } from './redditCollect';
import { preprocessPosts } from './preprocessing';
import { aggregateRiskKeywords, scoreCrisis, sentimentCounts } from './crisis';
import { buildTrends } from './trends';
import { buildTopics } from './topics';
import { buildBriefing } from './briefing';
import type { CollectParams } from './types';

const buildHighImpactPosts = (
  posts: ReturnType<typeof preprocessPosts>
): AnalyzeResponse['high_impact_posts'] =>
  [...posts]
    .map((post) => {
      const sentimentWeight =
        post.sentiment === 'negative' ? 1.5 : post.sentiment === 'positive' ? 0.8 : 1;
      const impactScore = Math.round(
        (post.score + post.numberOfComments * 2) * sentimentWeight
      );
      return {
        id: post.id,
        title: post.title,
        author: post.authorName,
        subreddit: post.subreddit,
        score: post.score,
        num_comments: post.numberOfComments,
        sentiment: post.sentiment,
        risk_keywords: post.riskKeywords,
        impact_score: impactScore,
        permalink: post.permalink,
      };
    })
    .sort((a, b) => b.impact_score - a.impact_score)
    .slice(0, 10);

export const runPipeline = async (
  params: CollectParams
): Promise<AnalyzeResponse> => {
  const collected = await collectRedditPostsForQuery(params);
  const topKeywords = extractTopKeywords(collected.posts, params.query, 10);
  const enriched = preprocessPosts(collected.posts);
  const trends = buildTrends(enriched);
  const crisis = scoreCrisis(enriched, trends.spike_detected);
  const topics = buildTopics(enriched, topKeywords);
  const counts = sentimentCounts(enriched);
  const total = enriched.length || 1;

  const summary = {
    total_posts: enriched.length,
    positive: counts.positive,
    neutral: counts.neutral,
    negative: counts.negative,
    sentiment_percentages: {
      positive: Math.round((counts.positive / total) * 100),
      neutral: Math.round((counts.neutral / total) * 100),
      negative: Math.round((counts.negative / total) * 100),
    },
    crisis_score: crisis.crisis_score,
    risk_level: crisis.risk_level,
  };

  const briefing = buildBriefing({
    params,
    posts: enriched,
    crisis,
    topKeywords,
    trends,
  });

  return {
    query: params.query,
    subreddit: params.subreddit,
    data_source: collected.dataSource,
    top_keywords: topKeywords,
    summary,
    sentiment_distribution: [
      { label: 'Positive', count: counts.positive },
      { label: 'Neutral', count: counts.neutral },
      { label: 'Negative', count: counts.negative },
    ],
    trends,
    topics,
    high_impact_posts: buildHighImpactPosts(enriched),
    risk_keywords: aggregateRiskKeywords(enriched),
    top_entities: extractTopEntities(collected.posts),
    crisis,
    briefing,
    techniques_used: {
      in_app: [
        'Devvit Reddit API post collection (preview only)',
        'Stopword removal and term-frequency keywords',
        'Regex preprocessing and lexicon sentiment',
        'Rule-based trends, crisis score, and briefing',
        'Keyword-overlap topic labels',
      ],
      full_report: [
        'spaCy NER and POS tagging',
        'VADER sentiment analysis',
        'TF-IDF + Logistic Regression ensemble',
        'Sentence embeddings (MiniLM) topic clustering',
        'RAG-grounded LLM briefing',
        'ReAct agent trace and printable HTML report with Matplotlib charts',
        'Runs in local Python FastAPI service (paste at /upload)',
      ],
    },
  };
};
