const BASE_URL = "/api";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function extractMessage(body, status) {
  if (typeof body?.detail === "string") {
    return body.detail;
  }
  // FastAPI validation errors arrive as a list of { loc, msg } objects.
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item) => `${item.loc.at(-1)}: ${item.msg}`).join(" ");
  }
  return `Request failed with status ${status}.`;
}

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (response.status === 204) {
    return null;
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(extractMessage(body, response.status), response.status);
  }
  return body;
}

function toQueryString(filters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });
  return params.toString();
}

export const api = {
  listEmployees: () => request("/employees"),

  listLeaveRequests: (filters) => request(`/leave-requests?${toQueryString(filters)}`),

  getSummary: () => request("/leave-requests/summary"),

  createLeaveRequest: (payload) =>
    request("/leave-requests", { method: "POST", body: JSON.stringify(payload) }),

  approveLeaveRequest: (id, comment) =>
    request(`/leave-requests/${id}/approve`, {
      method: "POST",
      body: JSON.stringify({ comment: comment || null }),
    }),

  rejectLeaveRequest: (id, comment) =>
    request(`/leave-requests/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ comment }),
    }),

  cancelLeaveRequest: (id) => request(`/leave-requests/${id}`, { method: "DELETE" }),
};
