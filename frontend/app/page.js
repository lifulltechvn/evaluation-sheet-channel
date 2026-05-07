"use client";
import { useState, useEffect, useCallback, useMemo } from "react";
import { getUserFromToken } from "./utils/auth";

const API = "/api";
async function api(path, opts) {
  const res = await fetch(`${API}${path}`, { headers: { "Content-Type": "application/json" }, ...opts });
  return res.json();
}

const ALL_TABS = [
  { id: "dashboard", label: "Dashboard", icon: "📊", requirePermission: "view_all" },
  { id: "sheets", label: "Sheets", icon: "📄" },
  { id: "employees", label: "Employees", icon: "👥" },
  { id: "history", label: "History", icon: "📜" },
];

const TAB_TITLES = { dashboard: "Dashboard Overview", sheets: "Evaluation Sheets", employees: "Employee Directory", history: "Evaluation History" };

function Badge({ status }) {
  return (
    <span className={`badge badge-${status}`}>
      <span className={`badge-dot badge-dot-${status}`} />
      {status}
    </span>
  );
}

function PositionTag({ position }) {
  return <span className="position-tag">{position?.replace("_", " ")}</span>;
}

export default function Dashboard() {
  const [permissions, setPermissions] = useState({});
  const [tab, setTab] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [sheets, setSheets] = useState([]);
  const [dashStatus, setDashStatus] = useState({});
  const [toast, setToast] = useState(null);
  const [genPeriod, setGenPeriod] = useState("2026-H1");
  const [history, setHistory] = useState(null);

  const TABS = useMemo(() => {
    return ALL_TABS.filter(t => {
      if (!t.requirePermission) return true;
      return permissions[t.requirePermission] === true;
    });
  }, [permissions]);

  useEffect(() => {
    const user = getUserFromToken();
    setPermissions(user?.permissions || {});
  }, []);

  useEffect(() => {
    if (TABS.length > 0 && tab === null) {
      setTab(TABS[0].id);
    }
  }, [TABS, tab]);

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 3000); };

  const load = useCallback(async () => {
    const [e, s, d] = await Promise.all([api("/employees"), api("/sheets"), api("/dashboard/status")]);
    setEmployees(e.employees || []);
    setSheets(s.sheets || []);
    setDashStatus(d);
  }, []);

  useEffect(() => { load(); }, [load]);

  const generateSheets = async () => {
    const emps = employees.map(e => ({ employee_id: e.employee_id, name: e.name, email: e.email, position: e.position, grade: e.grade }));
    const res = await api("/sheets/generate", { method: "POST", body: JSON.stringify({ period: genPeriod, employees: emps }) });
    showToast(`✅ Generated ${res.sheets_created} sheets`);
    load();
  };

  const sendSheet = async (id) => {
    await api(`/sheets/${id}/send`, { method: "POST" });
    showToast("✉️ Sheet sent!");
    load();
  };

  const validateSheet = async (id) => {
    const res = await api(`/sheets/${id}/validate`, { method: "POST" });
    showToast(`🔍 Validation: ${res.status} (${res.errors?.length || 0} errors)`);
    load();
  };

  const sendResults = async () => {
    const ids = employees.map(e => e.employee_id);
    await api("/notifications/send-results", { method: "POST", body: JSON.stringify({ period: genPeriod, employee_ids: ids }) });
    showToast("✉️ Result emails sent (mock)!");
  };

  const viewHistory = async (empId) => {
    const res = await api(`/employees/${empId}/history`);
    setHistory(res);
    setTab("history");
  };

  const migrate = async () => {
    await api("/sheets/migrate", { method: "POST", body: JSON.stringify({ from_period: "2025-H2", to_period: genPeriod }) });
    showToast("🔄 Migration complete!");
    load();
  };

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">📋</div>
            EvalSheet
          </div>
          <div className="sidebar-subtitle">HR Management System</div>
        </div>
        <nav className="sidebar-nav">
          {TABS.map(t => (
            <button key={t.id} className={`nav-item ${tab === t.id ? "active" : ""}`} onClick={() => setTab(t.id)}>
              <span className="nav-icon">{t.icon}</span>
              {t.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">Team Channel — AI Contest 2026</div>
      </aside>

      {/* Main */}
      <main className="main">
        <div className="topbar">
          <div className="topbar-title">{TAB_TITLES[tab]}</div>
          <span className="topbar-badge">🔶 Demo Mode</span>
        </div>

        <div className="content">
          {/* Dashboard */}
          {tab === "dashboard" && (
            <>
              <div className="stats-grid">
                <div className="stat-card primary">
                  <div className="stat-label">Total Sheets</div>
                  <div className="stat-value primary">{dashStatus.total_sheets || 0}</div>
                </div>
                {Object.entries(dashStatus.by_status || {}).map(([k, v]) => (
                  <div key={k} className={`stat-card ${k === "created" ? "primary" : k === "sent" ? "warning" : "success"}`}>
                    <div className="stat-label">{k}</div>
                    <div className={`stat-value ${k === "created" ? "primary" : k === "sent" ? "warning" : "success"}`}>{v}</div>
                  </div>
                ))}
                <div className="stat-card">
                  <div className="stat-label">Employees</div>
                  <div className="stat-value">{employees.length}</div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <div className="card-title">⚡ Quick Actions</div>
                </div>
                <div className="card-body">
                  <div className="actions-bar">
                    <select className="select" value={genPeriod} onChange={e => setGenPeriod(e.target.value)}>
                      <option>2026-H1</option><option>2026-H2</option><option>2025-H2</option>
                    </select>
                    <button className="btn btn-primary" onClick={generateSheets}>📄 Generate All Sheets</button>
                    <button className="btn btn-success" onClick={sendResults}>✉️ Send Results Email</button>
                    <button className="btn btn-warning" onClick={migrate}>🔄 Migrate from 2025-H2</button>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Sheets */}
          {tab === "sheets" && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">Evaluation Sheets</div>
                <span style={{ fontSize: 13, color: "var(--gray-400)" }}>{sheets.length} total</span>
              </div>
              {sheets.length === 0 ? (
                <div className="empty">
                  <div className="empty-icon">📄</div>
                  <div className="empty-text">No sheets yet. Go to Dashboard → Generate All Sheets.</div>
                </div>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Sheet ID</th><th>Employee</th><th>Position</th><th>Grade</th><th>Period</th><th>Status</th><th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sheets.map(s => (
                        <tr key={s.sheet_id}>
                          <td><code className="code">{s.sheet_id}</code></td>
                          <td style={{ fontWeight: 600 }}>{s.employee_name}</td>
                          <td><PositionTag position={s.position} /></td>
                          <td><strong>{s.grade}</strong></td>
                          <td>{s.period}</td>
                          <td><Badge status={s.status} /></td>
                          <td>
                            <div className="actions-bar">
                              <button className="btn btn-primary btn-sm" onClick={() => sendSheet(s.sheet_id)}>✉️ Send</button>
                              <button className="btn btn-success btn-sm" onClick={() => validateSheet(s.sheet_id)}>✓ Validate</button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Employees */}
          {tab === "employees" && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">Employee Directory</div>
                <span style={{ fontSize: 13, color: "var(--gray-400)" }}>{employees.length} employees</span>
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Team</th><th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {employees.map(e => (
                      <tr key={e.id}>
                        <td><code className="code">{e.id}</code></td>
                        <td style={{ fontWeight: 600 }}>{e.full_name}</td>
                        <td style={{ color: "var(--gray-500)" }}>{e.email}</td>
                        <td><span className="position-tag">{e.role}</span></td>
                        <td>{e.team || "—"}</td>
                        <td><Badge status={e.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* History */}
          {tab === "history" && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">Evaluation History {history ? `— ${history.employee_id}` : ""}</div>
              </div>
              {!history || history.history?.length === 0 ? (
                <div className="empty">
                  <div className="empty-icon">📜</div>
                  <div className="empty-text">No history available. Select an employee from the Employees tab.</div>
                </div>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr><th>Period</th><th>Grade</th><th>Position</th><th>Score</th><th>Sheet</th></tr>
                    </thead>
                    <tbody>
                      {(history.history || []).map((h, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 600 }}>{h.period}</td>
                          <td><strong>{h.grade}</strong></td>
                          <td><PositionTag position={h.position} /></td>
                          <td><span style={{ fontSize: 18, fontWeight: 700, color: "var(--primary)" }}>{h.total_score}</span></td>
                          <td><a href={h.google_sheet_url} target="_blank" rel="noreferrer" className="link">Open Sheet ↗</a></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {toast && <div className="toast">✓ {toast}</div>}
    </div>
  );
}
