import { FormEvent, useState } from 'react';
import { useQualityFeedbackMutation } from '../api/workspaceM4Queries';
import type { QualityFeedbackRequest } from '../types/api';
import { ApiErrorState } from './ApiErrorState';

type FeedbackTarget = Omit<QualityFeedbackRequest, 'rating' | 'comment'>;

export function LightweightFeedback({ workspaceId, target }: { workspaceId: string; target: FeedbackTarget }) {
  const [comment, setComment] = useState('');
  const [submittedRating, setSubmittedRating] = useState<QualityFeedbackRequest['rating'] | null>(null);
  const feedback = useQualityFeedbackMutation(workspaceId);

  const submit = (rating: QualityFeedbackRequest['rating']) => (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    feedback.mutate(
      {
        ...target,
        rating,
        comment: comment.trim() || undefined
      },
      {
        onSuccess: () => {
          setSubmittedRating(rating);
          setComment('');
        }
      }
    );
  };

  return (
    <div className="feedback-box" aria-label="轻量反馈">
      <div className="workspace-meta">反馈</div>
      <div className="feedback-actions">
        <form onSubmit={submit('up')}>
          <input type="hidden" name="rating" value="up" />
          <button className="secondary-button" type="submit" disabled={feedback.isPending}>
            有帮助
          </button>
        </form>
        <form onSubmit={submit('down')}>
          <input type="hidden" name="rating" value="down" />
          <button className="secondary-button" type="submit" disabled={feedback.isPending}>
            需要改进
          </button>
        </form>
      </div>
      <label>
        <span className="field-label">备注</span>
        <input
          className="text-input"
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="可选反馈"
        />
      </label>
      {submittedRating ? <p className="workspace-meta">反馈已提交：{submittedRating === 'up' ? '有帮助' : '需要改进'}</p> : null}
      {feedback.error ? <ApiErrorState title="反馈提交失败" error={feedback.error} /> : null}
    </div>
  );
}
