const STATUS_CARDS = [
  { key: "Pending", label: "Pending" },
  { key: "Approved", label: "Approved" },
  { key: "Rejected", label: "Rejected" },
];

export default function SummaryCards({ summary, state, onRetry }) {
  if (state.error) {
    return (
      <div className="banner banner-error">
        <span>Could not load summary: {state.error}</span>
        <button type="button" className="link-button" onClick={onRetry}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="summary-grid">
      <div className="stat-card">
        <span className="stat-label">Total</span>
        <span className="stat-value">{summary ? summary.total : "—"}</span>
      </div>
      {STATUS_CARDS.map(({ key, label }) => (
        <div className="stat-card" key={key}>
          <span className="stat-label">{label}</span>
          <span className="stat-value">
            {summary ? summary.by_status[key] : "—"}
          </span>
        </div>
      ))}
    </div>
  );
}
