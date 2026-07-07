import { useEffect, useRef, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Brain,
  Building2,
  CheckCircle2,
  Database,
  FileSearch,
  LineChart,
  Play,
  RefreshCcw,
  Search,
  ShieldCheck,
  Siren,
  Sparkles,
  WalletCards,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { get, patch, post, WS_URL } from "./lib/api";
import type {
  Alert,
  AlertInvestigation,
  AnalyticsBucket,
  DashboardOverview,
  SemanticSearchResponse,
  TopVendorRisk,
  Transaction,
  TrendPoint,
  Vendor,
} from "./types";

type PageId =
  | "command"
  | "monitor"
  | "search"
  | "alerts"
  | "vendors"
  | "analytics";

const pageLabels: Record<PageId, string> = {
  command: "Command Center",
  monitor: "Live Monitor",
  search: "Semantic Search",
  alerts: "Alert Investigation",
  vendors: "Vendor Risk",
  analytics: "Analytics",
};

const navItems: Array<{ id: PageId; icon: React.ReactNode; label: string }> = [
  { id: "command", icon: <ShieldCheck />, label: "Command Center" },
  { id: "monitor", icon: <Activity />, label: "Live Monitor" },
  { id: "search", icon: <Brain />, label: "Semantic Search" },
  { id: "alerts", icon: <Siren />, label: "Investigations" },
  { id: "vendors", icon: <Building2 />, label: "Vendors" },
  { id: "analytics", icon: <BarChart3 />, label: "Analytics" },
];

export default function App() {
  const [activePage, setActivePage] = useState<PageId>("command");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <ShieldCheck size={26} />
          </div>
          <div>
            <div className="brand-title">FinGuard AI</div>
            <div className="brand-subtitle">Compliance Intelligence</div>
          </div>
        </div>

        <nav className="nav-list">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activePage === item.id ? "active" : ""}`}
              onClick={() => setActivePage(item.id)}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>Backend connected</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Real-Time Compliance Intelligence</p>
            <h1>{pageLabels[activePage]}</h1>
          </div>
          <div className="topbar-card">
            <Sparkles size={18} />
            <span>OpenAI + ChromaDB Enabled</span>
          </div>
        </header>

        {activePage === "command" && <CommandCenter />}
        {activePage === "monitor" && <LiveMonitor />}
        {activePage === "search" && <SemanticSearchPage />}
        {activePage === "alerts" && <AlertInvestigationPage />}
        {activePage === "vendors" && <VendorRiskPage />}
        {activePage === "analytics" && <AnalyticsPage />}
      </main>
    </div>
  );
}

function CommandCenter() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await get<DashboardOverview>("/analytics/overview");
      setOverview(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 8000);
    return () => window.clearInterval(timer);
  }, []);

  if (loading && !overview) return <LoadingState label="Loading command center..." />;
  if (!overview) return <EmptyState label="No dashboard data available." />;

  const summary = overview.summary;

  return (
    <div className="page-grid">
      <section className="metric-grid">
        <MetricCard
          label="Transactions"
          value={summary.total_transactions}
          icon={<Activity />}
          accent="cyan"
        />
        <MetricCard
          label="Open Alerts"
          value={summary.open_alerts}
          icon={<AlertTriangle />}
          accent="amber"
        />
        <MetricCard
          label="Critical Alerts"
          value={summary.critical_alerts}
          icon={<Siren />}
          accent="red"
        />
        <MetricCard
          label="Avg Risk Score"
          value={summary.average_risk_score}
          icon={<LineChart />}
          accent="violet"
        />
      </section>

      <section className="content-grid two">
        <Panel title="Risk by Department" icon={<BarChart3 />}>
          <ChartBox>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={overview.risk_by_department}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="average_risk_score" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartBox>
        </Panel>

        <Panel title="Alert Severity" icon={<Siren />}>
          <ChartBox>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={overview.alert_severity_distribution}
                  dataKey="count"
                  nameKey="name"
                  innerRadius={60}
                  outerRadius={105}
                  paddingAngle={5}
                >
                  {overview.alert_severity_distribution.map((_, index) => (
                    <Cell key={index} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </ChartBox>
        </Panel>
      </section>

      <section className="content-grid two">
        <Panel title="Recent Transactions" icon={<Database />}>
          <TransactionList transactions={overview.recent_transactions} />
        </Panel>

        <Panel title="Recent Alerts" icon={<AlertTriangle />}>
          <AlertList alerts={overview.recent_alerts} />
        </Panel>
      </section>
    </div>
  );
}

function LiveMonitor() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [busy, setBusy] = useState(false);
  const [connected, setConnected] = useState(false);
  const [lastEventAt, setLastEventAt] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const latestTransactionId = useRef<string | null>(null);

  async function load() {
    const [tx, al] = await Promise.all([
      get<Transaction[]>("/transactions/recent/feed?limit=20"),
      get<Alert[]>("/alerts/recent/feed?limit=10"),
    ]);

    setTransactions(tx);
    setAlerts(al);
  }

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: number | undefined;
    let manuallyClosed = false;

    function connect() {
      socket = new WebSocket(`${WS_URL}/ws/live-feed`);

      socket.onopen = () => {
        setConnected(true);
      };

      socket.onclose = () => {
        setConnected(false);

        if (!manuallyClosed) {
          reconnectTimer = window.setTimeout(connect, 3000);
        }
      };

      socket.onerror = () => {
        setConnected(false);
      };

      socket.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        const nextTransactions = payload.transactions || [];
        const nextAlerts = payload.alerts || [];

        setTransactions(nextTransactions);
        setAlerts(nextAlerts);
        setLastEventAt(payload.timestamp || new Date().toISOString());

        const newest = nextTransactions[0];

        if (newest && latestTransactionId.current && newest.transaction_id !== latestTransactionId.current) {
          setToast(`New ${newest.risk_level} transaction detected: ${newest.transaction_id}`);
          window.setTimeout(() => setToast(null), 3500);
        }

        if (newest) {
          latestTransactionId.current = newest.transaction_id;
        }
      };
    }

    connect();
    load();

    return () => {
      manuallyClosed = true;

      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer);
      }

      if (socket) {
        socket.close();
      }
    };
  }, []);

  async function seedData() {
    setBusy(true);

    try {
      await post("/seed/sample-data?force=true");
      await post("/index/transactions?limit=500");
      await load();
      setToast("Sample data reset and indexed successfully.");
      window.setTimeout(() => setToast(null), 3000);
    } finally {
      setBusy(false);
    }
  }

  async function simulateBatch() {
    setBusy(true);

    try {
      await post("/simulate/batch?count=15");
      await load();
      setToast("Generated 15 simulated compliance events.");
      window.setTimeout(() => setToast(null), 3000);
    } finally {
      setBusy(false);
    }
  }

  async function startLive() {
    setBusy(true);

    try {
      await post("/simulate/live?count=40&delay_seconds=1");
      window.setTimeout(load, 1500);
      setToast("Live simulation started. New events will appear automatically.");
      window.setTimeout(() => setToast(null), 3500);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page-grid">
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}

      <section className="monitor-status-card">
        <div>
          <p className="eyebrow small">Streaming Status</p>
          <h2>Real-Time Compliance Event Feed</h2>
          <span>
            {lastEventAt
              ? `Last update: ${formatDate(lastEventAt)}`
              : "Waiting for first event update..."}
          </span>
        </div>

        <ConnectionBadge connected={connected} />
      </section>

      <section className="action-row">
        <button className="primary-btn" onClick={seedData} disabled={busy}>
          <Database size={18} />
          Reset Seed Data
        </button>
        <button className="secondary-btn" onClick={simulateBatch} disabled={busy}>
          <Play size={18} />
          Generate 15 Events
        </button>
        <button className="secondary-btn" onClick={startLive} disabled={busy}>
          <Activity size={18} />
          Start Live Stream
        </button>
        <button className="ghost-btn" onClick={load}>
          <RefreshCcw size={18} />
          Refresh
        </button>
      </section>

      <section className="content-grid two wide-left">
        <Panel title="Live Transaction Feed" icon={<Activity />}>
          <div className="live-feed">
            {transactions.map((tx) => (
              <button
                key={tx.transaction_id}
                className="feed-card clickable-feed-card"
                onClick={() => setSelectedTransaction(tx)}
              >
                <div className="feed-main">
                  <div className={`feed-pulse ${tx.risk_level.toLowerCase()}`} />
                  <div>
                    <div className="feed-title">{tx.transaction_id}</div>
                    <div className="feed-subtitle">
                      {tx.vendor_name} · {tx.department} · {tx.payment_method}
                    </div>
                  </div>
                </div>
                <div className="feed-right">
                  <div className="amount">{formatCurrency(tx.amount)}</div>
                  <RiskBadge level={tx.risk_level} score={tx.risk_score} />
                </div>
              </button>
            ))}
          </div>
        </Panel>

        <Panel title="Alert Stream" icon={<AlertTriangle />}>
          <AlertList alerts={alerts} />
        </Panel>
      </section>

      {selectedTransaction && (
        <TransactionDrawer
          transaction={selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
        />
      )}
    </div>
  );
}

function SemanticSearchPage() {
  const [query, setQuery] = useState("suspicious wire transfers with missing approvals");
  const [riskLevel, setRiskLevel] = useState("");
  const [department, setDepartment] = useState("");
  const [minAmount, setMinAmount] = useState("");
  const [results, setResults] = useState<SemanticSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function indexTransactions() {
    setLoading(true);
    try {
      await post("/index/transactions?limit=500");
    } finally {
      setLoading(false);
    }
  }

  async function runSearch(event?: React.FormEvent) {
    event?.preventDefault();
    setLoading(true);

    try {
      const data = await post<SemanticSearchResponse>("/search/semantic", {
        query,
        top_k: 10,
        risk_level: riskLevel || null,
        department: department || null,
        min_amount: minAmount ? Number(minAmount) : null,
      });
      setResults(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-grid">
      <Panel title="AI Semantic Investigation" icon={<Brain />}>
        <form className="search-form" onSubmit={runSearch}>
          <div className="search-input-wrap">
            <Search size={20} />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search compliance evidence using natural language..."
            />
          </div>

          <div className="filter-grid">
            <select value={riskLevel} onChange={(event) => setRiskLevel(event.target.value)}>
              <option value="">All Risk Levels</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>

            <select value={department} onChange={(event) => setDepartment(event.target.value)}>
              <option value="">All Departments</option>
              <option value="Finance">Finance</option>
              <option value="Procurement">Procurement</option>
              <option value="Operations">Operations</option>
              <option value="Legal">Legal</option>
              <option value="IT">IT</option>
              <option value="Administration">Administration</option>
            </select>

            <input
              value={minAmount}
              onChange={(event) => setMinAmount(event.target.value)}
              placeholder="Min amount"
              type="number"
            />

            <button className="primary-btn" type="submit" disabled={loading}>
              <FileSearch size={18} />
              Search
            </button>

            <button className="secondary-btn" type="button" onClick={indexTransactions} disabled={loading}>
              <Database size={18} />
              Reindex
            </button>
          </div>
        </form>
      </Panel>

      {loading && <LoadingState label="Running semantic search..." />}

      {results && (
        <section className="search-results">
          <div className="section-heading">
            <h2>{results.result_count} results found</h2>
            <p>Query: {results.query}</p>
          </div>

          {results.results.map((item) => (
            <div key={item.transaction.transaction_id} className="result-card">
              <div className="result-header">
                <div>
                  <h3>{item.transaction.vendor_name}</h3>
                  <p>{item.transaction.transaction_id} · {item.transaction.category}</p>
                </div>
                <div className="result-score">
                  <span>{Math.round(item.similarity_score * 100)}%</span>
                  Match
                </div>
              </div>

              <p className="matched-reason">{item.matched_reason}</p>

              <div className="result-meta">
                <RiskBadge level={item.transaction.risk_level} score={item.transaction.risk_score} />
                <span>{formatCurrency(item.transaction.amount)}</span>
                <span>{item.transaction.department}</span>
                <span>{item.transaction.payment_method}</span>
              </div>

              <div className="evidence-box">{item.evidence_text}</div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

function AlertInvestigationPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [investigation, setInvestigation] = useState<AlertInvestigation | null>(null);
  const [note, setNote] = useState("");

  async function loadAlerts() {
    const data = await get<Alert[]>("/alerts?limit=50");
    setAlerts(data);

    if (!selectedAlertId && data.length > 0) {
      setSelectedAlertId(data[0].alert_id);
    }
  }

  async function loadInvestigation(alertId: string) {
    const data = await get<AlertInvestigation>(`/alerts/${alertId}/investigation`);
    setInvestigation(data);
  }

  useEffect(() => {
    loadAlerts();
  }, []);

  useEffect(() => {
    if (selectedAlertId) {
      loadInvestigation(selectedAlertId);
    }
  }, [selectedAlertId]);

  async function updateStatus(status: string) {
    if (!selectedAlertId) return;

    await patch(`/alerts/${selectedAlertId}/status`, {
      status,
      assigned_to: "Anvesh",
    });

    await loadAlerts();
    await loadInvestigation(selectedAlertId);
  }

  async function addNote() {
    if (!selectedAlertId || !note.trim()) return;

    await post(`/alerts/${selectedAlertId}/notes`, {
      author: "Anvesh",
      note,
    });

    setNote("");
    await loadInvestigation(selectedAlertId);
  }

  return (
    <div className="content-grid two alert-layout">
      <Panel title="Alert Queue" icon={<Siren />}>
        <div className="alert-selector">
          {alerts.map((alert) => (
            <button
              key={alert.alert_id}
              className={`alert-select-card ${
                selectedAlertId === alert.alert_id ? "selected" : ""
              }`}
              onClick={() => setSelectedAlertId(alert.alert_id)}
            >
              <div>
                <strong>{alert.alert_id}</strong>
                <span>{alert.transaction_id}</span>
              </div>
              <RiskBadge level={alert.risk_level} score={alert.risk_score} />
            </button>
          ))}
        </div>
      </Panel>

      <Panel title="Investigation Workspace" icon={<FileSearch />}>
        {!investigation ? (
          <EmptyState label="Select an alert to investigate." />
        ) : (
          <div className="investigation">
            <div className="investigation-header">
              <div>
                <h2>{investigation.alert.alert_id}</h2>
                <p>{investigation.transaction.vendor_name}</p>
              </div>
              <RiskBadge
                level={investigation.alert.risk_level}
                score={investigation.alert.risk_score}
              />
            </div>

            <div className="action-row compact">
              <button className="secondary-btn" onClick={() => updateStatus("In Review")}>
                In Review
              </button>
              <button className="secondary-btn" onClick={() => updateStatus("Escalated")}>
                Escalate
              </button>
              <button className="secondary-btn" onClick={() => updateStatus("Resolved")}>
                Resolve
              </button>
            </div>

            <div className="ai-box">
              <div className="ai-box-title">
                <Brain size={18} />
                AI Explanation · {investigation.ai_mode}
              </div>
              <pre>{investigation.ai_explanation}</pre>
            </div>

            <div className="detail-grid">
              <Info label="Amount" value={formatCurrency(investigation.transaction.amount)} />
              <Info label="Department" value={investigation.transaction.department} />
              <Info label="Payment Method" value={investigation.transaction.payment_method} />
              <Info label="Approval" value={investigation.transaction.approval_status} />
            </div>

            <div className="note-box">
              <textarea
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="Add investigation note..."
              />
              <button className="primary-btn" onClick={addNote}>
                Add Note
              </button>
            </div>

            <h3 className="mini-heading">Timeline</h3>
            <div className="timeline">
              {investigation.timeline.map((item, index) => (
                <div key={`${item.type}-${index}`} className="timeline-item">
                  <div className="timeline-dot" />
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.description}</p>
                    <span>{formatDate(item.timestamp)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Panel>
    </div>
  );
}

function VendorRiskPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [topVendors, setTopVendors] = useState<TopVendorRisk[]>([]);

  useEffect(() => {
    Promise.all([
      get<Vendor[]>("/vendors?limit=100"),
      get<TopVendorRisk[]>("/analytics/top-risky-vendors?limit=10"),
    ]).then(([vendorData, topData]) => {
      setVendors(vendorData);
      setTopVendors(topData);
    });
  }, []);

  return (
    <div className="page-grid">
      <Panel title="Top Risky Vendors" icon={<Building2 />}>
        <div className="vendor-ranking">
          {topVendors.map((vendor, index) => (
            <div key={vendor.vendor_name} className="vendor-rank-card">
              <div className="rank-number">{index + 1}</div>
              <div>
                <h3>{vendor.vendor_name}</h3>
                <p>
                  {vendor.transaction_count} transactions · {vendor.alert_count} alerts ·{" "}
                  {formatCurrency(vendor.total_amount)}
                </p>
              </div>
              <RiskBadge level={riskFromScore(vendor.average_risk_score)} score={vendor.average_risk_score} />
            </div>
          ))}
        </div>
      </Panel>

      <Panel title="Vendor Directory" icon={<Database />}>
        <div className="table-card">
          <table>
            <thead>
              <tr>
                <th>Vendor</th>
                <th>Industry</th>
                <th>Country</th>
                <th>Risk</th>
                <th>Payment Volume</th>
              </tr>
            </thead>
            <tbody>
              {vendors.map((vendor) => (
                <tr key={vendor.vendor_id}>
                  <td>{vendor.name}</td>
                  <td>{vendor.industry || "N/A"}</td>
                  <td>{vendor.country}</td>
                  <td>
                    <RiskBadge level={vendor.risk_rating} score={vendor.average_risk_score} />
                  </td>
                  <td>{formatCurrency(vendor.total_payment_volume)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}

function AnalyticsPage() {
  const [riskByDepartment, setRiskByDepartment] = useState<AnalyticsBucket[]>([]);
  const [riskByPayment, setRiskByPayment] = useState<AnalyticsBucket[]>([]);
  const [riskByCountry, setRiskByCountry] = useState<AnalyticsBucket[]>([]);
  const [volumeTrend, setVolumeTrend] = useState<TrendPoint[]>([]);
  const [alertTrend, setAlertTrend] = useState<TrendPoint[]>([]);

  useEffect(() => {
    Promise.all([
      get<AnalyticsBucket[]>("/analytics/risk-by-department"),
      get<AnalyticsBucket[]>("/analytics/risk-by-payment-method"),
      get<AnalyticsBucket[]>("/analytics/risk-by-country"),
      get<TrendPoint[]>("/analytics/transaction-volume-trend?days=30"),
      get<TrendPoint[]>("/analytics/alert-trend?days=30"),
    ]).then(([department, payment, country, volume, alerts]) => {
      setRiskByDepartment(department);
      setRiskByPayment(payment);
      setRiskByCountry(country);
      setVolumeTrend(volume);
      setAlertTrend(alerts);
    });
  }, []);

  return (
    <div className="page-grid">
      <section className="content-grid two">
        <Panel title="Transaction Volume Trend" icon={<LineChart />}>
          <ChartBox>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={volumeTrend}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="count" strokeWidth={2} fillOpacity={0.25} />
              </AreaChart>
            </ResponsiveContainer>
          </ChartBox>
        </Panel>

        <Panel title="Alert Trend" icon={<AlertTriangle />}>
          <ChartBox>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={alertTrend}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="count" strokeWidth={2} fillOpacity={0.25} />
              </AreaChart>
            </ResponsiveContainer>
          </ChartBox>
        </Panel>
      </section>

      <section className="content-grid three">
        <BucketPanel title="Risk by Department" data={riskByDepartment} />
        <BucketPanel title="Risk by Payment" data={riskByPayment} />
        <BucketPanel title="Risk by Country" data={riskByCountry} />
      </section>
    </div>
  );
}

function ConnectionBadge({ connected }: { connected: boolean }) {
  return (
    <div className={`connection-badge ${connected ? "connected" : "disconnected"}`}>
      {connected ? <Wifi size={18} /> : <WifiOff size={18} />}
      <span>{connected ? "WebSocket Connected" : "Reconnecting..."}</span>
    </div>
  );
}

function Toast({
  message,
  onClose,
}: {
  message: string;
  onClose: () => void;
}) {
  return (
    <div className="toast">
      <div>
        <strong>Live Update</strong>
        <p>{message}</p>
      </div>
      <button onClick={onClose}>
        <X size={16} />
      </button>
    </div>
  );
}

function TransactionDrawer({
  transaction,
  onClose,
}: {
  transaction: Transaction;
  onClose: () => void;
}) {
  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside className="transaction-drawer" onClick={(event) => event.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <p className="eyebrow small">Transaction Detail</p>
            <h2>{transaction.transaction_id}</h2>
            <span>{transaction.vendor_name}</span>
          </div>

          <button className="icon-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="drawer-risk">
          <RiskBadge level={transaction.risk_level} score={transaction.risk_score} />
          <span>{transaction.review_status}</span>
        </div>

        <div className="detail-grid drawer-grid">
          <Info label="Amount" value={formatCurrency(transaction.amount)} />
          <Info label="Department" value={transaction.department} />
          <Info label="Payment Method" value={transaction.payment_method} />
          <Info label="Country" value={transaction.country} />
          <Info label="Category" value={transaction.category} />
          <Info label="Invoice ID" value={transaction.invoice_id || "N/A"} />
          <Info label="Approved By" value={transaction.approved_by || "Missing"} />
          <Info label="Approval Status" value={transaction.approval_status} />
        </div>

        <div className="drawer-section">
          <h3>Description</h3>
          <p>{transaction.description}</p>
        </div>

        <div className="drawer-section">
          <h3>Risk Flags</h3>
          {transaction.risk_flags.length === 0 ? (
            <p>No major risk flags detected.</p>
          ) : (
            <div className="flag-list">
              {transaction.risk_flags.map((flag) => (
                <span key={flag}>{flag}</span>
              ))}
            </div>
          )}
        </div>

        <div className="drawer-section">
          <h3>Timestamp</h3>
          <p>{formatDate(transaction.timestamp)}</p>
        </div>
      </aside>
    </div>
  );
}


function MetricCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  accent: string;
}) {
  return (
    <div className={`metric-card ${accent}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <p>{label}</p>
        <h2>{value}</h2>
      </div>
    </div>
  );
}

function Panel({
  title,
  icon,
  children,
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div className="panel-title">
          {icon}
          <h2>{title}</h2>
        </div>
      </div>
      {children}
    </section>
  );
}

function TransactionList({ transactions }: { transactions: Transaction[] }) {
  return (
    <div className="stack-list">
      {transactions.map((tx) => (
        <div key={tx.transaction_id} className="list-row">
          <div>
            <strong>{tx.vendor_name}</strong>
            <p>{tx.transaction_id} · {tx.department} · {formatDate(tx.timestamp)}</p>
          </div>
          <div className="row-right">
            <span>{formatCurrency(tx.amount)}</span>
            <RiskBadge level={tx.risk_level} score={tx.risk_score} />
          </div>
        </div>
      ))}
    </div>
  );
}

function AlertList({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="stack-list">
      {alerts.map((alert) => (
        <div key={alert.alert_id} className="list-row">
          <div>
            <strong>{alert.alert_id}</strong>
            <p>{alert.transaction_id} · {alert.status}</p>
          </div>
          <RiskBadge level={alert.risk_level} score={alert.risk_score} />
        </div>
      ))}
    </div>
  );
}

function BucketPanel({ title, data }: { title: string; data: AnalyticsBucket[] }) {
  return (
    <Panel title={title} icon={<BarChart3 />}>
      <div className="bucket-list">
        {data.map((item) => (
          <div key={item.name} className="bucket-row">
            <div>
              <strong>{item.name}</strong>
              <p>{item.count} records</p>
            </div>
            <span>{item.average_risk_score ?? 0}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function RiskBadge({ level, score }: { level: string; score?: number }) {
  const normalized = level.toLowerCase();
  return (
    <span className={`risk-badge ${normalized}`}>
      {level}
      {score !== undefined ? ` · ${Math.round(score)}` : ""}
    </span>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="info-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ChartBox({ children }: { children: React.ReactNode }) {
  return <div className="chart-box">{children}</div>;
}

function LoadingState({ label }: { label: string }) {
  return (
    <div className="empty-state">
      <RefreshCcw className="spin" />
      <span>{label}</span>
    </div>
  );
}

function EmptyState({ label }: { label: string }) {
  return (
    <div className="empty-state">
      <CheckCircle2 />
      <span>{label}</span>
    </div>
  );
}

function riskFromScore(score: number): string {
  if (score >= 81) return "Critical";
  if (score >= 61) return "High";
  if (score >= 31) return "Medium";
  return "Low";
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

const tooltipStyle = {
  background: "#020617",
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: "14px",
  color: "#e2e8f0",
};
