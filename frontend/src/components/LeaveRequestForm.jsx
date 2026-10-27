import { useState } from "react";
import { REASON_MAX_LENGTH, REASON_MIN_LENGTH, todayIso } from "../utils.js";

const LEAVE_TYPES = ["Annual", "Sick", "Casual"];

function emptyForm() {
  return {
    employee_id: "",
    leave_type: "Annual",
    start_date: "",
    end_date: "",
    reason: "",
  };
}

function validate(form) {
  const errors = {};
  const reasonLength = form.reason.trim().length;

  if (!form.employee_id) {
    errors.employee_id = "Select an employee.";
  }
  if (!form.start_date) {
    errors.start_date = "Choose a start date.";
  } else if (form.start_date < todayIso()) {
    errors.start_date = "Start date cannot be in the past.";
  }
  if (!form.end_date) {
    errors.end_date = "Choose an end date.";
  } else if (form.start_date && form.end_date < form.start_date) {
    errors.end_date = "End date cannot be earlier than start date.";
  }
  if (reasonLength < REASON_MIN_LENGTH || reasonLength > REASON_MAX_LENGTH) {
    errors.reason = `Reason must be between ${REASON_MIN_LENGTH} and ${REASON_MAX_LENGTH} characters.`;
  }
  return errors;
}

export default function LeaveRequestForm({ employees, onSubmit }) {
  const [form, setForm] = useState(emptyForm);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setServerError("");

    const validationErrors = validate(form);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({ ...form, reason: form.reason.trim() });
      setForm(emptyForm());
      setErrors({});
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  const reasonLength = form.reason.trim().length;

  return (
    <form className="form" onSubmit={handleSubmit} noValidate>
      <div className="field">
        <label htmlFor="employee_id">Employee</label>
        <select id="employee_id" name="employee_id" value={form.employee_id} onChange={updateField}>
          <option value="">Select an employee</option>
          {employees.map((employee) => (
            <option key={employee.id} value={employee.id}>
              {employee.name}
            </option>
          ))}
        </select>
        {errors.employee_id && <p className="field-error">{errors.employee_id}</p>}
      </div>

      <div className="field">
        <label htmlFor="leave_type">Leave type</label>
        <select id="leave_type" name="leave_type" value={form.leave_type} onChange={updateField}>
          {LEAVE_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="start_date">Start date</label>
          <input
            id="start_date"
            name="start_date"
            type="date"
            min={todayIso()}
            value={form.start_date}
            onChange={updateField}
          />
          {errors.start_date && <p className="field-error">{errors.start_date}</p>}
        </div>

        <div className="field">
          <label htmlFor="end_date">End date</label>
          <input
            id="end_date"
            name="end_date"
            type="date"
            min={form.start_date || todayIso()}
            value={form.end_date}
            onChange={updateField}
          />
          {errors.end_date && <p className="field-error">{errors.end_date}</p>}
        </div>
      </div>

      <div className="field">
        <label htmlFor="reason">
          Reason{" "}
          <span className="muted small">
            ({reasonLength}/{REASON_MAX_LENGTH})
          </span>
        </label>
        <textarea
          id="reason"
          name="reason"
          rows={3}
          value={form.reason}
          onChange={updateField}
          placeholder={`${REASON_MIN_LENGTH} to ${REASON_MAX_LENGTH} characters`}
        />
        {errors.reason && <p className="field-error">{errors.reason}</p>}
      </div>

      {serverError && (
        <div className="banner banner-error" role="alert">
          {serverError}
        </div>
      )}

      <div className="form-actions">
        <button type="submit" className="primary" disabled={submitting}>
          {submitting ? "Submitting…" : "Submit request"}
        </button>
      </div>
    </form>
  );
}
