import type { CollectedPostSummary } from '../../shared/types';

type FilteredPostsPanelProps = {
  query: string;
  posts: CollectedPostSummary[];
};

export const FilteredPostsPanel = ({ query, posts }: FilteredPostsPanelProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
      Matched posts — &quot;{query}&quot;
    </h2>
    {posts.length === 0 ? (
      <p className="text-sm text-gray-500">No posts matched this keyword.</p>
    ) : (
      <ul className="space-y-2 max-h-64 overflow-y-auto">
        {posts.map((post) => (
          <li
            key={post.id}
            className="rounded border border-gray-200 dark:border-gray-600 px-3 py-2 text-sm"
          >
            <p className="text-gray-900 dark:text-gray-100">{post.title}</p>
            <p className="text-xs text-gray-500 mt-0.5">
              r/{post.subreddit} · score {post.score}
            </p>
          </li>
        ))}
      </ul>
    )}
  </section>
);
