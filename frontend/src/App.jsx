import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "./api.js";
import EmployeeBalances from "./components/EmployeeBalances.jsx";
import LeaveRequestFilters from "./components/LeaveRequestFilters.jsx";
import LeaveRequestForm from "./components/LeaveRequestForm.jsx";
import LeaveRequestTable from "./components/LeaveRequestTable.jsx";
import ReviewDialog from "./components/ReviewDialog.jsx";
import SummaryCards from "./components/SummaryCards.jsx";

const EMPTY_FILTERS = {
  status: "",
  employee_id: "",
  employee_name: "",
  from_date: "",
  to_date: "",
};

const LOADING = { loading: true, error: "" };
const READY = { loading: false, error: "" };

function failed(err) {
  return { loading: false, error: err.message };
}

export default function App() {
  const [employees, setEmployees] = useState([]);
  const [employeesState, setEmployeesState] = useState(LOADING);

  const [summary, setSummary] = useState(null);
  const [summaryState, setSummaryState] = useState(LOADING);

  const [requests, setRequests] = useState([]);
  const [requestsState, setRequestsState] = useState(LOADING);

  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [feedback, setFeedback] = useState(null);
  const [reviewTarget, setReviewTarget] = useState(null);

  // Ignores responses to older filter values so a slow request cannot overwrite a newer one.
  const latestRequestId = useRef(0);

  const loadEmployees = useCallback(async () => {
    setEmployeesState(LOADING);
    try {
      setEmployees(await api.listEmployees());
      setEmployeesState(READY);
    } catch (err) {
      setEmployeesState(failed(err));
    }
  }, []);

  const loadSummary = useCallback(async () => {
    setSummaryState(LOADING);
    try {
      setSummary(await api.getSummary());
      setSummaryState(READY);
    } catch (err) {
      setSummaryState(failed(err));
    }
  }, []);

  const loadRequests = useCallback(async (activeFilters) => {
    const requestId = ++latestRequestId.current;
    setRequestsState(LOADING);
    try {
      const data = await api.listLeaveRequests(activeFilters);
      if (requestId === latestRequestId.current) {
        setRequests(data);
        setRequestsState(READY);
      }
    } catch (err) {
      if (requestId === latestRequestId.current) {
        setRequestsState(failed(err));
      }
    }
  }, []);

  // Balances and summary change whenever a request changes, so refresh everything together.
  const refreshAll = useCallback(async () => {
    await Promise.all([loadEmployees(), loadSummary(), loadRequests(filters)]);
  }, [filters, loadEmployees, loadSummary, loadRequests]);

  useEffect(() => {
    loadEmployees();
    loadSummary();
  }, [loadEmployees, loadSummary]);

  useEffect(() => {
    loadRequests(filters);
  }, [filters, loadRequests]);

  async function handleCreate(payload) {
    await api.createLeaveRequest(payload);
    setFeedback({ type: "success", message: "Leave request submitted and pending review." });
    await refreshAll();
  }

  async function handleReviewConfirm(comment) {
    const { request, action } = reviewTarget;
    if (action === "approve") {
      await api.approveLeaveRequest(request.id, comment);
    } else {
      await api.rejectLeaveRequest(request.id, comment);
    }
    setReviewTarget(null);
    setFeedback({
      type: "success",
      message: `${request.id} ${action === "approve" ? "approved" : "rejected"}.`,
    });
    await refreshAll();
  }

  async function handleCancel(request) {
    if (!window.confirm(`Cancel leave request ${request.id}?`)) {
      return;
    }
    try {
      await api.cancelLeaveRequest(request.id);
      setFeedback({ type: "success", message: `${request.id} cancelled.` });
      await refreshAll();
    } catch (err) {
      setFeedback({ type: "error", message: err.message });
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Leave Requests</h1>
        <p>Submit leave, filter requests, and review pending applications.</p>
      </header>

      {feedback && (
        <div className={`banner banner-${feedback.type}`} role="status">
          <span>{feedback.message}</span>
          <button type="button" className="link-button" onClick={() => setFeedback(null)}>
            Dismiss
          </button>
        </div>
      )}

      <SummaryCards summary={summary} state={summaryState} onRetry={loadSummary} />

      <div className="two-column">
        <section className="card">
          <h2>Submit a leave request</h2>
          <LeaveRequestForm employees={employees} onSubmit={handleCreate} />
        </section>

        <section className="card">
          <h2>Leave balances</h2>
          <EmployeeBalances employees={employees} state={employeesState} onRetry={loadEmployees} />
        </section>
      </div>

      <section className="card">
        <h2>Requests</h2>
        <LeaveRequestFilters
          employees={employees}
          filters={filters}
          onChange={setFilters}
          onClear={() => setFilters(EMPTY_FILTERS)}
        />
        <LeaveRequestTable
          requests={requests}
          state={requestsState}
          hasFilters={Object.values(filters).some(Boolean)}
          onRetry={() => loadRequests(filters)}
          onApprove={(request) => setReviewTarget({ request, action: "approve" })}
          onReject={(request) => setReviewTarget({ request, action: "reject" })}
          onCancel={handleCancel}
        />
      </section>

      {reviewTarget && (
        <ReviewDialog
          request={reviewTarget.request}
          action={reviewTarget.action}
          onConfirm={handleReviewConfirm}
          onClose={() => setReviewTarget(null)}
        />
      )}
    </div>
  );
}
