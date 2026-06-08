import { navigateTo } from '@devvit/web/client';
import type { AnalyzeResponse } from '../../shared/types';

type TopicCardsProps = {
  topics: AnalyzeResponse['topics'];
};

export const TopicCards = ({ topics }: TopicCardsProps) => (
  <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
      Topics
    </h2>
    <div className="grid gap-3 sm:grid-cols-2">
      {topics.map((topic) => (
        <div
          key={topic.topic_id}
          className="rounded border border-gray-200 dark:border-gray-600 p-3 text-sm"
        >
          <p className="font-medium text-gray-900 dark:text-gray-100">{topic.label}</p>
          <p className="text-gray-500 mt-1">
            {topic.size} posts · avg {topic.average_sentiment}
          </p>
          <p className="text-gray-400 text-xs mt-1">
            {topic.keywords.slice(0, 4).join(', ')}
          </p>
          {topic.representative_post ? (
            <button
              className="mt-2 text-left text-[#d93900] dark:text-orange-400 hover:underline text-xs"
              onClick={() => navigateTo(topic.representative_post!.permalink)}
            >
              {topic.representative_post.title}
            </button>
          ) : null}
        </div>
      ))}
    </div>
  </section>
);
