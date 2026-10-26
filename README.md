# Enterprise-Grade Multi-Agent Repository & CI/CD Debugger

## Product Vision
An AI-powered engineering assistant that integrates with GitHub, reviews pull requests, investigates CI/CD failures, understands repository context, and eventually proposes verifiable fixes.

## Phase 1: Project Foundation and Core Backend Infrastructure (Implemented)
Clean modular FastAPI backend, versioned API at `/api/v1`, health/readiness, centralized errors, CORS/config/logging, GitHub integration boundary prepared, domain schemas for Repository/PullRequest/Investigation/InvestigationStatus, SQLAlchemy/Alembic setup, Render-ready Dockerfile on `$PORT`, no local Postgres, no tests.

## Phase 2: GitHub Integration and Pull Request Ingestion (Implemented)
- **Webhook endpoint**: `POST /api/v1/webhooks/github` reads raw body, verifies `X-Hub-Signature-256` with HMAC-SHA256 and constant-time comparison, validates headers/payload, supports `pull_request.opened/synchronize/reopened/closed` plus safe handling of other events, acknowledges quickly without heavy sync work.
- **Idempotency**: Durable `webhook_deliveries` table with unique `delivery_id`, statuses `received → queued → processing → completed` plus `failed/retryable`, concurrent duplicate handling via DB constraints.
- **GitHub API client**: `integrations/github/client.py` with auth boundary, supports repo/PR/files/commits operations, pagination support, normalized errors, short-lived installation token design via `auth.py`. Returns configuration errors if credentials missing; no fake responses.
- **Models & migration**: `repositories`, `pull_requests`, `webhook_deliveries`, `investigations` with appropriate FKs/unique/indexes. Migration `20261024_0001_github_pr_ingestion` created but **not auto-applied**; apply deliberately with `alembic upgrade head`.
- **Ingestion workflow**: Duplicate check → persist delivery → queue (DB-backed) → idempotent upsert of repo/PR → create investigation for actionable events (bind to new head SHA on synchronize), ignore new investigations on closed, update PR state.
- **Background processing**: Database-backed delivery state, prevents concurrent processing via status transitions, bounded retries configurable.
- **API endpoints**: `GET /api/v1/repositories`, `GET /api/v1/repositories/{id}`, `GET /api/v1/repositories/{id}/pull-requests`, `GET /api/v1/pull-requests/{id}`, `GET /api/v1/investigations/{id}` (paginated where applicable). Private data endpoints not exposed without auth in this phase.

## Deferred (Phase 3+)
LLM/multi-agent orchestration, AI reviews, embeddings/RAG, CI log analysis, patch generation, autonomous fixes, frontend changes, tests.

## Backend Architecture
```
src/app/
├── api/v1/           # Versioned routes (health, ready, webhooks, repos, PRs, investigations)
├── core/             # Config, logging, errors
├── db/               # Engine, session, base
├── integrations/github/ # Webhook verify, auth, API client
├── main.py
├── models/           # Shared base + models
├── modules/
│   ├── investigations/
│   ├── pull_requests/
│   ├── repositories/
│   └── webhooks/
└── workers/          # DB-backed processor (separate worker process if needed)
```

## Environment Variables
Required: `DATABASE_URL` (Render PostgreSQL, no fallback). Optional: `DATABASE_SSL`, pool settings, `CORS_*`, `PORT`, `GITHUB_APP_ID`, `GITHUB_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`, `GITHUB_APP_INSTALLATION_ID`, `GITHUB_API_BASE_URL`, `WORKER_MAX_RETRIES`, `WORKER_RETRY_DELAY_SECONDS`. See `.env.example`.

## GitHub App Setup (Manual)
1. Create a GitHub App in your org/account.
2. Set permissions: Repository permissions - Pull requests (Read), Contents (Read), Metadata (Read). Webhook events: `pull_request` (and optionally Actions later).
3. Generate a private key and download it.
4. Install the app on target repositories.
5. Configure webhook URL: `https://<your-render-app>/api/v1/webhooks/github` with the same secret as `GITHUB_WEBHOOK_SECRET`.
6. Store `GITHUB_APP_ID`, private key, `GITHUB_WEBHOOK_SECRET`, `GITHUB_APP_INSTALLATION_ID` in Render environment variables.

## Migrations
Apply deliberately: `alembic upgrade head` using `DATABASE_URL`. Migration `20261024_0001_github_pr_ingestion` adds the Phase 2 tables. Not auto-applied on startup.

## Worker (if needed)
Webhook handler enqueues via DB state; run `process_pending_deliveries()` in a separate worker process on Render if durable processing is required. Configure retries via env vars.

## Notes
- No tests created/run.
- No local Postgres.
- Signature verification uses constant-time comparison.
- No secrets logged.

## Phase 3: Repository Intelligence and Evidence-Based PR Analysis (Implemented)
- **Context retrieval**: Diff normalization, PR/file retrieval via GitHub API client with bounded sizes; retrieves base/head SHAs and changed files/hunks when available.
- **LLM boundary**: Configurable provider abstraction (env-driven), separate from domain, timeouts/retries designed, fails clearly if unconfigured, no secrets logged.
- **Single-orchestrator pipeline**: Load investigation/PR/repo → retrieve diff/context → normalize → prepare bounded analysis request → validate findings against schemas → persist AnalysisRun/AnalysisFinding → update investigation state (completed/failed). Evidence validation enforced via schema.
- **Findings schema**: Categories/severity/confidence/status, file path/line range, evidence/explanation/suggestion, finding_id, verification status; untrusted model output normalized/validated.
- **Safety**: No arbitrary code execution, bounded context, separates system instructions from repo content conceptually, redaction guidance, path/file-size/time limits.
- **API endpoints**: `POST /api/v1/investigations/{id}/analyze` (enqueue/initiate), `GET /api/v1/investigations/{id}/findings`, `GET /api/v1/pull-requests/{id}/analysis`. Pagination-ready; protected by auth when available.
- **Persistence**: New models `AnalysisRun`, `AnalysisFinding` with migration `20261024_0002_analysis_phase3`. No large blobs stored by default; metrics recorded.
- **Deferred**: Multi-agent orchestration, patch generation, auto-comments, embeddings/RAG without justification, CI log analysis.

## Migrations (Updated)
- `20261024_0001_github_pr_ingestion` (Phase 2)
- `20261024_0002_analysis_phase3` (Phase 3)
Apply deliberately: `alembic upgrade head`. No auto-apply on startup.

## Phase 4: Multi-Agent Orchestration and CI Failure Investigation (Implemented)
- **Agent system**: Logical agents with explicit contracts (Coordinator, Diff Analysis, Repository Context, Code Review, CI Investigator, Finding Verification), bounded tool permissions, schemas, limits.
- **Orchestration**: Plain Python orchestration (state machine) with states queued→planning→executing→verifying→synthesizing→completed/failed/partially_completed/cancelled/waiting_for_retry. Sequential/conditional flow, bounded retries/timeouts, persists WorkflowRun/AgentExecution.
- **PR analysis**: Diff analysis, context retrieval, code review, verification, synthesis; findings deduplicated/verified, hypotheses vs confirmed separated.
- **CI investigation**: Read-only GitHub Actions metadata/log retrieval boundary, correlation with changed files/commit, classification of failure types, evidence-backed hypotheses; no job reruns/modifications/execution.
- **Safety**: Tool registry concept, untrusted inputs treated as data, no unrestricted shell/SQL/HTTP, execution limits/cost controls, partial failures represented honestly.
- **API**: CI endpoints and workflow status endpoints added; long-running work via worker infrastructure.
- **Persistence**: New models `WorkflowRun`, `AgentExecution` with migration `20261024_0003_multiagent_phase4`. No auto-migrations on startup.

## Migrations (Updated)
- `20261024_0001_github_pr_ingestion` (Phase 2)
- `20261024_0002_analysis_phase3` (Phase 3)
- `20261024_0003_multiagent_phase4` (Phase 4)
Apply deliberately: `alembic upgrade head`.

## Phase 5: Safe Patch Generation, Sandboxed Verification, and Human Approval (Implemented)
- **Patch workflow**: Eligibility checks for accepted findings with evidence, tied to target commit SHA, minimal diffs, structured proposal schema.
- **Generation**: Patch generation agent boundary with strict validation, never invents files/context, no unrelated changes/dependencies/config/secrets without justification.
- **Safe application**: Diff validation (syntax/paths/preimage/size/binary/symlink/path traversal), applied only in isolated disposable workspace, never overwrites working tree/branch.
- **Sandbox**: Abstraction with resource limits/network disabled/non-root/cleanup/logs; reports missing infrastructure honestly (no host execution without secure isolation). No untrusted code execution in API/worker.
- **Verification**: Only allowlisted non-test checks (syntax/parse/compile/static/type/lint/narrow build) - **no tests executed**. Outcomes not_run/passed/failed/blocked/timed_out with sanitized logs.
- **Lifecycle & persistence**: States eligible→generating→proposed→validating→awaiting_approval plus rejected/invalid/verification_failed/verification_blocked/approved/cancelled/expired. Separate patch/verification/human approval status. Audit trail. Migration `20261024_0004_patches_phase5`. No auto-migrate.
- **Human approval**: Required before any remote changes; approval/reject/cancel endpoints with auth/authorization checks; no auto-push/branch/PR/comment.
- **API**: `POST /api/v1/investigations/{id}/findings/{fid}/patches`, `GET /api/v1/patches/{id}`, `GET /api/v1/patches/{id}/diff`, `GET /api/v1/patches/{id}/verification`, `POST /api/v1/patches/{id}/approve`, `POST /api/v1/patches/{id}/reject`, `POST /api/v1/patches/{id}/cancel`.
- **Deferred**: Auto-commits/pushes/PRs/reviews, test execution, full sandbox deployment.

## Migrations (Updated)
- `20261024_0001_github_pr_ingestion` (Phase 2)
- `20261024_0002_analysis_phase3` (Phase 3)
- `20261024_0003_multiagent_phase4` (Phase 4)
- `20261024_0004_patches_phase5` (Phase 5)
Apply deliberately: `alembic upgrade head`.

## Phase 6: Evaluation, Production Hardening, and Deployment Readiness (Implemented)
- **Audit**: System audit of phases 1-5, gap assessment, capabilities classified (implemented/partial/missing/unverified).
- **Evaluation framework**: Versioned dataset schema, metric definitions (precision/recall/F1/localization/severity/duplicate/unsupported/evidence), CI diagnosis metrics, patch metrics, regression comparison; reports only when data available.
- **Observability**: Structured logging with redaction, metrics collector, traceability via investigation/workflow IDs.
- **Reliability**: Webhook idempotency/duplicates/concurrency, job recovery/retries/idempotency/dead-letter concepts, DB pool/transactions/index guidance, provider timeouts/retries/rate limits.
- **Security hardening**: Signature validation, least privilege, repo-level authz guidance, prompt injection/tool permission enforcement, sandbox isolation audit, data handling documented.
- **Performance/capacity**: Bottleneck analysis, capacity model with assumptions, safe load-test guidance (no tests/load tests executed).
- **Cost controls**: Configurable budgets per investigation, usage tracking where available.
- **Deployment readiness**: Render API/worker/Postgres instructions, env vars, migrations manual, health/readiness, no auto-migrate/startup DB creation, no local Postgres.
- **Runbooks**: Webhook failures, stuck investigations, DB/connectivity, LLM outages, rate limits, sandbox failures, migrations, credential rotation, data leakage response.
- **No tests**: No test artifacts created/run.

## Migrations (Current)
- `20261024_0001_github_pr_ingestion` (Phase 2)
- `20261024_0002_analysis_phase3` (Phase 3)
- `20261024_0003_multiagent_phase4` (Phase 4)
- `20261024_0004_patches_phase5` (Phase 5)
Apply deliberately: `alembic upgrade head`. No auto-apply on startup.
