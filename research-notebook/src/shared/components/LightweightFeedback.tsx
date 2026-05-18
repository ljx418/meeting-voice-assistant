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
    <div className="feedback-box" aria-label="Lightweight feedback">
      <div className="workspace-meta">Feedback</div>
      <div className="feedback-actions">
        <form onSubmit={submit('up')}>
          <input type="hidden" name="rating" value="up" />
          <button className="secondary-button" type="submit" disabled={feedback.isPending}>
            Helpful
          </button>
        </form>
        <form onSubmit={submit('down')}>
          <input type="hidden" name="rating" value="down" />
          <button className="secondary-button" type="submit" disabled={feedback.isPending}>
            Needs work
          </button>
        </form>
      </div>
      <label>
        <span className="field-label">Comment</span>
        <input
          className="text-input"
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="Optional feedback"
        />
      </label>
      {submittedRating ? <p className="workspace-meta">Feedback submitted: {submittedRating}</p> : null}
      {feedback.error ? <ApiErrorState title="Feedback submit failed" error={feedback.error} /> : null}
    </div>
  );
}
