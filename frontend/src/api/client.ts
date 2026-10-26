import type { Conversation, Message, Page, Turn, User } from "./types";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api";
export class ApiError extends Error { constructor(public status: number, message: string) { super(message); } }
async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init.headers } });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new ApiError(response.status, body.detail ?? "Request failed"); }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}
export const api = {
  register: (email: string, password: string) => request<User>("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),
  login: (email: string, password: string) => request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: (token: string) => request<void>("/auth/logout", { method: "POST" }, token),
  me: (token: string) => request<User>("/auth/me", {}, token),
  conversations: (token: string, cursor?: string) => request<Page<Conversation>>(`/conversations?limit=30${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`, {}, token),
  createConversation: (token: string, title?: string) => request<Conversation>("/conversations", { method: "POST", headers: { "Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({ title: title || null }) }, token),
  deleteConversation: (token: string, id: string) => request<void>(`/conversations/${id}`, { method: "DELETE" }, token),
  messages: (token: string, id: string, cursor?: string) => request<Page<Message>>(`/conversations/${id}/messages?limit=30${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`, {}, token),
  send: (token: string, id: string, content: string) => request<Turn>(`/conversations/${id}/messages`, { method: "POST", headers: { "Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify({ content }) }, token)
};
