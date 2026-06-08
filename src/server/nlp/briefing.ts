import type { AnalyzeResponse, KeywordCount } from '../../shared/types';
import type { CollectParams } from './types';
import type { EnrichedPost } from './types';

type BriefingInput = {
  params: CollectParams;
  posts: EnrichedPost[];
  crisis: AnalyzeResponse['crisis'];
  topKeywords: KeywordCount[];
  trends: AnalyzeResponse['trends'];
};

export const buildBriefing = (input: BriefingInput): AnalyzeResponse['briefing'] => {
  const { params, posts, crisis, topKeywords, trends } = input;
  const negativePosts = posts.filter((p) => p.sentiment === 'negative');
  const keywordList = topKeywords.slice(0, 5).map((k) => k.keyword).join(', ');

  const mainConcerns =
    crisis.reasons.length > 0
      ? crisis.reasons.slice(0, 4)
      : ['Limited negative signals in the current sample'];

  const recommendedActions: string[] = [];
  if (crisis.crisis_score >= 61) {
    recommendedActions.push('Prepare a public response addressing top complaints');
    recommendedActions.push('Monitor high-impact negative threads closely');
  } else if (crisis.crisis_score >= 31) {
    recommendedActions.push('Track recurring themes and respond to top threads');
  } else {
    recommendedActions.push('Continue routine monitoring');
  }
  recommendedActions.push('Validate findings with human review before acting');

  return {
    executive_summary: `Analysis of ${posts.length} Reddit posts about "${params.query}" in r/${params.subreddit} shows a crisis score of ${crisis.crisis_score} (${crisis.risk_level}). Top themes: ${keywordList || 'none identified'}.`,
    main_concerns: mainConcerns,
    crisis_explanation: `Crisis score combines negative sentiment (${crisis.components.negative_ratio ?? 0} pts), risk keywords (${crisis.components.risk_keywords ?? 0} pts), and engagement-weighted negative posts (${crisis.components.high_impact_negative ?? 0} pts).${trends.spike_detected ? ` ${trends.spike_message}` : ''}`,
    recommended_actions: recommendedActions,
    communication_strategy:
      negativePosts.length > posts.length * 0.3
        ? 'Acknowledge concerns transparently, share corrective actions, and avoid dismissive tone.'
        : 'Highlight positive feedback while noting areas for improvement.',
    ethics_notice:
      'Automated sentiment and crisis scores are indicative only. Do not use for individual targeting or moderation decisions without human oversight.',
    source: 'rule-based',
  };
};
