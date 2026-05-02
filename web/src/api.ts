const base = "/api/v1";

export type Category = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
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
};

async function parseError(res: Response): Promise<string> {
  try {
    const j = (await res.json()) as { detail?: unknown };
    if (typeof j.detail === "string") return j.detail;
    if (Array.isArray(j.detail)) return JSON.stringify(j.detail);
  } catch {
    /* ignore */
  }
  return res.statusText || "İstek başarısız";
}

export async function fetchCategories(): Promise<Category[]> {
  const r = await fetch(`${base}/categories`);
  if (!r.ok) throw new Error(await parseError(r));
  return r.json();
}

export async function createCategory(body: {
  name: string;
  slug: string;
  description?: string | null;
}): Promise<Category> {
  const r = await fetch(`${base}/categories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await parseError(r));
  return r.json();
}

export async function fetchQuestions(categoryId: number): Promise<Question[]> {
  const q = new URLSearchParams({ category_id: String(categoryId) });
  const r = await fetch(`${base}/questions?${q}`);
  if (!r.ok) throw new Error(await parseError(r));
  return r.json();
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
  const r = await fetch(`${base}/questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await parseError(r));
  return r.json();
}

export async function deleteQuestion(id: number): Promise<void> {
  const r = await fetch(`${base}/questions/${id}`, { method: "DELETE" });
  if (!r.ok) throw new Error(await parseError(r));
}
