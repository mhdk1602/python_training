import Head from "next/head";
import Link from "next/link";
import React, { startTransition, useDeferredValue, useEffect, useState } from "react";

import styles from "../../styles/chapter10.module.css";

type TagResult = {
  tag_key: string;
  value: string;
  confidence: number;
  method: string;
  evidence: string;
};

type SearchResult = {
  chunk_id: string;
  score: number;
  source_id: string;
  title: string;
  snippet: string;
  tags: TagResult[];
  metadata: Record<string, string>;
};

type Citation = {
  source_id: string;
  title: string;
  source_url: string;
  quote: string;
};

type AnswerResponse = {
  answer: string;
  citations: Citation[];
  matched_tags: TagResult[];
  applied_filters: Record<string, string>;
  warning?: string | null;
  trace: Array<Record<string, unknown>>;
};

type AgentStep = {
  tool: string;
  input_summary: string;
  output_summary: string;
};

type AgentResponse = {
  mode: string;
  answer_response?: AnswerResponse | null;
  source_preview?: Record<string, unknown> | null;
  tag_explanation?: Record<string, unknown> | null;
  trace: AgentStep[];
};

type SourcePreview = {
  source_id: string;
  title: string;
  summary: string;
  body: string;
  metadata: Record<string, string>;
  tags: TagResult[];
  source_url: string;
};

const API_BASE = process.env.NEXT_PUBLIC_RAG_LAB_API_BASE || "http://localhost:8001";

const FILTERS: Array<{ key: string; label: string; value: Record<string, string> }> = [
  { key: "all", label: "All sources", value: {} },
  { key: "zion", label: "Zion", value: { park_code: "zion" } },
  { key: "arches", label: "Arches", value: { park_code: "arch" } },
  { key: "accessible", label: "Accessible", value: { tag_accessible: "true" } },
  { key: "family", label: "Family-friendly", value: { tag_family_friendly: "true" } },
];

const FALLBACK_RESULTS: SearchResult[] = [
  {
    chunk_id: "nps-zion-riverside::chunk-0",
    score: 0.88,
    source_id: "nps-zion-riverside",
    title: "Riverside Walk",
    snippet:
      "Riverside Walk is one of the park's most approachable experiences. The path is paved, the terrain is gentle, and many visitors treat it as a low-friction introduction.",
    tags: [
      {
        tag_key: "accessible",
        value: "true",
        confidence: 0.82,
        method: "rule",
        evidence: "Matched keyword 'paved' in content text.",
      },
      {
        tag_key: "family-friendly",
        value: "true",
        confidence: 0.82,
        method: "rule",
        evidence: "Matched keyword 'first-time' in content text.",
      },
    ],
    metadata: {
      park_code: "zion",
      park_name: "Zion National Park",
      source_url: "https://www.nps.gov/zion/planyourvisit/riverside-walk.htm",
    },
  },
  {
    chunk_id: "nps-zion-ranger-program::chunk-0",
    score: 0.64,
    source_id: "nps-zion-ranger-program",
    title: "Evening Ranger Program",
    snippet:
      "This evening program gives visitors current trail conditions, wildlife safety reminders, and a compact history of the canyon.",
    tags: [
      {
        tag_key: "ranger-led",
        value: "true",
        confidence: 0.82,
        method: "rule",
        evidence: "Matched keyword 'ranger' in content text.",
      },
    ],
    metadata: {
      park_code: "zion",
      park_name: "Zion National Park",
      source_url: "https://www.nps.gov/zion/planyourvisit/ranger-programs.htm",
    },
  },
];

const FALLBACK_ANSWER: AnswerResponse = {
  answer:
    "Riverside Walk is the best grounded first stop in this sample because it is explicitly described as paved, gentle, and useful as an introduction before committing to a longer day.",
  citations: [
    {
      source_id: "nps-zion-riverside",
      title: "Riverside Walk",
      source_url: "https://www.nps.gov/zion/planyourvisit/riverside-walk.htm",
      quote:
        "The path is paved, the terrain is gentle, and many visitors treat it as a low-friction introduction.",
    },
  ],
  matched_tags: FALLBACK_RESULTS[0].tags,
  applied_filters: { park_code: "zion" },
  warning: null,
  trace: [
    { step: "retrieval", top_k: 4, hits: 2 },
    { step: "answer", mode: "extractive" },
  ],
};

const FALLBACK_SOURCE: SourcePreview = {
  source_id: "nps-zion-riverside",
  title: "Riverside Walk",
  summary: "A paved route along the Virgin River that works well as an accessible first stop.",
  body:
    "Riverside Walk is one of the park's most approachable experiences. The path is paved, the terrain is gentle, and many visitors treat it as a low-friction introduction before deciding whether they want a longer day on the trail system.",
  metadata: { park_code: "zion", park_name: "Zion National Park", state: "UT" },
  tags: FALLBACK_RESULTS[0].tags,
  source_url: "https://www.nps.gov/zion/planyourvisit/riverside-walk.htm",
};

const FALLBACK_AGENT: AgentResponse = {
  mode: "tag-explanation",
  tag_explanation: {
    source_id: "nps-zion-riverside",
    title: "Riverside Walk",
    tags: FALLBACK_RESULTS[0].tags,
  },
  trace: [
    { tool: "search", input_summary: "Explain why this was tagged", output_summary: "Retrieved 2 candidate chunks." },
    { tool: "explain_tags", input_summary: "nps-zion-riverside", output_summary: "Explained 2 tags." },
  ],
};

const defaultQuestion = "What should a first-time visitor start with in Zion?";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

const Chapter10Lab: React.FC = () => {
  const [query, setQuery] = useState(defaultQuestion);
  const deferredQuery = useDeferredValue(query);
  const [filterKey, setFilterKey] = useState("zion");
  const [results, setResults] = useState<SearchResult[]>(FALLBACK_RESULTS);
  const [answer, setAnswer] = useState<AnswerResponse>(FALLBACK_ANSWER);
  const [agent, setAgent] = useState<AgentResponse | null>(null);
  const [sources, setSources] = useState<SourcePreview[]>([FALLBACK_SOURCE]);
  const [selectedSource, setSelectedSource] = useState<SourcePreview>(FALLBACK_SOURCE);
  const [status, setStatus] = useState<string>("offline fallback");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedFilter = FILTERS.find((filter) => filter.key === filterKey) || FILTERS[0];

  const activeTrace = agent?.trace.length ? agent.trace : answer.trace;
  const activeTags = agent?.tag_explanation?.tags
    ? (agent.tag_explanation.tags as TagResult[])
    : selectedSource.tags || answer.matched_tags;

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const [health, sourcePayload] = await Promise.all([
          fetchJson<{ backend: string; embedding_model: string }>(`${API_BASE}/health`),
          fetchJson<{ sources: SourcePreview[] }>(`${API_BASE}/sources`),
        ]);
        if (cancelled) return;
        startTransition(() => {
          setStatus(`${health.backend} · ${health.embedding_model}`);
          if (sourcePayload.sources.length > 0) {
            setSources(sourcePayload.sources);
            setSelectedSource(sourcePayload.sources[0]);
          }
        });
      } catch {
        if (cancelled) return;
        setStatus("offline fallback");
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  async function runMode(mode: "search" | "answer" | "agent") {
    setBusy(true);
    setError(null);

    try {
      if (mode === "search") {
        const payload = await fetchJson<{ results: SearchResult[] }>(`${API_BASE}/search`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query, filters: selectedFilter.value, top_k: 5 }),
        });
        startTransition(() => {
          setResults(payload.results);
          setAgent(null);
          if (payload.results[0]) {
            void loadSource(payload.results[0].source_id);
          }
        });
      } else if (mode === "answer") {
        const payload = await fetchJson<AnswerResponse>(`${API_BASE}/answer`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query, filters: selectedFilter.value, top_k: 4 }),
        });
        startTransition(() => {
          setAnswer(payload);
          setAgent(null);
          if (payload.citations[0]) {
            void loadSource(payload.citations[0].source_id);
          }
        });
      } else {
        const payload = await fetchJson<AgentResponse>(`${API_BASE}/agent`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query, filters: selectedFilter.value }),
        });
        startTransition(() => {
          setAgent(payload);
          if (payload.answer_response) {
            setAnswer(payload.answer_response);
          }
          const agentSourceId =
            (payload.source_preview?.source_id as string | undefined) ||
            (payload.tag_explanation?.source_id as string | undefined);
          if (agentSourceId) {
            void loadSource(agentSourceId);
          }
        });
      }
    } catch (runError) {
      startTransition(() => {
        setError(`Live API unavailable. Showing fallback ${mode} state.`);
        if (mode === "search") {
          setResults(FALLBACK_RESULTS);
        } else if (mode === "answer") {
          setAnswer(FALLBACK_ANSWER);
        } else {
          setAgent(FALLBACK_AGENT);
        }
        setSelectedSource(FALLBACK_SOURCE);
      });
    } finally {
      setBusy(false);
    }
  }

  async function loadSource(sourceId: string) {
    try {
      const payload = await fetchJson<SourcePreview>(`${API_BASE}/sources/${sourceId}`);
      startTransition(() => setSelectedSource(payload));
    } catch {
      const source = sources.find((item) => item.source_id === sourceId) || FALLBACK_SOURCE;
      startTransition(() => setSelectedSource(source));
    }
  }

  return (
    <>
      <Head>
        <title>Chapter 10 · Retrieval Systems and Agents</title>
        <meta
          name="description"
          content="A modern teaching surface for vector stores, content tagging, grounded answers, and bounded agents."
        />
      </Head>

      <div className={styles.pageShell}>
        <div className={styles.backdrop} />

        <header className={styles.hero}>
          <div className={styles.heroText}>
            <p className={styles.eyebrow}>Chapter 10 capstone · retrieval systems and agents</p>
            <h1>Build a retrieval lab learners can inspect, question, and trust.</h1>
            <p className={styles.lead}>
              The core contract is generic. NPS is the worked example. The UI keeps the evidence visible enough that a
              learner can audit the answer instead of admiring it from a distance.
            </p>
            <div className={styles.heroActions}>
              <button className={styles.primaryButton} onClick={() => void runMode("answer")} disabled={busy}>
                {busy ? "Thinking..." : "Run grounded answer"}
              </button>
              <button className={styles.secondaryButton} onClick={() => void runMode("agent")} disabled={busy}>
                Inspect agent trace
              </button>
              <Link href="/" className={styles.inlineLink}>
                Back to trading dashboard
              </Link>
            </div>
          </div>

          <aside className={styles.heroCard}>
            <span className={styles.heroCardLabel}>Runtime</span>
            <strong>{status}</strong>
            <p>
              Query: <span>{deferredQuery}</span>
            </p>
            <p>Filter contract: metadata first, vectors second, answers last.</p>
          </aside>
        </header>

        <section className={styles.controlDeck}>
          <label className={styles.queryCard}>
            <span>Question</span>
            <textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className={styles.queryInput}
              rows={3}
            />
          </label>

          <div className={styles.filterCard}>
            <span>Filter chips</span>
            <div className={styles.filterRow}>
              {FILTERS.map((filter) => (
                <button
                  key={filter.key}
                  onClick={() => setFilterKey(filter.key)}
                  className={filter.key === filterKey ? styles.filterChipActive : styles.filterChip}
                >
                  {filter.label}
                </button>
              ))}
            </div>
            <div className={styles.actionRow}>
              <button className={styles.actionButton} onClick={() => void runMode("search")} disabled={busy}>
                Search
              </button>
              <button className={styles.actionButton} onClick={() => void runMode("answer")} disabled={busy}>
                Answer
              </button>
              <button className={styles.actionButton} onClick={() => void runMode("agent")} disabled={busy}>
                Agent
              </button>
            </div>
          </div>
        </section>

        {error ? <p className={styles.warningBanner}>{error}</p> : null}
        {answer.warning ? <p className={styles.warningBanner}>{answer.warning}</p> : null}

        <main className={styles.workbench}>
          <section className={styles.primaryColumn}>
            <article className={styles.answerPanel}>
              <div className={styles.panelHeader}>
                <span className={styles.panelKicker}>Why this answer</span>
                <span className={styles.panelMeta}>{selectedFilter.label}</span>
              </div>
              <p className={styles.answerText}>{agent?.answer_response?.answer || answer.answer}</p>
              <div className={styles.citationList}>
                {(agent?.answer_response?.citations || answer.citations).map((citation) => (
                  <button
                    key={citation.source_id}
                    className={styles.citationCard}
                    onClick={() => void loadSource(citation.source_id)}
                  >
                    <strong>{citation.title}</strong>
                    <span>{citation.quote}</span>
                  </button>
                ))}
              </div>
            </article>

            <article className={styles.resultsPanel}>
              <div className={styles.panelHeader}>
                <span className={styles.panelKicker}>Retrieval board</span>
                <span className={styles.panelMeta}>{results.length} candidates</span>
              </div>
              <div className={styles.resultGrid}>
                {results.map((result) => (
                  <button
                    key={result.chunk_id}
                    className={styles.resultCard}
                    onClick={() => void loadSource(result.source_id)}
                  >
                    <div className={styles.resultCardHeader}>
                      <strong>{result.title}</strong>
                      <span>{result.score.toFixed(2)}</span>
                    </div>
                    <p>{result.snippet}</p>
                    <div className={styles.badgeRow}>
                      {result.tags.map((tag) => (
                        <span key={`${result.chunk_id}-${tag.tag_key}`} className={styles.badge}>
                          {tag.tag_key}: {tag.value}
                        </span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            </article>
          </section>

          <aside className={styles.sideColumn}>
            <article className={styles.sideCard}>
              <div className={styles.panelHeader}>
                <span className={styles.panelKicker}>Tag inspector</span>
                <span className={styles.panelMeta}>{activeTags.length} tags</span>
              </div>
              <div className={styles.tagStack}>
                {activeTags.map((tag) => (
                  <div key={`${tag.tag_key}-${tag.value}`} className={styles.tagCard}>
                    <strong>
                      {tag.tag_key} · {tag.value}
                    </strong>
                    <p>{tag.evidence}</p>
                    <span>{tag.method} · {(tag.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </article>

            <article className={styles.sideCard}>
              <div className={styles.panelHeader}>
                <span className={styles.panelKicker}>Source drawer</span>
                <span className={styles.panelMeta}>{selectedSource.source_id}</span>
              </div>
              <h2>{selectedSource.title}</h2>
              <p className={styles.sourceSummary}>{selectedSource.summary}</p>
              <p className={styles.sourceBody}>{selectedSource.body}</p>
              <div className={styles.metadataList}>
                {Object.entries(selectedSource.metadata || {}).map(([key, value]) => (
                  <span key={key}>
                    {key}: {value}
                  </span>
                ))}
              </div>
              <a href={selectedSource.source_url} target="_blank" rel="noreferrer" className={styles.inlineLink}>
                Open source
              </a>
            </article>

            <article className={styles.sideCard}>
              <div className={styles.panelHeader}>
                <span className={styles.panelKicker}>Trace rail</span>
                <span className={styles.panelMeta}>{activeTrace.length} steps</span>
              </div>
              <ol className={styles.traceList}>
                {activeTrace.map((step, index) => (
                  <li key={`${index}-${JSON.stringify(step)}`} className={styles.traceItem}>
                    {"tool" in step ? (
                      <>
                        <strong>{(step as AgentStep).tool}</strong>
                        <p>{(step as AgentStep).output_summary}</p>
                      </>
                    ) : (
                      <>
                        <strong>{String(step.step || `step-${index + 1}`)}</strong>
                        <p>{JSON.stringify(step)}</p>
                      </>
                    )}
                  </li>
                ))}
              </ol>
            </article>
          </aside>
        </main>
      </div>
    </>
  );
};

export default Chapter10Lab;
