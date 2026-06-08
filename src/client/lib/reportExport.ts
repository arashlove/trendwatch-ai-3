import { showToast } from '@devvit/web/client';
import type { ReportRequest } from '../../shared/types';
import { DEFAULT_REPORT_API_URL, MAX_REPORT_POSTS } from '../../shared/types';

export const reportUploadUrl = (): string => {
  const base = (
    import.meta.env.VITE_REPORT_API_URL ?? DEFAULT_REPORT_API_URL
  ).replace(/\/$/, '');
  return `${base}/upload`;
};

export const buildReportRequest = (
  query: string,
  subreddit: string,
  posts: ReportRequest['posts']
): ReportRequest => ({
  query,
  subreddit,
  posts: posts.slice(0, MAX_REPORT_POSTS),
});

export const serializeReportRequest = (payload: ReportRequest): string => {
  if (payload.posts.length < 5) {
    throw new Error('Need at least 5 posts for a full report');
  }
  return JSON.stringify(payload, null, 2);
};

export type CopyReportResult = {
  json: string;
  copiedToClipboard: boolean;
};

export const copyReportDataToClipboard = async (
  payload: ReportRequest
): Promise<CopyReportResult> => {
  const json = serializeReportRequest(payload);

  try {
    await navigator.clipboard.writeText(json);
    showToast('Report JSON copied — paste at your local upload page');
    return { json, copiedToClipboard: true };
  } catch {
    return { json, copiedToClipboard: false };
  }
};
