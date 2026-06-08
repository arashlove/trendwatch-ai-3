import type { CollectResponse } from '../../shared/types';

type DataSourceBannerProps = {
  data: CollectResponse;
};

export const DataSourceBanner = ({ data }: DataSourceBannerProps) => {
  const hasFilter = data.query.trim().length > 0;
  const sourceLabel = hasFilter
    ? data.data_source === 'reddit_devvit_best'
      ? 'Live Reddit — best posts, keyword filter'
      : 'Live Reddit — new posts, keyword filter'
    : data.data_source === 'reddit_devvit_best'
      ? 'Live Reddit — best posts (no keyword filter)'
      : 'Live Reddit — all recent posts (no keyword filter)';

  return (
    <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950/40 p-3 text-sm">
      <p className="font-medium text-blue-900 dark:text-blue-100">{sourceLabel}</p>
      <p className="text-blue-800 dark:text-blue-200 mt-1">
        {hasFilter ? (
          <>
            Query &quot;{data.query}&quot; in r/{data.subreddit} — scanned{' '}
            <strong>{data.posts_scanned}</strong>, matched{' '}
            <strong>{data.posts_matched}</strong>
          </>
        ) : (
          <>
            r/{data.subreddit} — scanned <strong>{data.posts_scanned}</strong>, using{' '}
            <strong>{data.posts_matched}</strong> posts for keywords
          </>
        )}
      </p>
    </div>
  );
};
