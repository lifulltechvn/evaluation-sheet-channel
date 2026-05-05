"use client";
import { useState, useEffect } from "react";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("/api/employees")
      .then((r) => r.json())
      .then((data) => setEmployees(data.employees || []));
  }, []);

  const filtered = employees.filter(
    (e) =>
      e.full_name.toLowerCase().includes(search.toLowerCase()) ||
      e.email.toLowerCase().includes(search.toLowerCase()) ||
      (e.team || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">📋</div>
            EvalSheet
          </div>
          <div className="sidebar-subtitle">HR Management System</div>
        </div>
        <nav className="sidebar-nav">
          <a href="/" className="nav-item">
            <span className="nav-icon">📊</span>Dashboard
          </a>
          <a href="/employees" className="nav-item active">
            <span className="nav-icon">👥</span>Employees (DB)
          </a>
        </nav>
        <div className="sidebar-footer">Team Channel — AI Contest 2026</div>
      </aside>

      <main className="main">
        <div className="topbar">
          <div className="topbar-title">Employee Directory (from Database)</div>
          <span className="topbar-badge">🟢 Live DB</span>
        </div>

        <div className="content">
          <div className="card">
            <div className="card-header">
              <div className="card-title">Employees</div>
              <input
                className="select"
                placeholder="Search by name, email, or team..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{ minWidth: 260 }}
              />
            </div>
            <div style={{ padding: "0 4px 8px", fontSize: 13, color: "var(--gray-400)" }}>
              {filtered.length} of {employees.length} employees
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Full Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Team</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((e) => (
                    <tr key={e.id}>
                      <td><code className="code">{e.id}</code></td>
                      <td style={{ fontWeight: 600 }}>{e.full_name}</td>
                      <td style={{ color: "var(--gray-500)" }}>{e.email}</td>
                      <td><span className="position-tag">{e.role}</span></td>
                      <td>{e.team || "—"}</td>
                      <td><span className={`badge badge-${e.status}`}><span className={`badge-dot badge-dot-${e.status}`} />{e.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
