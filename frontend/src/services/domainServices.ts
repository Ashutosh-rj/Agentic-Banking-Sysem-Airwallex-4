import { api } from './api';
import {
  AuthResponse, User, DashboardSummary, ActivityItem, TrendPoint,
  Payment, PaymentTimelineEvent, Incident, IncidentEvidence,
  ReconciliationRun, ReconciliationRecord, TreasuryPosition, Account,
  PaymentObligation, CashFlowForecastEntry, RiskAlert, RiskOverview,
  AnalyticsOverview, IncidentPerformance, BusinessImpact, AuditLog,
  IntegrationStatus, PaginatedResponse, Beneficiary,
} from '../types';

// ==========================================
// Authentication
// ==========================================
export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>('/auth/login', { email, password });
    return res.data;
  },
  register: async (email: string, password: string, full_name: string, role = 'payment_ops'): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>('/auth/register', { email, password, full_name, role });
    return res.data;
  },
  logout: async (): Promise<{ message: string }> => {
    const res = await api.post('/auth/logout');
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },
};

// ==========================================
// Dashboard
// ==========================================
export const dashboardService = {
  getSummary: async (): Promise<DashboardSummary> => {
    const res = await api.get<DashboardSummary>('/dashboard/summary');
    return res.data;
  },
  getActivity: async (limit = 15): Promise<ActivityItem[]> => {
    const res = await api.get<ActivityItem[]>(`/dashboard/activity?limit=${limit}`);
    return res.data;
  },
  getTrends: async (days = 14): Promise<TrendPoint[]> => {
    const res = await api.get<TrendPoint[]>(`/dashboard/trends?days=${days}`);
    return res.data;
  },
};

// ==========================================
// Payments
// ==========================================
export const paymentService = {
  list: async (params?: { page?: number; page_size?: number; status?: string; currency?: string; search?: string }): Promise<PaginatedResponse<Payment>> => {
    const res = await api.get<PaginatedResponse<Payment>>('/payments', { params });
    return res.data;
  },
  get: async (id: string): Promise<Payment> => {
    const res = await api.get<Payment>(`/payments/${id}`);
    return res.data;
  },
  create: async (data: {
    amount: string;
    currency: string;
    beneficiary_id: string;
    account_id: string;
    reference?: string;
    description?: string;
    idempotency_key?: string;
  }): Promise<Payment> => {
    const res = await api.post<Payment>('/payments', data);
    return res.data;
  },
  retry: async (id: string): Promise<Payment> => {
    const res = await api.post<Payment>(`/payments/${id}/retry`);
    return res.data;
  },
  getTimeline: async (id: string): Promise<PaymentTimelineEvent[]> => {
    const res = await api.get<PaymentTimelineEvent[]>(`/payments/${id}/timeline`);
    return res.data;
  },
  getBeneficiaries: async (): Promise<Beneficiary[]> => {
    // Fetches beneficiaries through accounts or helper
    const res = await api.get<PaginatedResponse<Payment>>('/payments?page_size=100');
    // For dropdown choices in demo mode, return accounts or synthesized beneficiaries
    return [];
  },
};

// ==========================================
// Incidents
// ==========================================
export const incidentService = {
  list: async (params?: { page?: number; page_size?: number; status?: string; severity?: string }): Promise<PaginatedResponse<Incident>> => {
    const res = await api.get<PaginatedResponse<Incident>>('/incidents', { params });
    return res.data;
  },
  get: async (id: string): Promise<Incident> => {
    const res = await api.get<Incident>(`/incidents/${id}`);
    return res.data;
  },
  create: async (data: { payment_id?: string; title: string; description?: string; severity?: string }): Promise<Incident> => {
    const res = await api.post<Incident>('/incidents', data);
    return res.data;
  },
  update: async (id: string, data: Partial<Incident>): Promise<Incident> => {
    const res = await api.patch<Incident>(`/incidents/${id}`, data);
    return res.data;
  },
  investigate: async (id: string): Promise<{ message: string; report: any }> => {
    const res = await api.post(`/incidents/${id}/investigate`);
    return res.data;
  },
  resolve: async (id: string, notes?: string): Promise<Incident> => {
    const res = await api.post<Incident>(`/incidents/${id}/resolve`, { notes });
    return res.data;
  },
  assign: async (id: string, assignee_id: string): Promise<Incident> => {
    const res = await api.post<Incident>(`/incidents/${id}/assign`, { assignee_id });
    return res.data;
  },
  addEvidence: async (id: string, data: { evidence_type: string; content: string }): Promise<IncidentEvidence> => {
    const res = await api.post<IncidentEvidence>(`/incidents/${id}/evidence`, data);
    return res.data;
  },
  getActions: async (id: string): Promise<{ incident_id: string; actions: string[] }> => {
    const res = await api.get(`/incidents/${id}/actions`);
    return res.data;
  },
};

// ==========================================
// Reconciliation
// ==========================================
export const reconciliationService = {
  listRuns: async (page = 1, page_size = 20): Promise<PaginatedResponse<ReconciliationRun>> => {
    const res = await api.get<PaginatedResponse<ReconciliationRun>>('/reconciliation/runs', { params: { page, page_size } });
    return res.data;
  },
  getRun: async (runId: string): Promise<ReconciliationRun> => {
    const res = await api.get<ReconciliationRun>(`/reconciliation/runs/${runId}`);
    return res.data;
  },
  getRunRecords: async (runId: string, page = 1, page_size = 50): Promise<PaginatedResponse<ReconciliationRecord>> => {
    const res = await api.get<PaginatedResponse<ReconciliationRecord>>(`/reconciliation/runs/${runId}/records`, { params: { page, page_size } });
    return res.data;
  },
  triggerRun: async (): Promise<ReconciliationRun> => {
    const res = await api.post<ReconciliationRun>('/reconciliation/runs');
    return res.data;
  },
  reviewMatch: async (recordId: string, resolution: string, notes?: string): Promise<ReconciliationRecord> => {
    const res = await api.post<ReconciliationRecord>(`/reconciliation/records/${recordId}/review`, { resolution, notes });
    return res.data;
  },
};

// ==========================================
// Treasury
// ==========================================
export const treasuryService = {
  getAccounts: async (): Promise<Account[]> => {
    const res = await api.get<Account[]>('/treasury/accounts');
    return res.data;
  },
  getPositions: async (): Promise<TreasuryPosition[]> => {
    const res = await api.get<TreasuryPosition[]>('/treasury/positions');
    return res.data;
  },
  getObligations: async (page = 1, page_size = 20, status?: string): Promise<PaginatedResponse<PaymentObligation>> => {
    const res = await api.get<PaginatedResponse<PaymentObligation>>('/treasury/obligations', { params: { page, page_size, status } });
    return res.data;
  },
  getForecast: async (days = 14): Promise<CashFlowForecastEntry[]> => {
    const res = await api.get<CashFlowForecastEntry[]>(`/treasury/forecast?days=${days}`);
    return res.data;
  },
};

// ==========================================
// Risk & Controls
// ==========================================
export const riskService = {
  getOverview: async (): Promise<RiskOverview> => {
    const res = await api.get<RiskOverview>('/risk/overview');
    return res.data;
  },
  listAlerts: async (params?: { page?: number; page_size?: number; status?: string; severity?: string }): Promise<PaginatedResponse<RiskAlert>> => {
    const res = await api.get<PaginatedResponse<RiskAlert>>('/risk/alerts', { params });
    return res.data;
  },
  reviewAlert: async (alertId: string, action: string, notes?: string): Promise<RiskAlert> => {
    const res = await api.post<RiskAlert>(`/risk/alerts/${alertId}/review`, { action, notes });
    return res.data;
  },
  checkDuplicate: async (amount: string, beneficiary_id: string): Promise<{ is_duplicate_risk: boolean; match_count: number; matching_payment_ids: string[] }> => {
    const res = await api.post('/risk/check-duplicate', { amount, beneficiary_id });
    return res.data;
  },
};

// ==========================================
// Analytics
// ==========================================
export const analyticsService = {
  getOverview: async (period_days = 30): Promise<AnalyticsOverview> => {
    const res = await api.get<AnalyticsOverview>(`/analytics/overview?period_days=${period_days}`);
    return res.data;
  },
  getPerformance: async (): Promise<IncidentPerformance> => {
    const res = await api.get<IncidentPerformance>('/analytics/incident-performance');
    return res.data;
  },
  getImpact: async (): Promise<BusinessImpact> => {
    const res = await api.get<BusinessImpact>('/analytics/business-impact');
    return res.data;
  },
  getTrends: async (days = 14): Promise<TrendPoint[]> => {
    const res = await api.get<TrendPoint[]>(`/analytics/trends?days=${days}`);
    return res.data;
  },
};

// ==========================================
// Audit Logs
// ==========================================
export const auditService = {
  list: async (params?: { page?: number; page_size?: number; actor_id?: string; entity_type?: string }): Promise<PaginatedResponse<AuditLog>> => {
    const res = await api.get<PaginatedResponse<AuditLog>>('/audit-logs', { params });
    return res.data;
  },
  getExportUrl: (format = 'csv'): string => {
    const base = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    return `${base}/audit-logs/export?format=${format}`;
  },
};

// ==========================================
// Integrations
// ==========================================
export const integrationService = {
  list: async (): Promise<IntegrationStatus[]> => {
    const res = await api.get<IntegrationStatus[]>('/integrations');
    return res.data;
  },
  test: async (id: string): Promise<any> => {
    const res = await api.post(`/integrations/${id}/test`);
    return res.data;
  },
};
