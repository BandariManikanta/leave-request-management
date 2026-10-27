export default function LeaveRequestFilters({ employees, filters, onChange, onClear }) {
  function updateField(event) {
    const { name, value } = event.target;
    onChange({ ...filters, [name]: value });
  }

  return (
    <div className="filters">
      <div className="field">
        <label htmlFor="filter-employee">Employee</label>
        <select id="filter-employee" name="employee_id" value={filters.employee_id} onChange={updateField}>
          <option value="">All employees</option>
          {employees.map((employee) => (
            <option key={employee.id} value={employee.id}>
              {employee.name}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="filter-status">Status</label>
        <select id="filter-status" name="status" value={filters.status} onChange={updateField}>
          <option value="">All statuses</option>
          <option value="Pending">Pending</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>

      <div className="field">
        <label htmlFor="filter-name">Search by name</label>
        <input
          id="filter-name"
          name="employee_name"
          type="search"
          value={filters.employee_name}
          onChange={updateField}
          placeholder="e.g. Asha"
        />
      </div>

      <div className="field">
        <label htmlFor="filter-from">From</label>
        <input id="filter-from" name="from_date" type="date" value={filters.from_date} onChange={updateField} />
      </div>

      <div className="field">
        <label htmlFor="filter-to">To</label>
        <input id="filter-to" name="to_date" type="date" value={filters.to_date} onChange={updateField} />
      </div>

      <div className="filters-clear">
        <button type="button" onClick={onClear}>
          Clear filters
        </button>
      </div>
    </div>
  );
}
