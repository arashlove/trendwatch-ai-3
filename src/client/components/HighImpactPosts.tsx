import { navigateTo } from '@devvit/web/client';
import type { AnalyzeResponse } from '../../shared/types';

type HighImpactPostsProps = {
  posts: AnalyzeResponse['high_impact_posts'];
};

export const HighImpactPosts = ({ posts }: HighImpactPostsProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
      High-impact posts
    </h2>
    <ul className="space-y-2 max-h-64 overflow-y-auto">
      {posts.map((post) => (
        <li
          key={post.id}
          className="rounded border border-gray-200 dark:border-gray-600 p-2 text-sm"
        >
          <button
            className="text-left hover:underline text-gray-900 dark:text-gray-100"
            onClick={() => navigateTo(post.permalink)}
          >
            {post.title}
          </button>
          <p className="text-xs text-gray-500 mt-1">
            u/{post.author} · r/{post.subreddit} · {post.sentiment} · impact{' '}
            {post.impact_score}
            {post.risk_keywords.length > 0
              ? ` · risks: ${post.risk_keywords.join(', ')}`
              : ''}
          </p>
        </li>
      ))}
    </ul>
  </section>
);
