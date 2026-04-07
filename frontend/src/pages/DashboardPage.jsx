import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import MarkdownMessage from "../components/MarkdownMessage";

function buildMessage(role, content, sources = []) {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    role,
    content,
    sources,
    ts: new Date().toISOString(),
  };
}

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (_err) {
    return "";
  }
}

export default function DashboardPage() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState("");
  const [repoFilter, setRepoFilter] = useState("");
  const [showAddRepo, setShowAddRepo] = useState(false);
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [messagesByRepo, setMessagesByRepo] = useState({});
  const [isSwitchingRepo, setIsSwitchingRepo] = useState(false);
  const [isRepoLoading, setIsRepoLoading] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [toasts, setToasts] = useState([]);

  const chatEndRef = useRef(null);
  const composerRef = useRef(null);

  const selectedRepoLabel = useMemo(
    () => selectedRepo || "No repo selected",
    [selectedRepo]
  );

  const visibleRepos = useMemo(() => {
    const query = repoFilter.trim().toLowerCase();
    if (!query) {
      return repos;
    }
    return repos.filter((repo) => {
      const name = (repo.repo_name || "").toLowerCase();
      const ns = (repo.namespace || "").toLowerCase();
      return name.includes(query) || ns.includes(query);
    });
  }, [repoFilter, repos]);

  const activeMessages = useMemo(
    () => messagesByRepo[selectedRepo] || [],
    [messagesByRepo, selectedRepo]
  );

  const addToast = (message, type = "info") => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 2600);
  };

  const appendMessage = (repoName, message) => {
    if (!repoName) {
      return;
    }
    setMessagesByRepo((prev) => ({
      ...prev,
      [repoName]: [...(prev[repoName] || []), message],
    }));
  };

  const loadRepos = async () => {
    setIsRepoLoading(true);

    try {
      const res = await api.get("/repos/");
      const nextRepos = res?.data?.repos || [];
      setRepos(nextRepos);

      if (!selectedRepo && nextRepos.length > 0) {
        setSelectedRepo(nextRepos[0].repo_name);
      }
    } catch (err) {
      addToast(
        err?.response?.data?.detail || "Failed to load repositories",
        "error"
      );
    } finally {
      setIsRepoLoading(false);
    }
  };

  useEffect(() => {
    loadRepos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleIngest = async (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) {
      addToast("Please enter a valid repository URL.", "warn");
      return;
    }
    setIsIngesting(true);

    try {
      const res = await api.post("/ingest", { repo_url: repoUrl });
      const repoName = res?.data?.repo_name;
      setRepoUrl("");
      await loadRepos();

      if (repoName) {
        setSelectedRepo(repoName);
        addToast(`Repository ${repoName} ingested successfully.`, "success");
      } else {
        addToast("Repository ingested.", "success");
      }

      setShowAddRepo(false);
      setTimeout(() => {
        composerRef.current?.focus();
      }, 120);
    } catch (err) {
      addToast(err?.response?.data?.detail || "Ingestion failed", "error");
    } finally {
      setIsIngesting(false);
    }
  };

  const handleAsk = async (e, forcedQuestion = "") => {
    e.preventDefault();
    if (!selectedRepo) {
      addToast("Please select a repository first.", "warn");
      return;
    }

    const nextQuestion = (forcedQuestion || question).trim();
    if (!nextQuestion) {
      return;
    }

    setIsAsking(true);

    appendMessage(selectedRepo, buildMessage("user", nextQuestion));
    setQuestion("");

    try {
      const res = await api.post("/query/", {
        question: nextQuestion,
        repo_name: selectedRepo,
        top_k: 8,
      });

      appendMessage(
        selectedRepo,
        buildMessage(
          "assistant",
          res?.data?.answer || "No answer received.",
          res?.data?.sources || []
        )
      );
    } catch (err) {
      addToast(err?.response?.data?.detail || "Query failed", "error");
    } finally {
      setIsAsking(false);
      setTimeout(() => {
        composerRef.current?.focus();
      }, 80);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [activeMessages, isAsking, selectedRepo]);

  useEffect(() => {
    if (!selectedRepo) {
      return;
    }
    setIsSwitchingRepo(true);
    const id = setTimeout(() => setIsSwitchingRepo(false), 120);
    return () => clearTimeout(id);
  }, [selectedRepo]);

  const onSelectRepo = (repoName) => {
    setSelectedRepo(repoName);
  };

  const handleComposerKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk(e);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="dashboard-shell">
      <div className="toast-stack" aria-live="polite" aria-atomic="true">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast toast-${toast.type}`}>
            {toast.message}
          </div>
        ))}
      </div>

      <aside className="rag-sidebar">
        <button
          type="button"
          className="add-repo-btn"
          onClick={() => setShowAddRepo((prev) => !prev)}
        >
          + Add Repository
        </button>

        <div className="repo-search-wrap">
          <input
            type="text"
            placeholder="Search repositories"
            value={repoFilter}
            onChange={(e) => setRepoFilter(e.target.value)}
            aria-label="Search repositories"
          />
        </div>

        <div className="sidebar-header">
          <h2>Repositories</h2>
          <button
            className="ghost-btn"
            onClick={loadRepos}
            disabled={isRepoLoading}
            type="button"
          >
            {isRepoLoading ? "Loading" : "Refresh"}
          </button>
        </div>

        <div className="repo-list" role="listbox" aria-label="Repository list">
          {visibleRepos.length === 0 && (
            <p className="muted">No repositories found.</p>
          )}

          {visibleRepos.map((repo) => (
            <button
              key={`${repo.user_id}-${repo.repo_name}`}
              className={
                selectedRepo === repo.repo_name
                  ? "repo-item active"
                  : "repo-item"
              }
              onClick={() => onSelectRepo(repo.repo_name)}
              type="button"
              role="option"
              aria-selected={selectedRepo === repo.repo_name}
            >
              <strong>{repo.repo_name}</strong>
              <span className="muted small">{repo.namespace}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-bottom">
          <p className="muted small">Signed in</p>
          <button className="signout-btn" onClick={handleLogout} type="button">
            Sign Out
          </button>
        </div>
      </aside>

      <main className="chat-layout">
        <header className="chat-header">
          <div>
            <h1>Repository Assistant</h1>
            <p className="muted">Workspace: {selectedRepoLabel}</p>
          </div>

          {showAddRepo && (
            <form className="ingest-form" onSubmit={handleIngest}>
              <input
                type="url"
                placeholder="https://github.com/owner/repo"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                required
              />
              <button type="submit" disabled={isIngesting}>
                {isIngesting ? "Adding..." : "Add"}
              </button>
            </form>
          )}
        </header>

        <section
          className={
            isSwitchingRepo ? "chat-window switch-fade" : "chat-window"
          }
        >
          {activeMessages.length === 0 ? (
            <div className="empty-chat">
              <p className="muted">
                Ask about this repository. Your messages stay isolated per
                repository workspace.
              </p>
            </div>
          ) : (
            activeMessages.map((msg) => (
              <article
                key={msg.id}
                className={
                  msg.role === "user"
                    ? "chat-bubble user"
                    : "chat-bubble assistant"
                }
              >
                <div className="chat-meta">
                  <span>{msg.role === "user" ? "You" : "Assistant"}</span>
                  <span>{formatTime(msg.ts)}</span>
                </div>

                <div className="chat-content">
                  <MarkdownMessage content={msg.content} />
                </div>

                {msg.sources?.length > 0 && (
                  <details className="source-list">
                    <summary>Sources ({msg.sources.length})</summary>
                    <ul>
                      {msg.sources.map((src, i) => (
                        <li key={`${src.source}-${i}`}>
                          <strong>{src.source}</strong>
                          <p className="small muted">{src.chunk_preview}</p>
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </article>
            ))
          )}

          {isAsking && (
            <article className="chat-bubble assistant typing-bubble">
              <div className="chat-meta">
                <span>Assistant</span>
                <span>typing</span>
              </div>
              <div className="typing-dots" aria-label="Assistant is typing">
                <span />
                <span />
                <span />
              </div>
            </article>
          )}

          <div ref={chatEndRef} />
        </section>

        <form className="composer-wrap" onSubmit={handleAsk}>
          <textarea
            ref={composerRef}
            placeholder="Ask about architecture, files, bugs, or design decisions..."
            rows={2}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleComposerKeyDown}
            disabled={isAsking || !selectedRepo}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={isAsking || !selectedRepo || !question.trim()}
          >
            {isAsking ? "Sending" : "Send"}
          </button>
        </form>
      </main>
    </div>
  );
}
