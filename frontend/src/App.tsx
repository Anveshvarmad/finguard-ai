import { useEffect, useState } from "react";
import { Activity, AlertTriangle, Brain, Database, ShieldCheck, Zap } from "lucide-react";

const API_URL = "http://localhost:8000";

type HealthStatus = {
  status?: string;
  service?: string;
  environment?: string;
};

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth(null));
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="relative overflow-hidden border-b border-white/10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.25),transparent_35%),radial-gradient(circle_at_top_left,rgba(99,102,241,0.25),transparent_30%)]" />

        <div className="relative mx-auto max-w-7xl px-6 py-12">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-cyan-400/10 p-3 ring-1 ring-cyan-300/30">
              <ShieldCheck className="h-8 w-8 text-cyan-300" />
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-cyan-200">
                Real-Time Compliance Intelligence
              </p>
              <h1 className="mt-2 text-5xl font-bold tracking-tight">
                FinGuard AI
              </h1>
            </div>
          </div>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
            AI-powered compliance monitoring platform for transaction risk scoring,
            semantic investigation, alert triage, and explainable financial review workflows.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard title="Transactions" value="0" icon={<Activity />} />
            <MetricCard title="Open Alerts" value="0" icon={<AlertTriangle />} />
            <MetricCard title="AI Search" value="Ready" icon={<Brain />} />
            <MetricCard title="Backend" value={health?.status ?? "Checking"} icon={<Zap />} />
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-3">
        <Panel
          title="Service Health"
          icon={<Database className="h-5 w-5 text-cyan-300" />}
          body={
            <pre className="overflow-auto rounded-xl bg-black/30 p-4 text-sm text-slate-300">
              {JSON.stringify(health, null, 2)}
            </pre>
          }
        />

        <Panel
          title="Phase 1 Status"
          icon={<ShieldCheck className="h-5 w-5 text-emerald-300" />}
          body={
            <div className="space-y-3 text-sm text-slate-300">
              <Status label="FastAPI backend" />
              <Status label="React frontend" />
              <Status label="PostgreSQL container" />
              <Status label="Redis container" />
              <Status label="OpenAI integration endpoint" />
            </div>
          }
        />

        <Panel
          title="Next Phase"
          icon={<Brain className="h-5 w-5 text-violet-300" />}
          body={
            <p className="text-sm leading-6 text-slate-300">
              Next we will create transaction, vendor, alert, and risk-rule models,
              then generate fake real-time financial events.
            </p>
          }
        />
      </section>
    </main>
  );
}

function MetricCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 shadow-2xl backdrop-blur">
      <div className="flex items-center justify-between text-slate-400">
        <span className="text-sm">{title}</span>
        <div className="text-cyan-300">{icon}</div>
      </div>
      <div className="mt-4 text-3xl font-semibold">{value}</div>
    </div>
  );
}

function Panel({
  title,
  icon,
  body,
}: {
  title: string;
  icon: React.ReactNode;
  body: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 shadow-xl">
      <div className="mb-4 flex items-center gap-2">
        {icon}
        <h2 className="font-semibold">{title}</h2>
      </div>
      {body}
    </div>
  );
}

function Status({ label }: { label: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-white/[0.03] px-4 py-3">
      <span>{label}</span>
      <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">
        Ready
      </span>
    </div>
  );
}
