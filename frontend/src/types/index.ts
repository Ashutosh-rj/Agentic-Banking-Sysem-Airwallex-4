export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'treasury_manager' | 'payment_ops' | 'auditor' | string;
  org_id: string;
  is_active: boolean;
  avatar_initials?: string;
  last_login?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Account {
  id: string;
  org_id: string;
  name: string;
  account_number?: string;
  currency: string;
  available_balance: string;
  reserved_balance: string;
  total_balance: string;
  provider?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Beneficiary {
  id: string;
  org_id: string;
  name: string;
  account_number?: string;
  bank_code?: string;
  bank_name?: string;
  currency: string;
  email?: string;
  criticality: 'low' | 'medium' | 'high' | 'critical';
  is_active: boolean;
  created_at: string;
}

export interface Payment {
  id: string;
  org_id: string;
  payment_number: string;
  status: 'CREATED' | 'VALIDATING' | 'SUBMITTED' | 'PENDING' | 'SUCCEEDED' | 'FAILED' | 'UNKNOWN' | 'CANCELLED' | 'REQUIRES_REVIEW';
  amount: string;
  currency: string;
  beneficiary_id?: string;
  account_id?: string;
  beneficiary_name?: string;
  account_name?: string;
  reference?: string;
  description?: string;
  idempotency_key?: string;
  provider_ref?: string;
  error_message?: string;
  retry_count: number;
  parent_payment_id?: string;
  is_demo: boolean;
  submitted_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentTimelineEvent {
  timestamp: string;
  event: string;
  description: string;
  status?: string;
  actor?: string;
}

export interface Incident {
  id: string;
  org_id: string;
  incident_number: string;
  payment_id?: string;
  title: string;
  description?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'pending_action' | 'resolved' | 'closed' | 'escalated';
  priority_score: number;
  sla_deadline?: string;
  assigned_to?: string;
  assigned_user_name?: string;
  root_cause?: string;
  ai_report?: string;
  financial_impact?: string;
  financial_currency?: string;
  resolution_notes?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  payment_number?: string;
  payment_amount?: string;
  payment_currency?: string;
}

export interface IncidentEvidence {
  id: string;
  incident_id: string;
  evidence_type: string;
  content: string;
  created_by?: string;
  created_at: string;
}

export interface AgentExecution {
  id: string;
  incident_id: string;
  agent_name: string;
  step_index: number;
  status: string;
  input_data?: string;
  output_data?: string;
  error?: string;
  duration_ms?: number;
  started_at?: string;
  completed_at?: string;
}

export interface ReconciliationRun {
  id: string;
  org_id: string;
  run_number: string;
  status: string;
  matched_count: number;
  unmatched_count: number;
  exception_count: number;
  period_start?: string;
  period_end?: string;
  notes?: string;
  created_by?: string;
  created_at: string;
  completed_at?: string;
}

export interface ReconciliationRecord {
  id: string;
  run_id: string;
  payment_id?: string;
  payment_number?: string;
  match_status: 'matched' | 'probable_match' | 'unmatched' | 'conflict' | 'duplicate_candidate' | 'reviewed';
  match_confidence?: number;
  provider_reference?: string;
  provider_amount?: string;
  provider_currency?: string;
  internal_amount?: string;
  discrepancy_notes?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  resolution?: string;
  created_at: string;
}

export interface TreasuryPosition {
  currency: string;
  available_balance?: string;
  reserved_balance?: string;
  total_balance?: string;
  available?: string;
  reserved?: string;
  total?: string;
  pending_obligations?: string;
  net_position?: string;
  accounts?: Account[];
}

export interface PaymentObligation {
  id: string;
  org_id: string;
  beneficiary_id?: string;
  beneficiary_name?: string;
  amount: string;
  currency: string;
  due_date: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
  status: 'pending' | 'scheduled' | 'paid' | 'overdue' | 'cancelled';
  description?: string;
  payment_id?: string;
  created_at: string;
}

export interface CashFlowForecastEntry {
  date: string;
  currency: string;
  inflow?: string;
  outflow?: string;
  net?: string;
  cumulative?: string;
  projected_balance?: string;
  obligations_due?: string;
}

export interface RiskAlert {
  id: string;
  org_id: string;
  payment_id?: string;
  payment_number?: string;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  risk_score: number;
  risk_factors?: string;
  status: 'open' | 'reviewing' | 'dismissed' | 'escalated' | 'resolved' | string;
  reviewed_by?: string;
  reviewed_at?: string;
  review_notes?: string;
  created_at: string;
}

export interface RiskOverview {
  total_alerts: number;
  open_alerts: number;
  critical_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  duplicate_payment_exposure: string;
  uncertain_payment_count: number;
  average_risk_score: number;
  avg_risk_score?: number;
  alerts_by_type?: Record<string, number>;
}

export interface AnalyticsOverview {
  period_days: number;
  total_payments: number;
  successful_payments: number;
  failed_payments: number;
  pending_payments: number;
  success_rate: number;
  failure_rate: number;
  total_volume: string;
  total_incidents: number;
  resolved_incidents: number;
  open_incidents: number;
  avg_processing_time_seconds: number;
  avg_resolution_time_hours: number;
  sla_compliance_rate: number;
  reconciliation_exception_rate: number;
  top_currencies: Array<{ currency: string; volume: string }>;
  payments_by_status: Record<string, number>;
}

export interface IncidentPerformance {
  total_incidents: number;
  resolved_incidents: number;
  avg_resolution_minutes: number;
  avg_resolution_hours: number;
  sla_breached: number;
  period: string;
  created: number;
  resolved: number;
  by_severity: Record<string, number>;
  by_root_cause: Record<string, number>;
}

export interface BusinessImpact {
  total_financial_impact: string;
  incidents_with_impact: number;
  avg_impact_per_incident: string;
  payment_failure_cost: string;
  duplicate_payments_confirmed: number;
  duplicate_payment_amount: string;
  uncertain_payments: number;
  uncertain_payment_exposure: string;
  estimated_time_saved_hours: number;
  estimated_cost_savings: string;
  reconciliation_exceptions_resolved: number;
  calculation_methodology: string;
}

export interface AuditLog {
  id: string;
  org_id: string;
  actor_id?: string;
  actor_email?: string;
  actor_role?: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  before_state?: string;
  after_state?: string;
  reason?: string;
  ip_address?: string;
  created_at: string;
}

export interface IntegrationStatus {
  id: string;
  name: string;
  category: string;
  status: 'connected' | 'sandbox' | 'degraded' | 'disconnected';
  provider: string;
  mode: 'sandbox' | 'simulation' | 'live';
  latency_ms?: number;
  last_checked: string;
  endpoint_url: string;
  features: string[];
  has_credentials: boolean;
  error_message?: string;
}

export interface DashboardSummary {
  total_available_usd_equivalent: string;
  accounts: Account[];
  total_payments: number;
  pending_payments: number;
  pending_amount: string;
  failed_today: number;
  succeeded_today: number;
  open_incidents: number;
  critical_incidents: number;
  sla_breach_count: number;
  unresolved_exceptions: number;
  unread_notifications: number;
}

export interface ActivityItem {
  id: string;
  type: 'payment' | 'incident' | 'reconciliation' | 'risk';
  title: string;
  description: string;
  timestamp: string;
  status?: string;
  amount?: string;
  currency?: string;
  severity?: string;
}

export interface TrendPoint {
  date: string;
  payments: number;
  incidents: number;
  amount?: string;
  volume?: string;
  alerts?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
