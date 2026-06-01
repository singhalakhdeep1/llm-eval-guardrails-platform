"use client";

import { FormEvent, useEffect, useState, useTransition } from "react";

type PromptVersionRecord = {
    id: string;
    name: string;
    version: string;
    owner: string;
    model: string;
    risk_level: string;
    created_at: string;
};

type Scorecard = {
    prompt_id: string;
    prompt_name: string;
    latest_status: string;
    latest_pass_rate: number;
    safety_score: number;
    groundedness_score: number;
    release_ready: boolean;
};

type EvaluationMetric = {
    name: string;
    score: number;
    passed: boolean;
    details: string;
};

type EvaluationCaseResult = {
    input: string;
    output: string;
    metrics: EvaluationMetric[];
    passed: boolean;
};

type EvaluationRunRecord = {
    id: string;
    prompt_id: string;
    dataset_name: string;
    created_at: string;
    pass_rate: number;
    status: string;
    cases: EvaluationCaseResult[];
};

type AnalyticsSnapshot = {
    prompt_count: number;
    run_count: number;
    blocked_runs: number;
    release_ready_prompts: number;
    top_failure_mode: string;
};

type DatasetRecord = {
    name: string;
    case_count: number;
    fields: string[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8100";

export function EvalDashboard() {
    const [prompts, setPrompts] = useState<PromptVersionRecord[]>([]);
    const [scorecards, setScorecards] = useState<Scorecard[]>([]);
    const [runs, setRuns] = useState<EvaluationRunRecord[]>([]);
    const [analytics, setAnalytics] = useState<AnalyticsSnapshot | null>(null);
    const [datasets, setDatasets] = useState<DatasetRecord[]>([]);
    const [message, setMessage] = useState("Seed prompts are available. Run an evaluation to populate scorecards.");
    const [selectedPrompt, setSelectedPrompt] = useState("");
    const [datasetName, setDatasetName] = useState("baseline-policy-suite");
    const [evalInput, setEvalInput] = useState("Summarize the customer refund policy.");
    const [keywords, setKeywords] = useState("refund, customer, policy");
    const [isPending, startTransition] = useTransition();

    useEffect(() => {
        void refresh();
    }, []);

    const refresh = async () => {
        try {
            const [promptsResponse, scorecardsResponse, runsResponse, analyticsResponse, datasetsResponse] = await Promise.all([
                fetch(`${API_BASE_URL}/api/v1/prompts`),
                fetch(`${API_BASE_URL}/api/v1/scorecards`),
                fetch(`${API_BASE_URL}/api/v1/runs`),
                fetch(`${API_BASE_URL}/api/v1/analytics`),
                fetch(`${API_BASE_URL}/api/v1/datasets`),
            ]);

            if (promptsResponse.ok) {
                const payload = (await promptsResponse.json()) as { prompts: PromptVersionRecord[] };
                setPrompts(payload.prompts);
                if (!selectedPrompt && payload.prompts[0]) {
                    setSelectedPrompt(payload.prompts[0].id);
                }
            }

            if (scorecardsResponse.ok) {
                const payload = (await scorecardsResponse.json()) as { scorecards: Scorecard[] };
                setScorecards(payload.scorecards);
            }

            if (runsResponse.ok) {
                const payload = (await runsResponse.json()) as { runs: EvaluationRunRecord[] };
                setRuns(payload.runs);
            }

            if (analyticsResponse.ok) {
                const payload = (await analyticsResponse.json()) as AnalyticsSnapshot;
                setAnalytics(payload);
            }

            if (datasetsResponse.ok) {
                const payload = (await datasetsResponse.json()) as { datasets: DatasetRecord[] };
                setDatasets(payload.datasets);
            }
        } catch {
            setAnalytics(null);
        }
    };

    const handleRunFromDataset = () => {
        startTransition(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/evaluations/run-from-dataset`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        prompt_id: selectedPrompt,
                        dataset_name: datasetName,
                        max_cases: 20,
                    }),
                });

                if (!response.ok) {
                    throw new Error(`Dataset run failed with status ${response.status}`);
                }

                setMessage("Dataset-driven evaluation run completed.");
                await refresh();
            } catch (error) {
                const details = error instanceof Error ? error.message : "Unknown error";
                setMessage(`Dataset run failed: ${details}`);
            }
        });
    };

    const handleRun = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        startTransition(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/evaluations/run`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        prompt_id: selectedPrompt,
                        dataset_name: datasetName,
                        eval_cases: [
                            {
                                input: evalInput,
                                expected_keywords: keywords
                                    .split(",")
                                    .map((value) => value.trim())
                                    .filter(Boolean),
                            },
                        ],
                    }),
                });

                if (!response.ok) {
                    throw new Error(`Run failed with status ${response.status}`);
                }

                setMessage("Evaluation run completed. Scorecards and release gates refreshed.");
                await refresh();
            } catch (error) {
                const details = error instanceof Error ? error.message : "Unknown error";
                setMessage(`Evaluation run failed: ${details}`);
            }
        });
    };

    return (
        <main className="page">
            <section className="hero">
                <span className="eyebrow">LLM Quality Platform</span>
                <h1 className="headline">Prompt releases need evidence, not intuition.</h1>
                <p className="subhead">
                    This project models the core control plane for prompt regression testing, guardrail checks,
                    scorecards, and release readiness across production AI workflows.
                </p>
            </section>

            <section className="stats">
                <article className="card">
                    <p className="label">Prompt registry</p>
                    <p className="metric">{analytics?.prompt_count ?? prompts.length}</p>
                </article>
                <article className="card">
                    <p className="label">Evaluation runs</p>
                    <p className="metric">{analytics?.run_count ?? runs.length}</p>
                </article>
                <article className="card">
                    <p className="label">Blocked runs</p>
                    <p className="metric">{analytics?.blocked_runs ?? 0}</p>
                </article>
                <article className="card">
                    <p className="label">Release ready</p>
                    <p className="metric">{analytics?.release_ready_prompts ?? 0}</p>
                </article>
            </section>

            <section className="grid" aria-label="evaluation console">
                <section className="card">
                    <p className="label">Run evaluation</p>
                    <h2>Execute one dataset slice</h2>
                    <form className="form" onSubmit={handleRun}>
                        <label>
                            Prompt
                            <select value={selectedPrompt} onChange={(event) => setSelectedPrompt(event.target.value)}>
                                {prompts.map((prompt) => (
                                    <option key={prompt.id} value={prompt.id}>
                                        {prompt.name} v{prompt.version}
                                    </option>
                                ))}
                            </select>
                        </label>
                        <label>
                            Dataset name
                            <input value={datasetName} onChange={(event) => setDatasetName(event.target.value)} />
                        </label>
                        <label>
                            Evaluation input
                            <textarea value={evalInput} rows={4} onChange={(event) => setEvalInput(event.target.value)} />
                        </label>
                        <label>
                            Expected keywords
                            <input value={keywords} onChange={(event) => setKeywords(event.target.value)} />
                        </label>
                        <div className="button-row">
                            <button type="submit" disabled={isPending || !selectedPrompt}>
                                {isPending ? "Running..." : "Run evaluation"}
                            </button>
                            <button
                                type="button"
                                className="secondary"
                                disabled={isPending || !selectedPrompt || !datasetName.trim()}
                                onClick={handleRunFromDataset}
                            >
                                Run from dataset
                            </button>
                            <button type="button" className="secondary" onClick={() => void refresh()}>
                                Refresh data
                            </button>
                        </div>
                    </form>
                    {datasets.length > 0 ? (
                        <p className="label">
                            Available datasets: {datasets.map((dataset) => `${dataset.name} (${dataset.case_count})`).join(", ")}
                        </p>
                    ) : (
                        <p className="label">No datasets found in evals/*.json yet.</p>
                    )}
                    <p className="status">{message}</p>
                </section>

                <section className="card">
                    <p className="label">Release scorecards</p>
                    <h2>Latest prompt readiness</h2>
                    <div className="list">
                        {scorecards.map((scorecard) => (
                            <article className="item" key={scorecard.prompt_id}>
                                <div className="item-head">
                                    <strong>{scorecard.prompt_name}</strong>
                                    <span className={`pill ${scorecard.release_ready ? "" : "blocked"}`}>
                                        {scorecard.release_ready ? "Ready" : scorecard.latest_status}
                                    </span>
                                </div>
                                <p className="label">Pass rate {scorecard.latest_pass_rate.toFixed(2)}</p>
                                <p className="label">
                                    Safety {scorecard.safety_score.toFixed(2)} · Groundedness {scorecard.groundedness_score.toFixed(2)}
                                </p>
                            </article>
                        ))}
                    </div>
                </section>

                <section className="card">
                    <p className="label">Prompt registry</p>
                    <h2>Tracked prompt versions</h2>
                    <div className="list">
                        {prompts.map((prompt) => (
                            <article className="item" key={prompt.id}>
                                <div className="item-head">
                                    <strong>{prompt.name}</strong>
                                    <span className="pill">{prompt.risk_level}</span>
                                </div>
                                <p className="label">v{prompt.version} · {prompt.model} · {prompt.owner}</p>
                            </article>
                        ))}
                    </div>
                </section>

                <section className="card">
                    <p className="label">Run history</p>
                    <h2>Latest evaluation outcomes</h2>
                    <div className="list">
                        {runs.map((run) => (
                            <article className="item" key={run.id}>
                                <div className="item-head">
                                    <strong>{run.dataset_name}</strong>
                                    <span className={`pill ${run.status === "passed" ? "" : "blocked"}`}>{run.status}</span>
                                </div>
                                <p className="label">Pass rate {run.pass_rate.toFixed(2)} · {new Date(run.created_at).toLocaleString()}</p>
                                {run.cases[0] ? <p>{run.cases[0].output}</p> : null}
                            </article>
                        ))}
                    </div>
                </section>
            </section>
        </main>
    );
}
