"""The sole model-call boundary. Phase 0's default redactor refuses live traffic."""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, ROUND_CEILING
from typing import Protocol

from src.config import Settings, settings
from src.gateway.ledger import Ledger, UnresolvedReservation, utc_now
from src.gateway.prices import ROUTES, Price, get_price

WORKLOADS = {"setup", "extraction", "evidence", "critique", "evaluation"}
ESCALATIONS = {"final_evidence_pack", "completeness_critique", "quality_review"}


class GatewayError(RuntimeError):
    pass


class NotSent(GatewayError):
    """Transport can prove no inference request was dispatched. Never use for timeouts."""


@dataclass(frozen=True, repr=False)
class RedactedPrompt:
    text: str
    live_ready: bool = False


class Redactor(Protocol):
    def redact(self, prompt: str) -> RedactedPrompt: ...


class Phase0Redactor:
    def redact(self, prompt):
        # Interface stub only. Offline code never persists the raw prompt;
        # live mode refuses this result until real redaction is implemented.
        return RedactedPrompt(prompt, live_ready=False)


class LocalEmbedder:
    """Explicit, public-corpus-only CPU embeddings; no provider or download fallback.

    LLM_MODE continues to govern Azure text calls. This separate opt-in never
    enables Azure and the default dry-run entry point never constructs it.
    """

    def __init__(self, config=settings, *, redactor=None):
        import sqlite3
        from src.config import ROOT
        if not config.local_embedding_enabled:
            raise GatewayError("Local embeddings require LOCAL_EMBEDDING_ENABLED=true")
        self.pin = json.loads((ROOT / "src/gateway/local-model.json").read_text())
        self.identity = hashlib.sha256(json.dumps(self.pin, sort_keys=True).encode()).hexdigest()
        self.config = config
        self.redactor = redactor or Phase0Redactor()
        self.computed = self.hits = 0
        self._session = self._tokenizer = None
        self._verified = False
        config.state_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = config.state_dir / "local-embeddings.sqlite3"
        with sqlite3.connect(self.cache_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS embeddings(key TEXT PRIMARY KEY, vector TEXT)")
        self.ledger = Ledger(config.state_dir / "gateway.sqlite3", config.daily_limit, config.project_limit)

    def _assets(self):
        if self._verified:
            return
        for file in self.pin["files"]:
            path = self.config.local_model_dir / file["name"]
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != file["sha256"]:
                raise GatewayError("Missing or changed pinned local model asset; run acquisition")
        self._verified = True

    def _safe(self, text):
        try:
            result = self.redactor.redact(text)
            if not isinstance(result, RedactedPrompt) or not result.text.strip():
                raise ValueError
            return result.text
        except Exception:
            raise GatewayError("Local embedding redaction hook rejected input") from None

    def _tokens(self):
        from tokenizers import Tokenizer
        self._assets()
        if self._tokenizer is None:
            self._tokenizer = Tokenizer.from_file(str(self.config.local_model_dir / "tokenizer.json"))
            self._tokenizer.no_truncation()
            self._tokenizer.no_padding()
        return self._tokenizer

    def windows(self, text):
        text = self._safe(text)
        encoded = self._tokens().encode(text, add_special_tokens=False)
        # Preserve exact substrings and overlapping context. Never silently truncate.
        windows = []
        for start in range(0, len(encoded.ids), 192):
            stop = min(start + 224, len(encoded.ids))
            lo = 0 if start == 0 else encoded.offsets[start][0]
            hi = len(text) if stop == len(encoded.ids) else encoded.offsets[stop - 1][1]
            windows.append(text[lo:hi])
            if stop == len(encoded.ids):
                break
        return windows

    def embed(self, texts):
        import sqlite3
        safe = [self._safe(t) for t in texts]
        keys = [hashlib.sha256((self.identity + t).encode()).hexdigest() for t in safe]
        started = time.monotonic()
        computed = hits = tokens = 0
        found, missing = {}, {}
        with sqlite3.connect(self.cache_path) as db:
            for key, text in zip(keys, safe, strict=True):
                cached = db.execute("SELECT vector FROM embeddings WHERE key=?", (key,)).fetchone()
                if cached:
                    vector = json.loads(cached[0])
                    self._validate_vector(vector)
                    found[key] = vector
                    hits += 1
                else:
                    missing[key] = text
            pending = list(missing.items())
            for offset in range(0, len(pending), 16):
                batch = pending[offset:offset + 16]
                vectors, count = self._run([text for _, text in batch])
                tokens += count
                for (key, _), vector in zip(batch, vectors, strict=True):
                    self._validate_vector(vector)
                    found[key] = vector
                    db.execute("INSERT OR IGNORE INTO embeddings VALUES(?,?)", (key, json.dumps(vector)))
                    computed += 1
                db.commit()  # Interrupted later batches reuse all completed vectors.
        self.computed += computed
        self.hits += hits
        self.ledger.log({"timestamp": utc_now().isoformat(), "workload": "corpus_embedding",
                         "model": self.pin["model"], "model_version": self.pin["revision"],
                         "prompt_tokens": tokens, "completion_tokens": 0,
                         "latency_ms": round((time.monotonic() - started) * 1000, 3),
                         "estimated_aud": "0", "mode": "local", "cache_hit": not computed,
                         "cache_hits": hits, "embedded": computed, "escalation_reason": None})
        return [found[key] for key in keys]

    @staticmethod
    def _validate_vector(vector):
        import math
        if (len(vector) != 384 or any(not isinstance(x, (float, int)) or not math.isfinite(x) for x in vector)
                or not 0.99 < sum(x * x for x in vector) < 1.01):
            raise GatewayError("Invalid local embedding or cache corruption")

    def _run(self, texts):
        import numpy as np
        import onnxruntime as ort
        tokenizer = self._tokens()
        encoded = [tokenizer.encode(t) for t in texts]
        if any(len(e.ids) > 256 for e in encoded):
            raise GatewayError("Local embedding input exceeds the pinned token bound")
        if self._session is None:
            options = ort.SessionOptions()
            options.intra_op_num_threads = 2
            options.inter_op_num_threads = 1
            self._session = ort.InferenceSession(str(self.config.local_model_dir / "model.onnx"),
                                                 sess_options=options, providers=["CPUExecutionProvider"])
        width = max(len(e.ids) for e in encoded)
        ids = np.array([e.ids + [0] * (width - len(e.ids)) for e in encoded], dtype=np.int64)
        mask = np.array([[1] * len(e.ids) + [0] * (width - len(e.ids)) for e in encoded], dtype=np.int64)
        outputs = self._session.run(None, {"input_ids": ids, "attention_mask": mask,
                                           "token_type_ids": np.zeros_like(ids)})[0]
        # Model card: attention-masked mean pooling, then L2 normalisation.
        mean = (outputs * mask[:, :, None]).sum(axis=1) / mask.sum(axis=1)[:, None]
        vectors = mean / np.linalg.norm(mean, axis=1, keepdims=True)
        return vectors.tolist(), sum(len(e.ids) for e in encoded)


@dataclass(frozen=True, repr=False)
class Completion:
    text: str
    prompt_tokens: int
    completion_tokens: int  # Includes billed reasoning tokens, not just visible text.
    cached_input_tokens: int = 0
    reasoning_tokens: int = 0

    def validate(self):
        counts = (self.prompt_tokens, self.completion_tokens,
                  self.cached_input_tokens, self.reasoning_tokens)
        if (not isinstance(self.text, str) or
                any(type(n) is not int or n < 0 for n in counts) or
                self.cached_input_tokens > self.prompt_tokens or
                self.reasoning_tokens > self.completion_tokens):
            raise GatewayError("Provider returned invalid or incomplete token usage")


class LLMClient:
    def __init__(self, config: Settings = settings, *, redactor: Redactor | None = None,
                 transport=None):
        self.config = config
        if config.mode not in {"dry_run", "cached", "live"}:
            raise GatewayError("Unsupported execution mode")
        if config.mode == "live" and not config.allow_live:
            raise GatewayError("Live mode requires a separate explicit enable flag")
        self.redactor = redactor or Phase0Redactor()
        self._transport = transport or self._azure_call
        self.ledger = Ledger(config.state_dir / "gateway.sqlite3", config.daily_limit,
                             config.project_limit)

    def complete(self, prompt: str, *, workload="setup", tier="cheap", model=None,
                 max_output_tokens=None, escalation_reason=None) -> Completion:
        if workload not in WORKLOADS or tier not in {"cheap", "strong"}:
            raise GatewayError("Unsupported workload or text-model tier")
        price = get_price(model or ROUTES[tier])
        if price.model != ROUTES[tier]:
            raise GatewayError("Model must match the explicitly selected tier")
        if tier == "strong" and escalation_reason not in ESCALATIONS:
            raise GatewayError("Strong routing requires an approved escalation reason code")
        if tier == "cheap" and escalation_reason is not None:
            raise GatewayError("Escalation reason is only valid for the strong tier")
        if not isinstance(prompt, str):
            raise GatewayError("Only plain text prompts are supported")
        try:
            safe = self.redactor.redact(prompt)
            if not isinstance(safe, RedactedPrompt) or not isinstance(safe.text, str):
                raise ValueError
        except Exception:
            raise GatewayError("Redaction hook failed; no call made") from None
        output_cap = self.config.max_output_tokens if max_output_tokens is None else max_output_tokens
        if type(output_cap) is not int or not 0 < output_cap <= self.config.max_output_tokens:
            raise GatewayError("Output token bound is invalid")
        # Byte-level upper bound for one plain user message plus conservative framing.
        # No tools, image inputs, extra messages or arbitrary provider parameters accepted.
        if len(safe.text.encode("utf-8")) + 64 > self.config.max_input_tokens:
            raise GatewayError("Prompt exceeds conservative input token bound")
        self.ledger.ensure_clear()
        scope = {k: self.config.azure.get(k, "") for k in
                 ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_VERSION",
                  "AZURE_OPENAI_DEPLOYMENT_" + tier.upper())}
        params = {"max_completion_tokens": output_cap, "reasoning_effort": "minimal",
                  "input_bound": self.config.max_input_tokens, "scope": scope}
        key = hashlib.sha256(json.dumps([price.identity, safe.text, params],
                                       sort_keys=True, ensure_ascii=True).encode()).hexdigest()
        started = time.monotonic()

        def log(status, response=None, cost=0, hit=False, reservation=None):
            return {"timestamp": utc_now().isoformat(), "workload": workload,
                    "model": price.model, "model_version": price.version,
                    "prompt_tokens": response.prompt_tokens if response else 0,
                    "completion_tokens": response.completion_tokens if response else 0,
                    "reasoning_tokens": response.reasoning_tokens if response else 0,
                    "latency_ms": round((time.monotonic() - started) * 1000, 3),
                    "estimated_aud": None if cost is None else str(Decimal(cost) / 1_000_000),
                    "mode": self.config.mode, "cache_hit": hit,
                    "escalation_reason": escalation_reason, "status": status,
                    "reservation_id": reservation}

        if self.config.mode == "dry_run":
            self.ledger.log(log("dry_run"))
            return Completion("PHASE_0_DRY_RUN: no model or compliance assessment executed.", 0, 0)
        cached = self.ledger.cached(key)
        if cached is not None:
            result = Completion(**cached)
            result.validate()
            self.ledger.log(log("cache_hit", hit=True))
            return result
        if self.config.mode == "cached":
            raise GatewayError("Cache miss; cached mode never contacts a provider")
        if not safe.live_ready:
            raise GatewayError("Phase 0 redaction stub cannot authorise live traffic")
        # Reserve full input/output caps, including reasoning, at uncached prices.
        # Additional 25% reservation headroom is released on exact usage settlement.
        bound = price.cost_microaud(self.config.max_input_tokens, output_cap)
        maximum = int((Decimal(bound) * Decimal("1.25")).to_integral_value(rounding=ROUND_CEILING))
        for attempt in range(self.config.max_retries + 1):
            identifier = self.ledger.reserve(maximum)
            try:
                response = self._transport(price, safe.text, output_cap, tier)
                response.validate()
                if (response.prompt_tokens > self.config.max_input_tokens or
                        response.completion_tokens > output_cap):
                    raise GatewayError("Provider exceeded requested token bounds")
                actual = price.cost_microaud(response.prompt_tokens, response.completion_tokens,
                                              response.cached_input_tokens)
            except NotSent:
                self.ledger.fail(identifier, confirmed_not_sent=True,
                                 record=log("not_sent", reservation=identifier))
                if attempt < self.config.max_retries:
                    continue  # Fresh reservation, never an SDK-controlled hidden retry.
                raise GatewayError("Inference was not dispatched; reservation released") from None
            except Exception:
                self.ledger.fail(identifier, confirmed_not_sent=False,
                                 record=log("ambiguous", cost=None, reservation=identifier))
                raise UnresolvedReservation("Inference outcome or usage is ambiguous; spending halted") from None
            self.ledger.finish(identifier, actual, key, asdict(response),
                               log("success", response, actual, reservation=identifier))
            return response
        raise GatewayError("Retry limit reached")

    def _azure_call(self, price: Price, prompt: str, output_cap: int, tier: str) -> Completion:
        """Entra auth; management metadata verified before any inference is sent."""
        # Imports and Azure calls stay inside this module. Neither offline mode imports SDKs.
        try:
            import urllib.request
            from azure.identity import AzureCliCredential
            from openai import AzureOpenAI

            if (utc_now().date() - date.fromisoformat(price.retrieved_on)).days > 31:
                raise ValueError("Price refresh required")
            a = self.config.azure
            credential = AzureCliCredential(tenant_id=a["AZURE_TENANT_ID"])
            arm_token = credential.get_token("https://management.azure.com/.default").token
            resource = (f"https://management.azure.com/subscriptions/{a['AZURE_SUBSCRIPTION_ID']}"
                        f"/resourceGroups/{a['AZURE_RESOURCE_GROUP']}"
                        f"/providers/Microsoft.CognitiveServices/accounts/{a['AZURE_OPENAI_ACCOUNT']}")
            deployment_name = a["AZURE_OPENAI_DEPLOYMENT_" + tier.upper()]

            def metadata(url):
                request = urllib.request.Request(url + "?api-version=2025-06-01",
                                                 headers={"Authorization": "Bearer " + arm_token})
                with urllib.request.urlopen(request, timeout=15) as stream:
                    return json.load(stream)

            account = metadata(resource)
            deployment = metadata(resource + "/deployments/" + deployment_name)
            deployed = deployment["properties"]["model"]
            if (account["location"].lower() != price.region or a["AZURE_REGION"] != price.region or
                    account["properties"]["endpoint"].rstrip("/") != a["AZURE_OPENAI_ENDPOINT"].rstrip("/") or
                    deployed["name"] != price.model or deployed["version"] != price.version or
                    deployment["sku"]["name"] != price.sku):
                raise ValueError("Deployment does not match pinned price")
            # Local development uses existing Entra CLI auth, never API keys.
            # A managed identity credential can replace this on a future Azure host.
            token = credential.get_token("https://cognitiveservices.azure.com/.default").token
            client = AzureOpenAI(azure_endpoint=a["AZURE_OPENAI_ENDPOINT"],
                                 api_version=a["AZURE_OPENAI_API_VERSION"], azure_ad_token=token,
                                 max_retries=0, timeout=30)
        except Exception:
            raise NotSent("Azure pre-dispatch validation failed") from None
        # Once dispatch starts, every failure is conservatively ambiguous.
        with client:
            result = client.chat.completions.create(
                model=deployment_name, messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=output_cap, reasoning_effort="minimal",
            )
        usage = result.usage
        if usage is None:
            raise GatewayError("Missing provider usage")
        return Completion(result.choices[0].message.content or "", usage.prompt_tokens,
                          usage.completion_tokens,
                          getattr(usage.prompt_tokens_details, "cached_tokens", 0) or 0,
                          getattr(usage.completion_tokens_details, "reasoning_tokens", 0) or 0)
