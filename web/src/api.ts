import { authHeaders, clearToken, getToken } from "./auth";

const base = "/api/v1";

export type Category = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  owner_id: number | null;
  is_system: boolean;
};

export type Question = {
  id: number;
  category_id: number;
  text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_index: number;
  owner_id: number | null;
  is_system: boolean;
};

export class ApiError extends Error {
  readonly status: number;
  readonly body?: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

type ValidationErr = { loc?: unknown[]; msg?: string; type?: string };

function formatDetail(payload: unknown): string {
  if (payload === null || payload === undefined) return "İstek başarısız";
  if (typeof payload === "string") return payload;
  if (typeof payload === "object" && payload !== null && "detail" in payload) {
    const d = (payload as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) {
      const parts = (d as ValidationErr[])
        .map((e) => {
          const loc = Array.isArray(e.loc) ? e.loc.filter((x) => x !== "body").join(".") : "";
          const msg = e.msg ?? "";
          return loc ? `${loc}: ${msg}` : msg;
        })
        .filter(Boolean);
      if (parts.length) return parts.join("; ");
    }
  }
  try {
    return JSON.stringify(payload);
  } catch {
    return "İstek başarısız";
  }
}

async function parseError(res: Response): Promise<{ message: string; body: unknown }> {
  let body: unknown;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  return { message: formatDetail(body) || res.statusText || "İstek başarısız", body };
}

function mergeAuth(init?: RequestInit): RequestInit {
  const headers = new Headers(init?.headers);
  const auth = authHeaders();
  if (auth.Authorization) headers.set("Authorization", auth.Authorization);
  return { ...init, headers };
}

async function requestJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const hadToken = Boolean(getToken());
  const res = await fetch(input, mergeAuth(init));
  if (res.status === 401 && hadToken) {
    clearToken();
    window.dispatchEvent(new CustomEvent("quiz-auth-lost"));
  }
  if (!res.ok) {
    const { message, body } = await parseError(res);
    throw new ApiError(message, res.status, body);
  }
  return res.json() as Promise<T>;
}

export async function fetchCategories(): Promise<Category[]> {
  return requestJson(`${base}/categories`);
}

export async function createCategory(body: {
  name: string;
  slug: string;
  description?: string | null;
}): Promise<Category> {
  return requestJson(`${base}/categories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function fetchQuestions(categoryId: number): Promise<Question[]> {
  const q = new URLSearchParams({ category_id: String(categoryId) });
  return requestJson(`${base}/questions?${q}`);
}

export async function createQuestion(body: {
  category_id: number;
  text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_index: number;
}): Promise<Question> {
  return requestJson(`${base}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function deleteQuestion(id: number): Promise<void> {
  const hadToken = Boolean(getToken());
  const res = await fetch(`${base}/questions/${id}`, mergeAuth({ method: "DELETE" }));
  if (res.status === 401 && hadToken) {
    clearToken();
    window.dispatchEvent(new CustomEvent("quiz-auth-lost"));
  }
  if (!res.ok) {
    const { message, body } = await parseError(res);
    throw new ApiError(message, res.status, body);
  }
}
