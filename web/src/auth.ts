const TOKEN_KEY = "quiz_admin_token";

/** Önce localStorage; yoksa sessionStorage (eski sürüm) — böylece localhost / 127.0.0.1 karışımında daha az kopma olur */
export function getToken(): string | null {
  let t = localStorage.getItem(TOKEN_KEY);
  if (!t) {
    t = sessionStorage.getItem(TOKEN_KEY);
    if (t) {
      localStorage.setItem(TOKEN_KEY, t);
      sessionStorage.removeItem(TOKEN_KEY);
    }
  }
  return t;
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  sessionStorage.removeItem(TOKEN_KEY);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TOKEN_KEY);
}

export function authHeaders(): Record<string, string> {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

export async function loginRequest(username: string, password: string): Promise<void> {
  const r = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!r.ok) {
    let msg = "Giriş başarısız";
    try {
      const j = (await r.json()) as { detail?: unknown };
      if (typeof j.detail === "string") msg = j.detail;
    } catch {
      /* ignore */
    }
    throw new Error(msg);
  }
  const data = (await r.json()) as { access_token: string };
  setToken(data.access_token);
}

export type Me = { id: number; username: string; role: string };

export async function registerRequest(username: string, password: string): Promise<void> {
  const r = await fetch("/api/v1/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!r.ok) {
    let msg = "Kayıt başarısız";
    try {
      const j = (await r.json()) as { detail?: unknown };
      if (typeof j.detail === "string") msg = j.detail;
    } catch {
      /* ignore */
    }
    throw new Error(msg);
  }
}

export async function fetchMe(): Promise<Me> {
  const r = await fetch("/api/v1/auth/me", { headers: { ...authHeaders() } });
  if (!r.ok) {
    clearToken();
    window.dispatchEvent(new CustomEvent("quiz-auth-lost"));
    throw new Error("Oturum geçersiz veya süresi dolmuş.");
  }
  return r.json() as Promise<Me>;
}

export function logout(): void {
  clearToken();
}
