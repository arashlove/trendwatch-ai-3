export type CollectedPost = {
  id: string;
  title: string;
  body: string;
  subreddit: string;
  authorName: string;
  score: number;
  numberOfComments: number;
  permalink: string;
  createdAt: Date;
};

export type RedditDataSource = 'reddit_devvit_new' | 'reddit_devvit_best';

export type CollectParams = {
  query: string;
  subreddit: string;
  scanLimit: number;
  postLimit: number;
};

export type CollectResult = {
  posts: CollectedPost[];
  postsScanned: number;
  postsMatched: number;
  dataSource: RedditDataSource;
};

export type SentimentLabel = 'positive' | 'neutral' | 'negative';

export type EnrichedPost = CollectedPost & {
  cleanedText: string;
  sentiment: SentimentLabel;
  sentimentScore: number;
  riskKeywords: string[];
};
