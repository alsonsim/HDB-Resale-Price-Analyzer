import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

// --- Types ---

export interface Transaction {
  id: number;
  month: string;
  town: string;
  flat_type: string;
  block: string;
  street_name: string;
  storey_range: string;
  floor_area_sqm: number;
  flat_model: string;
  lease_commence_date: string;
  remaining_lease: string;
  resale_price: number;
  price_per_sqm: number | null;
}

export interface TrendPoint {
  month: string;
  median_price: number;
  avg_price: number;
  transaction_count: number;
  avg_psm: number;
}

export interface TrendData {
  town: string;
  flat_type: string | null;
  data: TrendPoint[];
}

export interface AnalysisResult {
  is_fair: boolean;
  fair_price_range: [number, number];
  price_vs_median_pct: number;
  summary: string;
  ai_insight: string;
  comparable_transactions: Transaction[];
}

export interface Alert {
  id: number;
  town: string;
  flat_type: string;
  max_price: number;
  is_active: boolean;
  created_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// --- API calls ---

export async function getTransactions(params: {
  town?: string;
  flat_type?: string;
  limit?: number;
}) {
  const { data } = await api.get<Transaction[]>("/transactions", { params });
  return data;
}

export async function getTrends(town: string, flatType?: string) {
  const { data } = await api.get<TrendData>(`/trends/${town}`, {
    params: flatType ? { flat_type: flatType } : {},
  });
  return data;
}

export async function analyzeListing(params: {
  town: string;
  flat_type: string;
  asking_price: number;
  floor_area_sqm?: number;
  storey_range?: string;
}) {
  const { data } = await api.post<AnalysisResult>("/analyze", params);
  return data;
}

export async function sendChatMessage(message: string, sessionId?: string) {
  const { data } = await api.post<{
    reply: string;
    session_id: string;
    data: Record<string, unknown> | null;
  }>("/chat", { message, session_id: sessionId });
  return data;
}

export async function syncDataGov(town?: string, limit = 1000) {
  const { data } = await api.post("/scrape/datagov", null, {
    params: { town, limit },
  });
  return data;
}

export async function getAlerts() {
  const { data } = await api.get<Alert[]>("/alerts");
  return data;
}

export async function createAlert(alert: {
  town: string;
  flat_type: string;
  max_price: number;
}) {
  const { data } = await api.post<Alert>("/alerts", alert);
  return data;
}

export async function deleteAlert(id: number) {
  await api.delete(`/alerts/${id}`);
}

export async function getTowns() {
  const { data } = await api.get<{ towns: string[] }>("/towns");
  return data.towns;
}

export async function getFlatTypes() {
  const { data } = await api.get<{ flat_types: string[] }>("/flat-types");
  return data.flat_types;
}

export default api;
