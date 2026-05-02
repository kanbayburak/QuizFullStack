import { useCallback, useEffect, useState } from "react";
import {
  createCategory,
  createQuestion,
  deleteQuestion,
  fetchCategories,
  fetchQuestions,
  type Category,
  type Question,
} from "./api";
import "./App.css";

function App() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [catName, setCatName] = useState("");
  const [catSlug, setCatSlug] = useState("");
  const [catDesc, setCatDesc] = useState("");

  const [qText, setQText] = useState("");
  const [qA, setQA] = useState("");
  const [qB, setQB] = useState("");
  const [qC, setQC] = useState("");
  const [qD, setQD] = useState("");
  const [qCorrect, setQCorrect] = useState(0);

  const loadCategories = useCallback(async () => {
    setError(null);
    const list = await fetchCategories();
    setCategories(list);
    setSelectedId((prev) => {
      if (prev !== null && list.some((c) => c.id === prev)) return prev;
      return list[0]?.id ?? null;
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        await loadCategories();
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Yükleme hatası");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [loadCategories]);

  useEffect(() => {
    if (selectedId === null) {
      setQuestions([]);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const list = await fetchQuestions(selectedId);
        if (!cancelled) setQuestions(list);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Sorular yüklenemedi");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  const onAddCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await createCategory({
        name: catName,
        slug: catSlug || catName.toLowerCase().replace(/\s+/g, "-"),
        description: catDesc || null,
      });
      setCatName("");
      setCatSlug("");
      setCatDesc("");
      await loadCategories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kategori eklenemedi");
    }
  };

  const onAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedId === null) return;
    setError(null);
    try {
      await createQuestion({
        category_id: selectedId,
        text: qText,
        option_a: qA,
        option_b: qB,
        option_c: qC,
        option_d: qD,
        correct_index: qCorrect,
      });
      setQText("");
      setQA("");
      setQB("");
      setQC("");
      setQD("");
      setQCorrect(0);
      setQuestions(await fetchQuestions(selectedId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Soru eklenemedi");
    }
  };

  const onDeleteQuestion = async (id: number) => {
    if (!confirm("Bu soruyu silmek istiyor musunuz?")) return;
    setError(null);
    try {
      await deleteQuestion(id);
      if (selectedId !== null) setQuestions(await fetchQuestions(selectedId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Silinemedi");
    }
  };

  const selected = categories.find((c) => c.id === selectedId);

  return (
    <div className="layout">
      <header className="header">
        <h1>Quiz yönetim paneli</h1>
        <p className="muted">
          Kategoriler ve sorular API üzerinden yönetilir; mobil uygulama aynı REST uçlarına bağlanabilir.
        </p>
      </header>

      {error && (
        <div className="banner error" role="alert">
          {error}
        </div>
      )}

      <div className="grid">
        <aside className="card">
          <h2>Kategoriler</h2>
          {loading ? (
            <p className="muted">Yükleniyor…</p>
          ) : (
            <ul className="cat-list">
              {categories.map((c) => (
                <li key={c.id}>
                  <button
                    type="button"
                    className={c.id === selectedId ? "cat active" : "cat"}
                    onClick={() => setSelectedId(c.id)}
                  >
                    <span className="cat-name">{c.name}</span>
                    <span className="cat-slug">{c.slug}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          <form className="form" onSubmit={onAddCategory}>
            <h3>Yeni kategori</h3>
            <label>
              Ad
              <input value={catName} onChange={(e) => setCatName(e.target.value)} required />
            </label>
            <label>
              Slug (opsiyonel)
              <input
                value={catSlug}
                onChange={(e) => setCatSlug(e.target.value)}
                placeholder="ör. custom-topic"
              />
            </label>
            <label>
              Açıklama
              <input value={catDesc} onChange={(e) => setCatDesc(e.target.value)} />
            </label>
            <button type="submit">Kategori ekle</button>
          </form>
        </aside>

        <main className="card main">
          <h2>Sorular</h2>
          {selected ? (
            <p className="muted">
              Seçili: <strong>{selected.name}</strong> — {selected.description ?? "—"}
            </p>
          ) : (
            <p className="muted">Önce bir kategori seçin veya ekleyin.</p>
          )}

          {selectedId !== null && (
            <form className="form question-form" onSubmit={onAddQuestion}>
              <h3>Yeni soru</h3>
              <label className="full">
                Soru metni
                <textarea value={qText} onChange={(e) => setQText(e.target.value)} rows={3} required />
              </label>
              <div className="options-grid">
                <label>
                  Şık A
                  <input value={qA} onChange={(e) => setQA(e.target.value)} required />
                </label>
                <label>
                  Şık B
                  <input value={qB} onChange={(e) => setQB(e.target.value)} required />
                </label>
                <label>
                  Şık C
                  <input value={qC} onChange={(e) => setQC(e.target.value)} required />
                </label>
                <label>
                  Şık D
                  <input value={qD} onChange={(e) => setQD(e.target.value)} required />
                </label>
              </div>
              <label>
                Doğru şık
                <select value={qCorrect} onChange={(e) => setQCorrect(Number(e.target.value))}>
                  <option value={0}>A</option>
                  <option value={1}>B</option>
                  <option value={2}>C</option>
                  <option value={3}>D</option>
                </select>
              </label>
              <button type="submit">Soru ekle</button>
            </form>
          )}

          {selectedId !== null && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Metin</th>
                    <th>Doğru</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {questions.map((q) => (
                    <tr key={q.id}>
                      <td>{q.id}</td>
                      <td className="q-text">{q.text}</td>
                      <td>{["A", "B", "C", "D"][q.correct_index]}</td>
                      <td>
                        <button type="button" className="btn-danger" onClick={() => onDeleteQuestion(q.id)}>
                          Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {questions.length === 0 && <p className="muted pad">Bu kategoride henüz soru yok.</p>}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
