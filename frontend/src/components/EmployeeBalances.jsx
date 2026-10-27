export default function EmployeeBalances({ employees, state, onRetry }) {
  if (state.loading && employees.length === 0) {
    return <p className="muted">Loading balances…</p>;
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

  if (employees.length === 0) {
    return <p className="muted">No employees found.</p>;
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Employee</th>
            <th className="num">Balance</th>
            <th className="num">Pending</th>
            <th className="num">Available</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((employee) => (
            <tr key={employee.id}>
              <td>
                <div>{employee.name}</div>
                <div className="muted small">{employee.email}</div>
              </td>
              <td className="num">{employee.leave_balance} d</td>
              <td className="num">{employee.pending_days} d</td>
              <td className="num strong">{employee.available_balance} d</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
