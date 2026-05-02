import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  createCategory,
  createQuestion,
  deleteQuestion,
  fetchCategories,
  fetchQuestions,
  type Category,
  type Question,
} from "./api";
import {
  fetchMe,
  getToken,
  loginRequest,
  logout as logoutAuth,
  registerRequest,
  type Me,
} from "./auth";
import "./App.css";

function errMsg(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  if (e instanceof Error) return e.message;
  return "Bilinmeyen hata";
}

function LoginScreen({
  onSuccess,
  onCancel,
}: {
  onSuccess: () => void | Promise<void>;
  onCancel?: () => void;
}) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setPending(true);
    try {
      const u = username.trim();
      if (mode === "register") {
        if (u.length < 3) {
          setError("Kullanıcı adı en az 3 karakter olmalı.");
          return;
        }
        if (password !== password2) {
          setError("Şifreler eşleşmiyor.");
          return;
        }
        await registerRequest(u, password);
        await loginRequest(u, password);
      } else {
        await loginRequest(u, password);
      }
      await onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "İşlem başarısız");
    } finally {
      setPending(false);
    }
  };

  return (
    <div className="login-layout">
      <div className="login-card card">
        <div className="login-card-head">
          <h1>{mode === "login" ? "Giriş yap" : "Kayıt ol"}</h1>
          {onCancel ? (
            <button type="button" className="btn-dismiss-login" onClick={onCancel}>
              Kapat
            </button>
          ) : null}
        </div>
        <p className="muted">
          {mode === "login"
            ? "Hesabın yoksa kayıt olabilirsin. Giriş yapan kullanıcılar quiz içeriğini düzenleyebilir."
            : "Ücretsiz hesap oluştur. Kayıt sonrası aynı bilgilerle oturum açılır."}
        </p>
        <div className="auth-tabs">
          <button
            type="button"
            className={mode === "login" ? "auth-tab active" : "auth-tab"}
            onClick={() => {
              setMode("login");
              setError(null);
            }}
          >
            Giriş
          </button>
          <button
            type="button"
            className={mode === "register" ? "auth-tab active" : "auth-tab"}
            onClick={() => {
              setMode("register");
              setError(null);
            }}
          >
            Kayıt ol
          </button>
        </div>
        {error && (
          <div className="banner error" role="alert">
            {error}
          </div>
        )}
        <form className="form" onSubmit={submit}>
          <label>
            Kullanıcı adı
            <input
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={mode === "register" ? 3 : 1}
              disabled={pending}
            />
          </label>
          <label>
            Şifre
            <input
              type="password"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={4}
              disabled={pending}
            />
          </label>
          {mode === "register" && (
            <label>
              Şifre tekrar
              <input
                type="password"
                autoComplete="new-password"
                value={password2}
                onChange={(e) => setPassword2(e.target.value)}
                required
                minLength={4}
                disabled={pending}
              />
            </label>
          )}
          <button type="submit" disabled={pending}>
            {pending ? (
              <>
                <span className="spinner-inline" aria-hidden />
                {mode === "register" ? "Kaydediliyor…" : "Giriş yapılıyor…"}
              </>
            ) : mode === "register" ? (
              "Hesap oluştur"
            ) : (
              "Giriş yap"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

function App() {
  const [me, setMe] = useState<Me | null>(null);
  const [authChecking, setAuthChecking] = useState(true);
  const [showLogin, setShowLogin] = useState(false);

  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [questionsLoading, setQuestionsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [submittingCat, setSubmittingCat] = useState(false);
  const [submittingQ, setSubmittingQ] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const [catName, setCatName] = useState("");
  const [catSlug, setCatSlug] = useState("");
  const [catDesc, setCatDesc] = useState("");

  const [qText, setQText] = useState("");
  const [qA, setQA] = useState("");
  const [qB, setQB] = useState("");
  const [qC, setQC] = useState("");
  const [qD, setQD] = useState("");
  const [qCorrect, setQCorrect] = useState(0);

  useEffect(() => {
    const onLost = () => setMe(null);
    window.addEventListener("quiz-auth-lost", onLost);
    return () => window.removeEventListener("quiz-auth-lost", onLost);
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!getToken()) {
        setAuthChecking(false);
        return;
      }
      try {
        const u = await fetchMe();
        if (!cancelled) setMe(u);
      } catch {
        if (!cancelled) setMe(null);
      } finally {
        if (!cancelled) setAuthChecking(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

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
    if (authChecking) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        await loadCategories();
      } catch (e) {
        if (!cancelled) setError(errMsg(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [authChecking, me?.id, loadCategories]);

  useEffect(() => {
    if (selectedId === null) {
      setQuestions([]);
      return;
    }
    let cancelled = false;
    (async () => {
      setQuestionsLoading(true);
      try {
        const list = await fetchQuestions(selectedId);
        if (!cancelled) setQuestions(list);
      } catch (e) {
        if (!cancelled) setError(errMsg(e));
      } finally {
        if (!cancelled) setQuestionsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  const onAddCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!me) return;
    setError(null);
    setSubmittingCat(true);
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
      setError(errMsg(err));
    } finally {
      setSubmittingCat(false);
    }
  };

  const onAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!me || selectedId === null) return;
    setError(null);
    setSubmittingQ(true);
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
      setError(errMsg(err));
    } finally {
      setSubmittingQ(false);
    }
  };

  const onDeleteQuestion = async (id: number) => {
    if (!me) return;
    if (!confirm("Bu soruyu silmek istiyor musunuz?")) return;
    setError(null);
    setDeletingId(id);
    try {
      await deleteQuestion(id);
      if (selectedId !== null) setQuestions(await fetchQuestions(selectedId));
    } catch (err) {
      setError(errMsg(err));
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = () => {
    logoutAuth();
    setMe(null);
    void loadCategories();
  };

  const handleLoginSuccess = useCallback(async () => {
    try {
      const u = await fetchMe();
      setMe(u);
      setShowLogin(false);
    } catch {
      setMe(null);
    }
  }, []);

  const selected = categories.find((c) => c.id === selectedId);

  if (authChecking) {
    return (
      <div className="login-layout">
        <div className="login-card card">
          <p className="muted">
            <span className="spinner-inline" aria-hidden />
            Oturum kontrol ediliyor…
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="layout">
      <header className="header">
        <div className="header-top">
          <div>
            <h1>Quiz paneli</h1>
            <p className="muted">
              Varsayılan kategoriler ve sorular herkese açıktır. Giriş yaparak kendi kategorilerinizi ve sorularınızı
              ekleyebilirsiniz; varsayılan içerik salt okunurdur.
            </p>
          </div>
          <div className="user-bar">
            {me ? (
              <>
                <span className="user-label">{me.username}</span>
                <button type="button" className="btn-logout" onClick={handleLogout}>
                  Çıkış
                </button>
              </>
            ) : (
              <button type="button" className="btn-primary-outline" onClick={() => setShowLogin(true)}>
                Giriş yap
              </button>
            )}
          </div>
        </div>
        <div className="badge-row">
          <span className="badge">FastAPI</span>
          <span className="badge">PostgreSQL</span>
          <span className="badge">JWT</span>
          <span className="badge">React · Vite</span>
        </div>
      </header>

      {error && (
        <div className="banner error" role="alert">
          <span>{error}</span>
          <button type="button" className="dismiss" onClick={() => setError(null)}>
            Kapat
          </button>
        </div>
      )}

      <div className="grid">
        <aside className="card">
          <h2>Kategoriler</h2>
          {loading ? (
            <div className="skeleton" style={{ marginBottom: "1rem" }} aria-hidden />
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
                    <span className={`cat-origin ${c.is_system ? "system" : "mine"}`}>
                      {c.is_system ? "Varsayılan" : "Senin"}
                    </span>
                    <span className="cat-slug">{c.slug}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {me ? (
            <form className="form" onSubmit={onAddCategory}>
              <h3>Yeni kategori</h3>
              <label>
                Ad
                <input value={catName} onChange={(e) => setCatName(e.target.value)} required disabled={submittingCat} />
              </label>
              <label>
                Slug (opsiyonel)
                <input
                  value={catSlug}
                  onChange={(e) => setCatSlug(e.target.value)}
                  placeholder="ör. genel-kultur"
                  disabled={submittingCat}
                />
              </label>
              <label>
                Açıklama
                <input value={catDesc} onChange={(e) => setCatDesc(e.target.value)} disabled={submittingCat} />
              </label>
              <button type="submit" disabled={submittingCat}>
                {submittingCat ? (
                  <>
                    <span className="spinner-inline" aria-hidden />
                    Kaydediliyor…
                  </>
                ) : (
                  "Kategori ekle"
                )}
              </button>
            </form>
          ) : (
            <p className="muted pad">Kendi kategorinizi eklemek için giriş yapın.</p>
          )}
        </aside>

        <main className="card main">
          <h2>Sorular</h2>
          {selected ? (
            <p className="muted">
              Seçili: <strong>{selected.name}</strong>
              <span className={`cat-origin-inline ${selected.is_system ? "system" : "mine"}`}>
                {selected.is_system ? "Varsayılan kategori" : "Senin kategorin"}
              </span>
              {" — "}
              {selected.description ?? "—"}
            </p>
          ) : (
            <p className="muted">Önce bir kategori seçin veya ekleyin.</p>
          )}

          {me && selectedId !== null && (
            <form className="form question-form" onSubmit={onAddQuestion}>
              <h3>Yeni soru</h3>
              <label className="full">
                Soru metni
                <textarea value={qText} onChange={(e) => setQText(e.target.value)} rows={3} required disabled={submittingQ} />
              </label>
              <div className="options-grid">
                <label>
                  Şık A
                  <input value={qA} onChange={(e) => setQA(e.target.value)} required disabled={submittingQ} />
                </label>
                <label>
                  Şık B
                  <input value={qB} onChange={(e) => setQB(e.target.value)} required disabled={submittingQ} />
                </label>
                <label>
                  Şık C
                  <input value={qC} onChange={(e) => setQC(e.target.value)} required disabled={submittingQ} />
                </label>
                <label>
                  Şık D
                  <input value={qD} onChange={(e) => setQD(e.target.value)} required disabled={submittingQ} />
                </label>
              </div>
              <label>
                Doğru şık
                <select value={qCorrect} onChange={(e) => setQCorrect(Number(e.target.value))} disabled={submittingQ}>
                  <option value={0}>A</option>
                  <option value={1}>B</option>
                  <option value={2}>C</option>
                  <option value={3}>D</option>
                </select>
              </label>
              <button type="submit" disabled={submittingQ}>
                {submittingQ ? (
                  <>
                    <span className="spinner-inline" aria-hidden />
                    Ekleniyor…
                  </>
                ) : (
                  "Soru ekle"
                )}
              </button>
            </form>
          )}

          {!me && selectedId !== null && (
            <p className="muted pad">Soru eklemek için giriş yapın. Varsayılan soruları görüntüleyebilirsiniz.</p>
          )}

          {selectedId !== null && (
            <div className="table-wrap">
              {questionsLoading ? (
                <p className="muted">
                  <span className="spinner-inline" aria-hidden />
                  Sorular yükleniyor…
                </p>
              ) : (
                <>
                  <table>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Metin</th>
                        <th>Kaynak</th>
                        <th>Doğru</th>
                        <th />
                      </tr>
                    </thead>
                    <tbody>
                      {questions.map((q) => (
                        <tr key={q.id}>
                          <td>{q.id}</td>
                          <td className="q-text">{q.text}</td>
                          <td>
                            <span className={`cat-origin ${q.is_system ? "system" : "mine"}`}>
                              {q.is_system ? "Varsayılan" : "Senin"}
                            </span>
                          </td>
                          <td>{["A", "B", "C", "D"][q.correct_index]}</td>
                          <td>
                            {me && !q.is_system ? (
                              <button
                                type="button"
                                className="btn-danger"
                                onClick={() => onDeleteQuestion(q.id)}
                                disabled={deletingId !== null}
                              >
                                {deletingId === q.id ? "…" : "Sil"}
                              </button>
                            ) : (
                              <span className="muted tiny">—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {questions.length === 0 && <p className="muted pad">Bu kategoride henüz soru yok.</p>}
                </>
              )}
            </div>
          )}
        </main>
      </div>

      {!me && showLogin && (
        <div className="login-overlay" role="dialog" aria-modal="true" aria-label="Giriş">
          <LoginScreen onSuccess={handleLoginSuccess} onCancel={() => setShowLogin(false)} />
        </div>
      )}
    </div>
  );
}

export default App;
