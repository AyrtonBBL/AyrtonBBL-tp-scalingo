// L'URL de l'API vient TOUJOURS de VITE_API_URL (jamais en dur).
export const API_URL = buildBaseUrl(import.meta.env.VITE_API_URL);

export function buildBaseUrl(raw: string | undefined): string {
  if (!raw) throw new Error("VITE_API_URL n'est pas définie (voir client/.env.example)");
  return raw.replace(/\/+$/, "");
}

export type Note = { id: number; title: string; content: string; created_at: string };

const TOKEN_KEY = "token";
export const auth = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = auth.get();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : `Erreur ${res.status}`;
    throw new ApiError(res.status, detail);
  }
  return (res.status === 204 ? undefined : await res.json()) as T;
}

export const api = {
  register: (email: string, password: string) =>
    request("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  listNotes: () => request<Note[]>("/notes"),
  createNote: (title: string, content: string) =>
    request<Note>("/notes", { method: "POST", body: JSON.stringify({ title, content }) }),
  deleteNote: (id: number) => request<void>(`/notes/${id}`, { method: "DELETE" }),
};
