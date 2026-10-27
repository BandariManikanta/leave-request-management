import { useState } from "react";

export default function ReviewDialog({ request, action, onConfirm, onClose }) {
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const isReject = action === "reject";
  const title = isReject ? "Reject leave request" : "Approve leave request";

  async function handleConfirm() {
    setError("");
    const trimmed = comment.trim();
    if (isReject && !trimmed) {
      setError("A reviewer comment is required when rejecting a request.");
      return;
    }

    setSubmitting(true);
    try {
      await onConfirm(trimmed);
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="review-title"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id="review-title">{title}</h2>
        <p className="muted">
          {request.id} · {request.employee_name} · {request.start_date} to {request.end_date} (
          {request.number_of_days} days)
        </p>

        <div className="field">
          <label htmlFor="review-comment">
            {isReject ? "Reviewer comment (required)" : "Reviewer comment (optional)"}
          </label>
          <textarea
            id="review-comment"
            rows={3}
            value={comment}
            onChange={(event) => setComment(event.target.value)}
            autoFocus
          />
        </div>

        {error && (
          <div className="banner banner-error" role="alert">
            {error}
          </div>
        )}

        <div className="form-actions">
          <button type="button" onClick={onClose} disabled={submitting}>
            Cancel
          </button>
          <button
            type="button"
            className={isReject ? "danger" : "primary"}
            onClick={handleConfirm}
            disabled={submitting}
          >
            {submitting ? "Saving…" : isReject ? "Reject request" : "Approve request"}
          </button>
        </div>
      </div>
    </div>
  );
}
