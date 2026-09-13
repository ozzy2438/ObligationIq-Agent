# Reproduction guide

This guide rebuilds the public, offline evidence on a clean checkout. It does not reproduce paid Azure calls, private caches, raw PDFs or local service state. Python 3.11+ and Git are required; CI uses Python 3.12.

## 1. Install

```sh
git clone https://github.com/ozzy2438/ObligationIq-Agent.git
cd ObligationIq-Agent
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test,register,risk,mcp]'
cp .env.example .env
```

Leave `LLM_MODE=dry_run`, `LLM_ALLOW_LIVE=false` and cloud values empty for the reproducible path. The install downloads Python packages; the checks below make no model call.

## 2. Verify committed evidence

```sh
python scripts/check_boundaries.py
python scripts/build_population.py --check
python scripts/evaluate_controls.py --check
python scripts/evaluate_risk.py --check
python scripts/evaluate_agents.py --check
python scripts/evaluate.py --check
python scripts/generate_cost_model.py --check --from-results
pytest
python -m src
```

These are the same required CI checks. Expected control/risk headline metrics are 31 TP, 3 FP, 0 FN, 38 TN; recall 1.0, precision 0.9117647059 and FPR 0.0731707317. Phase 7 is a committed live-evaluation snapshot bound to `docs/phase-7-frozen-manifest.json`; the check verifies its scope and hashes rather than contacting Azure.

## 3. Rebuild local source stores (optional)

Read `data/SOURCES.md` and `docs/phase-1-corpus.md` first. Install corpus/register extras, then explicitly acquire checksum-pinned public sources and local model assets:

```sh
python -m pip install -e '.[corpus,register]'
python scripts/acquire_corpus.py
```

Set `LOCAL_EMBEDDING_ENABLED=true` only for the documented local public-corpus build. Raw PDFs, extracted text, vectors, Delta tables and Unity Catalog state remain under ignored paths. Retrieval is filtered by regime and snapshot date. Starting the digest-pinned Unity Catalog OSS service is optional and documented in `docs/local-unity-catalog.md`; it is not Databricks.

## 4. Rebuild generated local analyses (optional)

```sh
python scripts/build_population.py
python scripts/evaluate_controls.py
python scripts/evaluate_risk.py
python scripts/evaluate_agents.py
```

The synthetic population seed is 20260912; the challenge-set seed is 20260913. Ground truth is isolated from controls and agents and CI enforces the boundary. Local MLflow records the shipped deterministic risk policy; no learned classifier is trained because no defensible longitudinal target exists.

## 5. Live evaluation boundary

Do not run `scripts/evaluate.py --live` as an ordinary reproduction step. It needs owner-authorised spend, Azure CLI authentication, the exact account/deployments in `docs/azure-resource-inventory.md`, fresh upward-rounded price pins, a retained ledger and both live flags. Global Standard is not Australia-only processing. `--cache-replay` also requires the private response cache; the completed project replay added zero spend.

## Evidence map

| Question | Document |
|---|---|
| What exists and where does authority sit? | `docs/solution-architecture.md` |
| Which sources and review decisions were used? | `data/SOURCES.md`, `docs/review-summary.md` |
| How accurate were controls and agents? | `docs/phase-4-controls.md`, `docs/phase-7-evaluation.md` |
| What did it cost? | `docs/cost-model.md` |
| What remains unsafe or unmeasured? | `docs/limitations-and-unmeasured-claims.md` |
| Which security and failure controls exist? | `docs/security-control-matrix.md`, `docs/stride-threat-model.md`, `docs/non-functional-requirements.md` |
