import type { SentimentLabel } from './types';

const POSITIVE_WORDS = [
  'love', 'great', 'happy', 'good', 'praise', 'excellent', 'amazing', 'awesome',
  'fantastic', 'wonderful', 'best', 'beautiful', 'brilliant', 'delighted', 'enjoy',
  'excited', 'glad', 'helpful', 'impressive', 'nice', 'perfect', 'pleased',
  'recommend', 'satisfied', 'success', 'thank', 'thanks', 'thrilled', 'win',
  'winning', 'positive', 'trust', 'reliable', 'innovative', 'upgrade',
];

const NEGATIVE_WORDS = [
  'bad', 'angry', 'scam', 'refund', 'delay', 'complaint', 'terrible', 'awful',
  'hate', 'worst', 'broken', 'fail', 'failed', 'failure', 'frustrated', 'angry',
  'disappointed', 'horrible', 'issue', 'problem', 'bug', 'crash', 'lies', 'lie',
  'fraud', 'ripoff', 'sucks', 'useless', 'waste', 'warning', 'avoid', 'boycott',
  'lawsuit', 'unsafe', 'danger', 'risk', 'concern', 'outrage', 'unacceptable',
  'disaster', 'crisis', 'negative', 'poor', 'slow', 'overpriced', 'misleading',
];

export const scoreSentiment = (
  text: string
): { sentiment: SentimentLabel; sentimentScore: number } => {
  const tokens = text.split(/\s+/);
  let positiveHits = 0;
  let negativeHits = 0;

  for (const token of tokens) {
    if (POSITIVE_WORDS.includes(token)) {
      positiveHits += 1;
    }
    if (NEGATIVE_WORDS.includes(token)) {
      negativeHits += 1;
    }
  }

  const rawScore = positiveHits - negativeHits;
  const maxHits = Math.max(positiveHits + negativeHits, 1);
  const sentimentScore = Math.max(-1, Math.min(1, rawScore / maxHits));

  let sentiment: SentimentLabel = 'neutral';
  if (sentimentScore >= 0.2) {
    sentiment = 'positive';
  } else if (sentimentScore <= -0.2) {
    sentiment = 'negative';
  }

  return { sentiment, sentimentScore };
};
