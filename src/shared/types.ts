export type KeywordCount = {
  keyword: string;
  count: number;
  post_count: number;
};

export type CollectedPostSummary = {
  id: string;
  title: string;
  subreddit: string;
  score: number;
  permalink: string;
};

export type PostPayload = {
  id: string;
  title: string;
  selftext: string;
  author: string;
  subreddit: string;
  score: number;
  num_comments: number;
  created_utc: number;
  permalink: string;
};

export type ReportRequest = {
  query: string;
  subreddit: string;
  posts: PostPayload[];
};

export type CollectResponse = {
  query: string;
  subreddit: string;
  data_source: 'reddit_devvit_new' | 'reddit_devvit_best';
  posts_scanned: number;
  posts_matched: number;
  top_keywords: KeywordCount[];
  posts: CollectedPostSummary[];
  export_posts: PostPayload[];
};

export type BackendHealthResponse = {
  connected: boolean;
  mode: string;
  message: string;
  checked_at: string;
};

export type AnalyzeResponse = {
  query: string;
  subreddit: string;
  data_source: string;
  top_keywords: KeywordCount[];
  summary: {
    total_posts: number;
    positive: number;
    neutral: number;
    negative: number;
    sentiment_percentages: {
      positive: number;
      neutral: number;
      negative: number;
    };
    crisis_score: number;
    risk_level: string;
  };
  sentiment_distribution: { label: string; count: number }[];
  trends: {
    timeline: {
      date: string;
      post_count: number;
      negative_count: number;
      negative_ratio: number;
      risk_keyword_count: number;
    }[];
    spike_detected: boolean;
    spike_message: string;
    avg_negative_ratio: number;
  };
  topics: {
    topic_id: number;
    label: string;
    size: number;
    keywords: string[];
    average_sentiment: string;
    representative_post: {
      id: string;
      title: string;
      sentiment: string;
      permalink: string;
    } | null;
  }[];
  high_impact_posts: {
    id: string;
    title: string;
    author: string;
    subreddit: string;
    score: number;
    num_comments: number;
    sentiment: string;
    risk_keywords: string[];
    impact_score: number;
    permalink: string;
  }[];
  risk_keywords: { keyword: string; count: number }[];
  top_entities: { entity: string; count: number }[];
  crisis: {
    crisis_score: number;
    risk_level: string;
    components: Record<string, number>;
    reasons: string[];
  };
  briefing: {
    executive_summary: string;
    main_concerns: string[];
    crisis_explanation: string;
    recommended_actions: string[];
    communication_strategy: string;
    ethics_notice: string;
    source: string;
  };
  techniques_used: {
    in_app: string[];
    full_report: string[];
  };
};

export type TrendWatchSearchParams = {
  query: string;
  subreddit: string;
  scan_limit: number;
  limit: number;
};

export const MAX_SCAN_LIMIT = 1000;
export const MAX_POST_LIMIT = 500;
export const MIN_SCAN_LIMIT = 100;
export const MIN_POST_LIMIT = 10;
export const DEFAULT_SCAN_LIMIT = 1000;
export const DEFAULT_POST_LIMIT = 200;
export const MAX_REPORT_POSTS = 200;
export const DEFAULT_REPORT_API_URL = 'http://127.0.0.1:8000';
export const DEFAULT_REPORT_UPLOAD_URL = `${DEFAULT_REPORT_API_URL}/upload`;
