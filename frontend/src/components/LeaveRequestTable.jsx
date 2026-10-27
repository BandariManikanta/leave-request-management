const STATUS_CLASS = {
  Pending: "badge badge-pending",
  Approved: "badge badge-approved",
  Rejected: "badge badge-rejected",
};

export default function LeaveRequestTable({
  requests,
  state,
  hasFilters,
  onRetry,
  onApprove,
  onReject,
  onCancel,
}) {
  if (state.loading && requests.length === 0) {
    return <p className="muted">Loading leave requests…</p>;
  }

  if (state.error) {
    return (
      <div className="banner banner-error">
        <span>{state.error}</span>
        <button type="button" className="link-button" onClick={onRetry}>
          Retry
        </button>
      </div>
    );
  }

  if (requests.length === 0) {
    return (
      <p className="muted empty-state">
        {hasFilters ? "No leave requests match the selected filters." : "No leave requests yet."}
      </p>
    );
  }

  return (
    <div className="table-wrapper">
      {state.loading && <p className="muted small">Refreshing…</p>}
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Employee</th>
            <th>Type</th>
            <th>Dates</th>
            <th className="num">Days</th>
            <th className="num">Working days</th>
            <th>Reason</th>
            <th>Status</th>
            <th>Reviewer comment</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((request) => (
            <tr key={request.id}>
              <td>{request.id}</td>
              <td>{request.employee_name}</td>
              <td>{request.leave_type}</td>
              <td className="nowrap">
                {request.start_date} to {request.end_date}
              </td>
              <td className="num">{request.number_of_days}</td>
              <td className="num">{request.working_days}</td>
              <td className="wrap">{request.reason}</td>
              <td>
                <span className={STATUS_CLASS[request.status]}>{request.status}</span>
              </td>
              <td className="wrap">{request.reviewer_comment || <span className="muted">—</span>}</td>
              <td className="actions">
                {request.status === "Pending" ? (
                  <>
                    <button type="button" className="primary small-button" onClick={() => onApprove(request)}>
                      Approve
                    </button>
                    <button type="button" className="danger small-button" onClick={() => onReject(request)}>
                      Reject
                    </button>
                    <button type="button" className="small-button" onClick={() => onCancel(request)}>
                      Cancel
                    </button>
                  </>
                ) : (
                  <span className="muted small">No actions</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
