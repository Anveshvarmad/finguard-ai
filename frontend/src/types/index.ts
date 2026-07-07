export type RiskLevel = "Low" | "Medium" | "High" | "Critical";

export type Transaction = {
  id: number;
  transaction_id: string;
  vendor_name: string;
  department: string;
  amount: number;
  currency: string;
  payment_method: string;
  country: string;
  category: string;
  description: string;
  invoice_id: string | null;
  approved_by: string | null;
  approval_status: string;
  risk_score: number;
  risk_level: RiskLevel | string;
  risk_flags: string[];
  review_status: string;
  timestamp: string;
  created_at: string;
};

export type Alert = {
  id: number;
  alert_id: string;
  transaction_id: string;
  risk_level: RiskLevel | string;
  risk_score: number;
  risk_flags: string[];
  alert_reason: string;
  status: string;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
};

export type Vendor = {
  id: number;
  vendor_id: string;
  name: string;
  industry: string | null;
  country: string;
  risk_rating: string;
  status: string;
  total_payment_volume: number;
  average_risk_score: number;
  created_at: string;
};

export type DashboardSummary = {
  total_transactions: number;
  total_vendors: number;
  total_alerts: number;
  open_alerts: number;
  critical_alerts: number;
  high_risk_transactions: number;
  total_payment_volume: number;
  average_transaction_amount: number;
  average_risk_score: number;
};

export type AnalyticsBucket = {
  name: string;
  count: number;
  average_risk_score?: number | null;
  total_amount?: number | null;
};

export type TrendPoint = {
  date: string;
  count: number;
  total_amount?: number | null;
  average_risk_score?: number | null;
};

export type TopVendorRisk = {
  vendor_name: string;
  transaction_count: number;
  alert_count: number;
  total_amount: number;
  average_risk_score: number;
  max_risk_score: number;
};

export type DashboardOverview = {
  summary: DashboardSummary;
  risk_by_department: AnalyticsBucket[];
  alert_severity_distribution: AnalyticsBucket[];
  alert_status_distribution: AnalyticsBucket[];
  top_risky_vendors: TopVendorRisk[];
  recent_transactions: Transaction[];
  recent_alerts: Alert[];
};

export type SemanticSearchResult = {
  transaction: Transaction;
  similarity_score: number;
  distance: number;
  evidence_text: string;
  metadata: Record<string, unknown>;
  matched_reason: string;
};

export type SemanticSearchResponse = {
  query: string;
  top_k: number;
  result_count: number;
  results: SemanticSearchResult[];
};

export type TimelineItem = {
  type: string;
  timestamp: string;
  title: string;
  description: string;
};

export type InvestigationNote = {
  id: number;
  alert_id: string;
  transaction_id: string;
  author: string;
  note: string;
  created_at: string;
};

export type AlertInvestigation = {
  alert: Alert;
  transaction: Transaction;
  notes: InvestigationNote[];
  timeline: TimelineItem[];
  related_transactions: Transaction[];
  ai_mode: string;
  ai_explanation: string;
  evidence: string;
};
