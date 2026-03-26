#!/usr/bin/env python3
"""Enrich question bank deep dives from Obsidian vault and generate per-question concept diagrams."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import shutil
import textwrap
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "how",
    "if",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "use",
    "using",
    "vs",
    "what",
    "when",
    "where",
    "which",
    "why",
    "with",
    "you",
    "your",
}

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
HTTP_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")
OBSIDIAN_IMAGE_RE = re.compile(r"!\[\[([^\]]+)\]\]")
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

SECTION_KEYWORDS = {
    "microservices": ["microservice", "gateway", "circuit", "idempotency", "saga", "service"],
    "sharding": ["shard", "partition", "routing", "rebalance", "consistent", "hash"],
    "consistency": ["consistency", "cap", "replication", "causal", "eventual"],
    "redis": ["redis", "replica", "psync", "aof", "rdb", "backlog", "sentinel"],
    "kafka": ["kafka", "partition", "isr", "consumer", "offset", "tiered"],
    "communication": ["request", "response", "websocket", "sse", "polling", "sidecar", "protocol"],
    "spring-boot": ["spring", "boot", "dto", "mapstruct", "controlleradvice", "validation"],
    "system-design": ["design", "estimate", "scalability", "latency", "trade", "architecture"],
    "elasticsearch": ["elasticsearch", "opensearch", "query", "shard", "wildcard", "profile"],
    "caching": ["cache", "memcached", "redis", "stampede", "ttl", "eviction"],
    "infrastructure": ["kubernetes", "dns", "cdn", "terraform", "observability", "canary"],
    "java": ["java", "jvm", "gc", "heap", "concurrent", "future"],
    "behavioral": ["star", "situation", "task", "action", "result", "leadership"],
    "x-twitter": ["twitter", "latency", "postgres", "wal", "pagination", "locks"],
    "ai-and-vectors": ["vector", "embedding", "hnsw", "ivf", "rag", "quantization", "ann"],
}

SECTION_PATH_HINTS = {
    "microservices": ["microservices", "spring boot", "distributed concepts"],
    "sharding": ["sharding", "distributed concepts", "system design"],
    "consistency": ["consistency", "distributed concepts", "system design"],
    "redis": ["redis", "implement redis"],
    "kafka": ["kafka", "distributed concepts"],
    "communication": ["backend communications", "protocols", "tcp-ip"],
    "spring-boot": ["spring boot", "udemy/spring boot"],
    "system-design": ["system design", "problems"],
    "elasticsearch": ["elasticsearch", "vector search", "opensearch"],
    "caching": ["meghacache", "redis", "cache"],
    "infrastructure": ["linux", "system design", "kubernetes"],
    "java": ["spring boot", "java"],
    "behavioral": ["interview questions", "system design"],
    "x-twitter": ["twitter", "system design", "linux"],
    "ai-and-vectors": ["artificial intelligence", "vector search", "opensearch", "rag", "hnsw"],
}

NOISY_DOC_PATTERNS = [
    re.compile(r"technical[/\\\\]test\\.md$", re.I),
    re.compile(r"technical[/\\\\]post links\\.md$", re.I),
    re.compile(r"system calude prompt\\.md$", re.I),
    re.compile(r"updated test\\.md$", re.I),
    re.compile(r"important links\\.md$", re.I),
]

DIAGRAM_PATTERNS = [
    (re.compile(r"circuit breaker", re.I), ["Request enters dependency call", "Closed state counts recent failures", "Threshold reached -> Open fail-fast", "Half-open sends probe requests", "Recover to Closed or reopen"]),
    (re.compile(r"idempotency", re.I), ["Client sends request + idempotency key", "Server checks dedupe record", "If seen -> return stored result", "If new -> execute once and persist", "Safe retries without double side effects"]),
    (re.compile(r"rate limit|token bucket|leaky bucket|sliding window", re.I), ["Identify caller key (user/token/IP)", "Track request budget in window", "Allow when tokens remain", "Reject or delay on depletion", "Expose limit headers and monitor drop rate"]),
    (re.compile(r"shard|consistent hashing|rebalanc", re.I), ["Select high-cardinality shard key", "Route request to target shard", "Monitor hot partitions and skew", "Rebalance with minimal movement", "Handle cross-shard queries explicitly"]),
    (re.compile(r"cap theorem|eventual|causal|read-your-writes|consistency", re.I), ["Identify partition/failure scenario", "Choose CP vs AP behavior", "Define user-facing consistency guarantee", "Apply reconciliation/conflict strategy", "Measure stale reads and recovery lag"]),
    (re.compile(r"redis.*(replica|psync|fullresync|backlog)|rdb|aof|sentinel", re.I), ["Replica sends PSYNC to master", "Master replies FULLRESYNC or partial", "RDB snapshot transfers baseline state", "Buffered writes replay after load", "Backlog size controls partial resync success"]),
    (re.compile(r"kafka|isr|consumer group|partition|tiered storage", re.I), ["Producer writes with partition key", "Leader appends and replicates to ISR", "Committed offset becomes consumable", "Consumer group processes per partition", "Retention/tiered storage manages history"]),
    (re.compile(r"long polling|sse|websocket|request-response|push|sidecar", re.I), ["Pick communication directionality", "Define connection lifecycle", "Add timeout/retry/back-pressure", "Instrument latency + disconnect causes", "Select protocol per workload constraints"]),
    (re.compile(r"eureka|config server|gateway|spring cloud", re.I), ["Services register/discover instances", "Config server centralizes runtime config", "Gateway enforces routing/security", "Circuit breaker isolates failing deps", "Tracing/metrics close operational loop"]),
    (re.compile(r"dto|mapstruct|modelmapper|validation|exception", re.I), ["Separate API contract from entity model", "Map request/response DTO boundaries", "Validate input close to controller edge", "Normalize errors in global handler", "Version and test API compatibility"]),
    (re.compile(r"music streaming|spotify|subscribe|save|amazon", re.I), ["Estimate user and traffic profile", "Separate metadata from large media blobs", "Design async workflows for long tasks", "Handle retries/idempotency in payments", "Track business and reliability metrics"]),
    (re.compile(r"wildcard|profile|query phase|fetch phase|lucene|slow log", re.I), ["Validate rewrite to inspect actual Lucene query", "Measure phase timings: query vs fetch", "Profile shard-level hotspots", "Fix mapping/query pattern bottlenecks", "Re-test latency and shard skew"]),
    (re.compile(r"cache|memcached|stampede|cache-aside", re.I), ["Define cache ownership and invalidation", "Handle miss path to authoritative store", "Prevent stampede with coalescing/locks", "Plan eviction + freshness policy", "Observe hit ratio and tail latency"]),
    (re.compile(r"dns|cdn|kubernetes|iac|canary|blue-green|observability", re.I), ["Route user traffic through edge/control plane", "Deploy workload with health gates", "Progressively release with canary checks", "Roll back fast on error budget impact", "Use logs/metrics/traces for diagnosis"]),
    (re.compile(r"outofmemory|gc|concurrenthashmap|completablefuture|jvm", re.I), ["Identify memory/concurrency bottleneck", "Choose JVM tuning or code-level fix", "Validate thread pool and async flow", "Measure GC pauses and allocation rate", "Document safe defaults and guardrails"]),
    (re.compile(r"vector|ann|hnsw|ivf|rag|quant|turboquant|embedding", re.I), ["Embed query/doc into vector space", "Retrieve candidates via ANN index", "Apply metadata filters and reranking", "Evaluate faithfulness + task success", "Tune recall/latency/memory trade-offs"]),
    (re.compile(r"behavioral|time you|tell me about", re.I), ["Situation and production context", "Task and ownership scope", "Action with technical depth", "Result with measurable impact", "Follow-up guardrails and learnings"]),
]

SECTION_DIAGRAM_FALLBACK = {
    "microservices": ["Bound service responsibilities", "Use gateway/discovery to route safely", "Apply resilience patterns per dependency", "Preserve data consistency with idempotency", "Observe SLOs and failure budgets"],
    "sharding": ["Choose stable shard key", "Route requests deterministically", "Balance data and traffic distribution", "Plan re-sharding strategy", "Protect cross-shard query performance"],
    "consistency": ["Define consistency contract", "Handle partitions explicitly", "Reconcile divergent states", "Expose user-visible guarantees", "Track replication and stale-read lag"],
    "redis": ["Design in-memory data model", "Select persistence mode", "Scale with replication/cluster", "Tune memory + eviction policy", "Monitor latency and replication health"],
    "kafka": ["Model event streams by entity key", "Guarantee partition-level ordering", "Manage producer/consumer reliability", "Control retention and replay", "Measure lag and throughput"],
    "communication": ["Choose sync or async interaction", "Define protocol and framing", "Handle retries/back-pressure", "Secure and observe traffic", "Tune for latency and scale"],
    "spring-boot": ["Structure controller/service/repo layers", "Use DTO + mapper boundaries", "Centralize config/discovery concerns", "Standardize validation and errors", "Instrument health and traces"],
    "system-design": ["Estimate scale assumptions", "Choose data + compute boundaries", "Plan async/sync workflow split", "Model failure and recovery", "Validate with measurable trade-offs"],
    "elasticsearch": ["Inspect query rewrite path", "Profile shard execution", "Tune mappings/analyzers", "Separate query vs fetch costs", "Verify improvements with metrics"],
    "caching": ["Define cache key strategy", "Handle misses and stale data", "Prevent hotspots/stampedes", "Scale proxy + backend pools", "Track hit ratio + p95/p99"],
    "infrastructure": ["Route globally via DNS/CDN", "Deploy safely with rollout controls", "Automate infra changes via IaC", "Guard reliability with SLO alerts", "Use full observability stack"],
    "java": ["Map runtime memory/concurrency model", "Choose safe defaults for GC", "Use concurrent primitives correctly", "Profile under realistic load", "Close loop with regression tests"],
    "behavioral": ["Set context and constraints", "Show specific ownership", "Describe technical decision path", "Quantify outcomes", "Explain prevention improvements"],
    "x-twitter": ["Start with symptom and telemetry", "Narrow to bottleneck hypothesis", "Apply mitigation with rollback path", "Validate impact on tail latency", "Document durable guardrails"],
    "ai-and-vectors": ["Design retrieval architecture", "Tune ANN and filtering", "Ground responses with evidence", "Evaluate quality by layer", "Optimize memory/latency trade-offs"],
}


@dataclass
class VaultDoc:
    path: Path
    relpath: str
    title: str
    text: str
    cleaned_text: str
    paragraphs: list[str]
    tokens: Counter
    local_images: list[str]
    http_images: list[str]


def tokenize(text: str) -> list[str]:
    tokens = [m.group(0).lower() for m in TOKEN_RE.finditer(text)]
    return [tok for tok in tokens if len(tok) > 2 and tok not in STOPWORDS]


def clean_markdown(raw: str) -> str:
    text = CODE_FENCE_RE.sub(" ", raw)
    text = HTTP_IMAGE_RE.sub(" ", text)
    text = OBSIDIAN_IMAGE_RE.sub(" ", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"`", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out = []
    for part in parts:
        part = re.sub(r"\s+", " ", part).strip()
        if len(part) >= 80:
            out.append(part)
    return out


def load_vault_docs(vault_root: Path) -> list[VaultDoc]:
    docs: list[VaultDoc] = []
    for file_path in sorted(vault_root.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in {".md", ".markdown", ".txt"}:
            continue

        raw = file_path.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_markdown(raw)
        paragraphs = split_paragraphs(cleaned)
        if not paragraphs:
            continue

        local_images = OBSIDIAN_IMAGE_RE.findall(raw)
        http_images = HTTP_IMAGE_RE.findall(raw)
        relpath = str(file_path.relative_to(vault_root.parent))
        relpath_lower = relpath.lower()
        if any(pattern.search(relpath_lower) for pattern in NOISY_DOC_PATTERNS):
            continue
        if any(
            noisy in relpath_lower
            for noisy in [
                "system calude prompt.md",
                "post links.md",
                "/test.md",
                "updated test.md",
                "important links.md",
            ]
        ):
            continue
        title = file_path.stem
        docs.append(
            VaultDoc(
                path=file_path,
                relpath=relpath,
                title=title,
                text=raw,
                cleaned_text=cleaned,
                paragraphs=paragraphs,
                tokens=Counter(tokenize(cleaned + " " + relpath)),
                local_images=local_images,
                http_images=http_images,
            )
        )
    return docs


def compute_idf(docs: list[VaultDoc]) -> dict[str, float]:
    doc_count = len(docs)
    df: defaultdict[str, int] = defaultdict(int)
    for doc in docs:
        for token in doc.tokens:
            df[token] += 1

    return {token: math.log((doc_count + 1) / (count + 1)) + 1.0 for token, count in df.items()}


def doc_score(doc: VaultDoc, query_tokens: list[str], idf: dict[str, float], section_slug: str) -> float:
    score = 0.0
    for token in query_tokens:
        tf = doc.tokens.get(token, 0)
        if tf:
            score += (1.0 + math.log(tf)) * idf.get(token, 1.0)

    for extra in SECTION_KEYWORDS.get(section_slug, []):
        tf = doc.tokens.get(extra, 0)
        if tf:
            score += 0.4 * (1.0 + math.log(tf)) * idf.get(extra, 1.0)

    path_lower = doc.relpath.lower()
    if section_slug.replace("-", " ") in path_lower:
        score += 1.2
    if any(piece in path_lower for piece in [section_slug, section_slug.replace("-", " ")]):
        score += 0.8
    for hint in SECTION_PATH_HINTS.get(section_slug, []):
        if hint in path_lower:
            score += 1.6

    # Prefer focused notes over giant catch-all docs.
    if len(doc.cleaned_text) > 24000:
        score -= 1.4
    elif len(doc.cleaned_text) > 12000:
        score -= 0.6

    # Favor title matches strongly.
    title_tokens = set(tokenize(doc.title))
    overlap = title_tokens.intersection(query_tokens)
    score += 0.9 * len(overlap)

    # De-prioritize generic question dumps unless no better docs exist.
    if path_lower.endswith("interview questions.md"):
        if section_slug == "behavioral":
            score += 4.0
        else:
            score -= 3.2

    return score


def paragraph_score(paragraph: str, query_tokens: list[str]) -> float:
    p_tokens = Counter(tokenize(paragraph))
    if not p_tokens:
        return 0.0
    score = 0.0
    for token in query_tokens:
        if p_tokens.get(token):
            score += 1.0 + math.log(p_tokens[token])
    return score


def extract_doc_notes(doc: VaultDoc, query_tokens: list[str], char_budget: int = 1800) -> str:
    scored = [(paragraph_score(p, query_tokens), idx, p) for idx, p in enumerate(doc.paragraphs)]
    scored.sort(key=lambda row: row[0], reverse=True)

    if not scored or scored[0][0] <= 0:
        return "\n\n".join(doc.paragraphs[:3])[:char_budget]

    selected = []
    used = 0
    for _, _, paragraph in scored:
        if paragraph in selected:
            continue
        if used + len(paragraph) > char_budget and selected:
            break
        selected.append(paragraph)
        used += len(paragraph)
        if len(selected) >= 4:
            break

    return "\n\n".join(selected)[:char_budget]


def section_slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def pick_docs_for_question(question: dict, section_slug: str, docs: list[VaultDoc], idf: dict[str, float]) -> list[tuple[float, VaultDoc]]:
    query_text = f"{question['question']} {question.get('core_answer', '')} {question.get('deep_dive', '')}"
    query_tokens = tokenize(query_text)

    if not query_tokens:
        query_tokens = SECTION_KEYWORDS.get(section_slug, [])

    if section_slug == "behavioral":
        behavioral_docs = []
        for doc in docs:
            path = doc.relpath.lower()
            if path.endswith("interview questions.md") or path.endswith("important notes.md"):
                behavioral_docs.append((10.0, doc))
        if behavioral_docs:
            return behavioral_docs[:2]

    hints = SECTION_PATH_HINTS.get(section_slug, [])
    preferred_docs = []
    if hints:
        for doc in docs:
            path = doc.relpath.lower()
            if any(hint in path for hint in hints):
                preferred_docs.append(doc)

    source_docs = preferred_docs if preferred_docs else docs

    ranked = []
    for doc in source_docs:
        score = doc_score(doc, query_tokens, idf, section_slug)
        if score > 0:
            ranked.append((score, doc))

    def generic_rank_penalty(row: tuple[float, VaultDoc]) -> int:
        return 1 if row[1].relpath.lower().endswith("interview questions.md") else 0

    ranked.sort(key=lambda row: (generic_rank_penalty(row), -row[0]))

    if ranked and ranked[0][0] > 1.2:
        first_score = ranked[0][0]
        picks = [ranked[0]]
        if len(ranked) > 1 and ranked[1][0] >= max(1.2, first_score * 0.65):
            picks.append(ranked[1])
        return picks

    # fallback: pick docs with section keyword in path
    section_picks = []
    needle = section_slug.replace("-", " ")
    for doc in docs:
        path = doc.relpath.lower()
        if section_slug in path or needle in path:
            section_picks.append((1.0, doc))
    if section_picks:
        return section_picks[:2]

    return ranked[:2]


def build_deep_dive(base_deep: str, picked: list[tuple[float, VaultDoc]], query_tokens: list[str]) -> tuple[str, list[str]]:
    if not picked:
        return base_deep, []

    chunks = [base_deep.strip()]
    source_paths = []

    chunks.append("Vault Notes (from your Technical Obsidian):")
    for _, doc in picked:
        source_paths.append(doc.relpath)
        notes = extract_doc_notes(doc, query_tokens)
        chunks.append(f"Source: {doc.relpath}\n{notes}")

    return "\n\n".join(chunk for chunk in chunks if chunk).strip(), source_paths


def wrap_svg_text(text: str, width: int) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return [""]
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def xml_escape(value: str) -> str:
    return html.escape(value, quote=True)


def diagram_steps(question_text: str, section_slug: str) -> list[str]:
    for pattern, steps in DIAGRAM_PATTERNS:
        if pattern.search(question_text):
            return steps

    fallback = SECTION_DIAGRAM_FALLBACK.get(section_slug)
    if fallback:
        return fallback

    keywords = [tok for tok in tokenize(question_text) if tok not in STOPWORDS][:2]
    key = " / ".join(keywords) if keywords else "core concept"
    return [
        f"Define {key} clearly",
        "Explain request/data flow",
        "Discuss trade-offs and failure modes",
        "Show scale and reliability implications",
        "Close with metrics and debugging plan",
    ]


def render_svg(question_text: str, section_name: str, steps: list[str]) -> str:
    width, height = 1300, 820
    boxes = [
        (70, 180, 1160, 90),
        (70, 290, 1160, 90),
        (70, 400, 1160, 90),
        (70, 510, 1160, 90),
        (70, 620, 1160, 90),
    ]

    title_lines = wrap_svg_text(question_text, 66)
    title_y = 85

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        "<linearGradient id=\"bg\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">",
        "<stop offset=\"0%\" stop-color=\"#f4fbfa\"/>",
        "<stop offset=\"100%\" stop-color=\"#fff6ee\"/>",
        "</linearGradient>",
        "</defs>",
        "<rect x=\"0\" y=\"0\" width=\"1300\" height=\"820\" fill=\"url(#bg)\"/>",
        "<rect x=\"32\" y=\"30\" width=\"1236\" height=\"760\" rx=\"24\" fill=\"#ffffff\" stroke=\"#d9e7e5\" stroke-width=\"2\"/>",
        f'<text x="70" y="58" fill="#0f766e" font-size="26" font-family="Arial, Helvetica, sans-serif" font-weight="700">{xml_escape(section_name)} Concept Flow</text>',
    ]

    for idx, line in enumerate(title_lines[:3]):
        y = title_y + (idx * 34)
        svg_parts.append(
            f'<text x="70" y="{y}" fill="#1f2937" font-size="34" font-family="Arial, Helvetica, sans-serif" font-weight="700">{xml_escape(line)}</text>'
        )

    for idx, (x, y, w, h) in enumerate(boxes):
        fill = "#ecf7f6" if idx % 2 == 0 else "#fff0e2"
        stroke = "#b7dfda" if idx % 2 == 0 else "#f2d1b2"
        svg_parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )

        step_lines = wrap_svg_text(steps[idx], 74)
        text_y = y + 36
        svg_parts.append(
            f'<text x="98" y="{text_y}" fill="#213042" font-size="27" font-family="Arial, Helvetica, sans-serif" font-weight="600">{idx + 1}. {xml_escape(step_lines[0])}</text>'
        )
        for j, sub in enumerate(step_lines[1:3], start=1):
            svg_parts.append(
                f'<text x="132" y="{text_y + (j * 28)}" fill="#334155" font-size="24" font-family="Arial, Helvetica, sans-serif">{xml_escape(sub)}</text>'
            )

        if idx < len(boxes) - 1:
            arrow_y1 = y + h
            arrow_y2 = y + h + 18
            svg_parts.append(
                f'<line x1="650" y1="{arrow_y1}" x2="650" y2="{arrow_y2}" stroke="#6b7280" stroke-width="3"/>'
            )
            svg_parts.append(
                f'<polygon points="650,{arrow_y2 + 8} 642,{arrow_y2 - 4} 658,{arrow_y2 - 4}" fill="#6b7280"/>'
            )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def choose_note_image(picked_docs: list[tuple[float, VaultDoc]], vault_root: Path) -> tuple[Path | None, str | None, str | None]:
    image_index: defaultdict[str, list[Path]] = defaultdict(list)
    for file_path in vault_root.parent.rglob("Pasted image *"):
        if file_path.is_file():
            image_index[file_path.name].append(file_path)

    for _, doc in picked_docs:
        for image_name in doc.local_images:
            candidates = image_index.get(image_name, [])
            if candidates:
                return candidates[0], f"Obsidian image from {doc.relpath}", ""

        for url in doc.http_images:
            return Path(url), f"Image referenced in {doc.relpath}", url

    return None, None, None


def copy_or_download_image(source: Path, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source.as_posix().startswith("http://") or source.as_posix().startswith("https://"):
        try:
            req = urllib.request.Request(
                source.as_posix(),
                headers={"User-Agent": "interview-prep-site/1.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as response, destination.open("wb") as out:
                out.write(response.read())
            return True
        except Exception:
            return False

    if source.exists() and source.is_file():
        shutil.copyfile(source, destination)
        return True

    return False


def extension_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    ext = Path(parsed.path).suffix.lower()
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
        return ext
    return ".png"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--vault",
        type=Path,
        default=Path("/Users/johnsonanikethnagamallah/Documents/vault/Technical"),
    )
    args = parser.parse_args()

    root = args.root.resolve()
    vault_root = args.vault.resolve()

    bank_path = root / "backend" / "data" / "question_bank.json"
    out_dir = root / "frontend" / "illustrations" / "questions"

    if out_dir.exists():
        for existing in out_dir.iterdir():
            if existing.is_file():
                existing.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    with bank_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    docs = load_vault_docs(vault_root)
    if not docs:
        raise RuntimeError(f"No docs found in vault: {vault_root}")

    idf = compute_idf(docs)

    updated = 0
    with_vault_sources = 0

    for section in payload["sections"]:
        section_name = section["name"]
        section_slug = section.get("slug") or section_slugify(section_name)

        for question in section["questions"]:
            question_id = question["id"]
            query_tokens = tokenize(
                f"{question['question']} {question.get('core_answer', '')} {question.get('deep_dive', '')}"
            )
            if not query_tokens:
                query_tokens = SECTION_KEYWORDS.get(section_slug, [])

            picked = pick_docs_for_question(question, section_slug, docs, idf)
            deep_dive, vault_sources = build_deep_dive(question.get("deep_dive", ""), picked, query_tokens)
            question["deep_dive"] = deep_dive
            question["vault_sources"] = vault_sources

            if vault_sources:
                with_vault_sources += 1

            # Ensure interview notes include vault source hints.
            notes = list(question.get("notes") or [])
            for source in vault_sources[:2]:
                note_line = f"Vault source: {source}"
                if note_line not in notes:
                    notes.append(note_line)
            question["notes"] = notes[:8]

            # 1) Generated concept diagram (always unique per question)
            steps = diagram_steps(question["question"], section_slug)
            svg_path = out_dir / f"{question_id}-diagram.svg"
            svg_content = render_svg(question["question"], section_name, steps)
            svg_path.write_text(svg_content, encoding="utf-8")

            illustrations = [
                {
                    "image_path": f"/illustrations/questions/{question_id}-diagram.svg",
                    "caption": "Question-specific concept flow diagram",
                    "source_title": "Generated from question intent + vault context",
                    "source_url": "",
                }
            ]

            # 2) Vault image (if available) as secondary illustration
            image_source, source_title, source_url = choose_note_image(picked, vault_root)
            if image_source is not None:
                if source_url:
                    ext = extension_from_url(source_url)
                else:
                    ext = image_source.suffix.lower() or ".png"
                dest = out_dir / f"{question_id}-vault{ext}"
                if copy_or_download_image(image_source, dest):
                    illustrations.append(
                        {
                            "image_path": f"/illustrations/questions/{dest.name}",
                            "caption": "Illustration referenced by relevant Obsidian note",
                            "source_title": source_title or "Obsidian vault",
                            "source_url": source_url or "",
                        }
                    )

            question["illustrations"] = illustrations
            updated += 1

    payload["generated_at"] = payload.get("generated_at")

    with bank_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

    print(
        f"Updated {updated} questions. Vault-backed deep dives: {with_vault_sources}. Diagram folder: {out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
