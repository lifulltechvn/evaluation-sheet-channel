"use client";
import { useState, useEffect, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import { getUserFromToken, clearAuth } from "./utils/auth";

const API = "/api";
async function api(path, opts = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const headers = { "Content-Type": "application/json", ...(token && { Authorization: `Bearer ${token}` }), ...opts.headers };
  const res = await fetch(`${API}${path}`, { ...opts, headers });
  return res.json();
}

const ALL_TABS = [
  { id: "dashboard", label: "Dashboard", icon: "📊", requirePermission: "view_all" },
  { id: "sheets", label: "Sheets", icon: "📄", requirePermission: "view_all" },
  { id: "self-assessment", label: "Self Assessment", icon: "✍️" },
  { id: "employees", label: "Employees", icon: "👥", requirePermission: "view_all" },
  { id: "history", label: "History", icon: "📜" },
];

const TAB_TITLES = { dashboard: "Dashboard Overview", sheets: "Evaluation Sheets", "self-assessment": "Self Assessment", employees: "Employee Directory", history: "Evaluation History" };

const STATUS_LABELS = {
  Self_Evaluating: "Employee self-assessment",
  Leader_Reviewing: "Leader Manager Approved",
  Manager_Reviewing: "Unit Manager Confirmation",
  Completed: "Division Manager Approved",
};

function Badge({ status }) {
  const label = STATUS_LABELS[status] || status;
  return (
    <span className={`badge badge-${status}`}>
      <span className={`badge-dot badge-dot-${status}`} />
      {label}
    </span>
  );
}

function PositionTag({ position }) {
  return <span className="position-tag">{position?.replace("_", " ")}</span>;
}

export default function Dashboard() {
  const router = useRouter();
  const [permissions, setPermissions] = useState({});
  const [currentUser, setCurrentUser] = useState(null);
  const [tab, setTab] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [sheets, setSheets] = useState([]);
  const [dashStatus, setDashStatus] = useState({});
  const [toast, setToast] = useState(null);
  const [genPeriod, setGenPeriod] = useState("");
  const [periods, setPeriods] = useState([]);
  const [history, setHistory] = useState(null);
  const [genProgress, setGenProgress] = useState(null); // {current, total, name}
  const [mySheets, setMySheets] = useState([]);
  const [myPeriodName, setMyPeriodName] = useState(null);
  const [sheetSearch, setSheetSearch] = useState("");
  const [sheetStatusFilter, setSheetStatusFilter] = useState("");
  const [sheetTeamFilter, setSheetTeamFilter] = useState("");

  const TABS = useMemo(() => {
    return ALL_TABS.filter(t => {
      if (!t.requirePermission) return true;
      return permissions[t.requirePermission] === true;
    });
  }, [permissions]);

  useEffect(() => {
    const user = getUserFromToken();
    setPermissions(user?.permissions || {});
    setCurrentUser(user);
  }, []);

  useEffect(() => {
    if (TABS.length > 0 && tab === null) {
      setTab(TABS[0].id);
    }
  }, [TABS, tab]);

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 3000); };

  const load = useCallback(async () => {
    const [e, s, p] = await Promise.all([api("/employees"), api("/sheets"), api("/periods")]);
    setEmployees(e.employees || []);
    setSheets(s.sheets || []);
    const periodList = Array.isArray(p) ? p : [];
    setPeriods(periodList);
    if (periodList.length > 0 && !genPeriod) setGenPeriod(periodList[0].id);
  }, []);

  const loadDashboard = useCallback(async (periodId) => {
    const d = await api(`/dashboard/status${periodId ? `?period_id=${periodId}` : ""}`);
    setDashStatus(d);
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (genPeriod) loadDashboard(genPeriod);
  }, [genPeriod, loadDashboard]);

  const loadMySheets = useCallback(async () => {
    const res = await api("/sheets/me");
    setMySheets(res.sheets || []);
    setMyPeriodName(res.period_name || null);
  }, []);

  useEffect(() => {
    if (tab === "self-assessment") loadMySheets();
  }, [tab, loadMySheets]);

  const generateSheets = async () => {
    const token = localStorage.getItem("access_token");
    setGenProgress({ current: 0, total: 0, name: "Checking..." });
    try {
      const backendUrl = window.location.origin.replace(":3000", ":8000");
      const res = await fetch(`${backendUrl}/v1/sheets/generate-stream?period_id=${genPeriod}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop();
        for (const line of lines) {
          const data = line.replace("data: ", "");
          if (!data) continue;
          const evt = JSON.parse(data);
          if (evt.type === "start") setGenProgress({ current: 0, total: evt.total, name: "Checking..." });
          else if (evt.type === "skipped") setGenProgress({ current: evt.current, total: evt.total, name: `⏭️ ${evt.name} (exists)` });
          else if (evt.type === "progress") setGenProgress({ current: evt.current, total: evt.total, name: `✅ ${evt.name}` });
          else if (evt.type === "done") {
            showToast(`✅ Generated ${evt.sheets_created} sheets` + (evt.skipped ? ` (${evt.skipped} skipped)` : ""));
          }
        }
      }
    } catch (e) {
      showToast("❌ Generation failed");
    }
    setGenProgress(null);
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

  const [historySource, setHistorySource] = useState(null); // "menu" or "employee"

  const viewHistory = async (empId) => {
    const res = await api(`/employees/${empId}/history`);
    setHistory(res);
    setHistorySource("employee");
    setTab("history");
  };

  const loadMyHistory = useCallback(async () => {
    const res = await api("/employees/me/history");
    setHistory(res);
  }, []);

  useEffect(() => {
    if (tab === "history" && historySource !== "employee") {
      loadMyHistory();
    }
    if (tab !== "history") {
      setHistorySource(null);
    }
  }, [tab, historySource, loadMyHistory]);

  const migrate = async () => {
    await api("/sheets/migrate", { method: "POST", body: JSON.stringify({ from_period: "2025-H2", to_period: genPeriod }) });
    showToast("🔄 Migration complete!");
    load();
  };

  const handleLogout = () => {
    clearAuth();
    router.replace("/login");
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
        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>🚪 Đăng xuất</button>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        <div className="topbar">
          <div className="topbar-title">{TAB_TITLES[tab]}</div>
          <div className="topbar-right">
            <span className="topbar-badge">🔶 Demo Mode</span>
            {currentUser && <span className="topbar-user">👤 {currentUser.email} ({currentUser.role})</span>}
          </div>
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
                      {periods.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                    </select>
                    <button className="btn btn-primary" onClick={generateSheets} disabled={!!genProgress}>
                      {genProgress ? "⏳ Generating..." : "📄 Generate All Sheets"}
                    </button>
                    <button className="btn btn-success" onClick={sendResults}>✉️ Send Results Email</button>
                    <button className="btn btn-warning" onClick={migrate}>🔄 Migrate from 2025-H2</button>
                  </div>
                  {genProgress && (
                    <div style={{ marginTop: 12 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
                        <span>{genProgress.name}</span>
                        <span>{genProgress.current}/{genProgress.total}</span>
                      </div>
                      <div style={{ background: "var(--gray-100)", borderRadius: 6, height: 8, overflow: "hidden" }}>
                        <div style={{ width: `${genProgress.total ? (genProgress.current / genProgress.total) * 100 : 0}%`, height: "100%", background: "var(--primary)", borderRadius: 6, transition: "width 0.2s" }} />
                      </div>
                    </div>
                  )}
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
              <div className="card-body" style={{ paddingBottom: 0 }}>
                <div className="actions-bar" style={{ marginBottom: 12 }}>
                  <div className="search-wrapper">
                    <span className="search-icon">🔍</span>
                    <input
                      type="text"
                      className="search-input"
                      placeholder="Search by name..."
                      value={sheetSearch}
                      onChange={e => setSheetSearch(e.target.value)}
                    />
                  </div>
                  <select className="select" value={sheetStatusFilter} onChange={e => setSheetStatusFilter(e.target.value)}>
                    <option value="">All Status</option>
                    {Object.entries(STATUS_LABELS).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                  <select className="select" value={sheetTeamFilter} onChange={e => setSheetTeamFilter(e.target.value)}>
                    <option value="">All Teams</option>
                    {[...new Set(sheets.map(s => s.team).filter(t => t && t !== "—"))].sort().map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
              </div>
              {(() => {
                const filtered = sheets.filter(s => {
                  if (sheetSearch && !s.employee_name.toLowerCase().includes(sheetSearch.toLowerCase())) return false;
                  if (sheetStatusFilter && s.status !== sheetStatusFilter) return false;
                  if (sheetTeamFilter && s.team !== sheetTeamFilter) return false;
                  return true;
                });
                return filtered.length === 0 ? (
                  <div className="empty">
                    <div className="empty-icon">📄</div>
                    <div className="empty-text">No sheets found.</div>
                  </div>
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Sheet ID</th><th>Employee</th><th>Team</th><th>Position</th><th>Grade</th><th>Period</th><th>Status</th><th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filtered.map(s => (
                          <tr key={s.sheet_id}>
                            <td><code className="code">{s.sheet_id}</code></td>
                            <td style={{ fontWeight: 600 }}>{s.employee_name}</td>
                            <td>{s.team}</td>
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
                );
              })()}
            </div>
          )}

          {/* Self Assessment */}
          {tab === "self-assessment" && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">My Evaluation Sheets {myPeriodName ? `— ${myPeriodName}` : ""}</div>
              </div>
              {mySheets.length === 0 ? (
                <div className="empty">
                  <div className="empty-icon">✍️</div>
                  <div className="empty-text">No evaluation sheets assigned to you yet.</div>
                </div>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Status</th><th>Score</th><th>Rank</th><th>Sheet</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mySheets.map(s => (
                        <tr key={s.sheet_id}>
                          <td><Badge status={s.status} /></td>
                          <td><span style={{ fontSize: 18, fontWeight: 700, color: "var(--primary)" }}>{s.final_score ?? "—"}</span></td>
                          <td><strong>{s.rank || "—"}</strong></td>
                          <td><a href={s.spreadsheet_url} target="_blank" rel="noreferrer" className="link">Open Sheet ↗</a></td>
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
                      <th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Team</th><th>Status</th><th>Actions</th>
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
                        <td><button className="btn btn-primary btn-sm" onClick={() => viewHistory(e.id)}>📜 History</button></td>
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
                <div className="card-title">Evaluation History {history ? `— ${history.employee_name || history.employee_id}` : ""}</div>
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
                            <tr><th>Year</th><th>Status</th><th>Score</th><th>Rank</th><th>Sheet</th></tr>
                          </thead>
                          <tbody>
                      {(history.history || []).map((h, i) => (
                              <tr key={i}>
                                <td style={{ fontWeight: 600 }}>{h.period_name || h.period_id}</td>
                                <td><Badge status={h.status} /></td>
                                <td><span style={{ fontSize: 18, fontWeight: 700, color: "var(--primary)" }}>{h.final_score ?? "—"}</span></td>
                                <td><strong>{h.rank || "—"}</strong></td>
                                <td><a href={h.spreadsheet_url} target="_blank" rel="noreferrer" className="link">Open Sheet ↗</a></td>
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
