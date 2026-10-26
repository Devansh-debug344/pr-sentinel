export type User = { id: string; email: string; created_at: string };
export type Conversation = { id: string; title: string | null; created_at: string; updated_at: string };
export type Message = { id: string; conversation_id: string; role: "user" | "assistant" | "system"; content: string; created_at: string; updated_at: string };
export type Page<T> = { items: T[]; next_cursor: string | null };
export type Turn = { request_id: string; assistant_message_id: string; content: string; model: string; provider: string; usage: { input_tokens: number | null; output_tokens: number | null; total_tokens: number | null } };
