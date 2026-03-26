#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";

const root = path.resolve(process.argv[2] || process.cwd());
const indexPath = path.join(root, "index.html");
const generatedAnswersPath = path.join(root, "generated-draft-answers.js");
const outputPath = path.join(root, "backend", "data", "question_bank.json");

function mustMatch(source, regex, label) {
  const match = source.match(regex);
  if (!match) {
    throw new Error(`Unable to parse ${label}`);
  }
  return match[0];
}

function evalCode(code) {
  return vm.runInNewContext(`(${code})`, {}, { timeout: 1000 });
}

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function dedupe(values) {
  return [...new Set(values.filter(Boolean))];
}

const indexSource = fs.readFileSync(indexPath, "utf8");
const sectionsSnippet = mustMatch(
  indexSource,
  /const sections = \[(.|\n)*?\n\];\n\nconst draftAnswerAliases/,
  "sections"
);
const aliasesSnippet = mustMatch(
  indexSource,
  /const draftAnswerAliases = \{[\s\S]*?\n\};\n\nconst sectionIllustrations/,
  "draftAnswerAliases"
);
const overridesSnippet = mustMatch(
  indexSource,
  /const questionRichOverrides = \{[\s\S]*?\n\};\n\nconst draftAnswerSource/,
  "questionRichOverrides"
);

const sectionsCode = sectionsSnippet
  .replace(/^const sections = /, "")
  .replace(/;\n\nconst draftAnswerAliases$/, "");
const aliasesCode = aliasesSnippet
  .replace(/^const draftAnswerAliases = /, "")
  .replace(/;\n\nconst sectionIllustrations$/, "");
const overridesCode = overridesSnippet
  .replace(/^const questionRichOverrides = /, "")
  .replace(/;\n\nconst draftAnswerSource$/, "");

const sections = evalCode(sectionsCode);
const draftAnswerAliases = evalCode(aliasesCode);
const questionRichOverrides = evalCode(overridesCode);

const generatedContext = { window: {} };
vm.createContext(generatedContext);
vm.runInContext(fs.readFileSync(generatedAnswersPath, "utf8"), generatedContext, {
  timeout: 1000,
});
const generatedDraftAnswers = generatedContext.window.generatedDraftAnswers || {};

const sectionAssets = {
  Microservices: {
    imagePath: "/illustrations/microservices.png",
    sourceTitle: "microservices.io",
    sourceUrl: "https://microservices.io/",
  },
  Sharding: {
    imagePath: "/illustrations/sharding.png",
    sourceTitle: "Wikipedia - Shard (database architecture)",
    sourceUrl: "https://en.wikipedia.org/wiki/Shard_(database_architecture)",
  },
  Consistency: {
    imagePath: "/illustrations/consistency.png",
    sourceTitle: "Wikipedia - CAP theorem",
    sourceUrl: "https://en.wikipedia.org/wiki/CAP_theorem",
  },
  Redis: {
    imagePath: "/illustrations/redis.png",
    sourceTitle: "Wikipedia - Redis",
    sourceUrl: "https://en.wikipedia.org/wiki/Redis",
  },
  Kafka: {
    imagePath: "/illustrations/kafka.png",
    sourceTitle: "Wikipedia - Apache Kafka",
    sourceUrl: "https://en.wikipedia.org/wiki/Apache_Kafka",
  },
  Communication: {
    imagePath: "/illustrations/communication.png",
    sourceTitle: "Wikipedia - WebSocket",
    sourceUrl: "https://en.wikipedia.org/wiki/WebSocket",
  },
  "Spring Boot": {
    imagePath: "/illustrations/spring-boot.png",
    sourceTitle: "Wikipedia - Spring Framework",
    sourceUrl: "https://en.wikipedia.org/wiki/Spring_Framework",
  },
  "System Design": {
    imagePath: "/illustrations/system-design.png",
    sourceTitle: "Wikipedia - Systems design",
    sourceUrl: "https://en.wikipedia.org/wiki/Systems_design",
  },
  Elasticsearch: {
    imagePath: "/illustrations/elasticsearch.png",
    sourceTitle: "Wikipedia - Elasticsearch",
    sourceUrl: "https://en.wikipedia.org/wiki/Elasticsearch",
  },
  Caching: {
    imagePath: "/illustrations/caching.png",
    sourceTitle: "Wikipedia - CPU cache",
    sourceUrl: "https://en.wikipedia.org/wiki/CPU_cache",
  },
  Infrastructure: {
    imagePath: "/illustrations/infrastructure.png",
    sourceTitle: "Wikipedia - Kubernetes",
    sourceUrl: "https://en.wikipedia.org/wiki/Kubernetes",
  },
  Java: {
    imagePath: "/illustrations/java.png",
    sourceTitle: "Wikipedia - Java virtual machine",
    sourceUrl: "https://en.wikipedia.org/wiki/Java_virtual_machine",
  },
  Behavioral: {
    imagePath: "/illustrations/behavioral.png",
    sourceTitle: "The Muse - STAR interview method",
    sourceUrl: "https://www.themuse.com/advice/star-interview-method",
  },
  "X/Twitter": {
    imagePath: "/illustrations/x-twitter.png",
    sourceTitle: "Wikipedia - Twitter",
    sourceUrl: "https://en.wikipedia.org/wiki/Twitter",
  },
  "AI & Vectors": {
    imagePath: "/illustrations/ai-vectors.png",
    sourceTitle: "Wikipedia - Nearest neighbor search",
    sourceUrl: "https://en.wikipedia.org/wiki/Nearest_neighbor_search",
  },
};

const sectionSummaries = {
  Microservices:
    "Service decomposition, resiliency patterns, and operational controls for distributed backend systems.",
  Sharding:
    "Data partitioning strategies and shard-key design for scaling relational or NoSQL storage.",
  Consistency:
    "Consistency models, CAP trade-offs, replication, and conflict-handling in distributed services.",
  Redis:
    "Redis internals, replication, memory policy, persistence, and production diagnostics.",
  Kafka:
    "Partitioning, ordering, replication, and event-driven reliability patterns with Kafka.",
  Communication:
    "Request/response, streaming, push channels, sidecars, and protocol-level back-pressure.",
  "Spring Boot":
    "Spring and Spring Cloud concepts for production-grade Java microservices platforms.",
  "System Design":
    "Architecture interviews focused on estimation, constraints, and trade-off-oriented decision making.",
  Elasticsearch:
    "Query execution, profiling, wildcard behavior, and debugging search latency at shard level.",
  Caching:
    "Cache architecture patterns, failure modes, routing layers, and scale bottlenecks.",
  Infrastructure:
    "Core platform topics including DNS, CDN, Kubernetes, IaC, rollout strategy, and observability.",
  Java:
    "Runtime internals, concurrency, memory management, and modern Java backend coding patterns.",
  Behavioral:
    "Structured interview storytelling for impact, ownership, and technical decision narrative.",
  "X/Twitter":
    "Production debugging, high-scale data systems, and reliability interview themes from social platforms.",
  "AI & Vectors":
    "Vector search, ANN index tuning, RAG evaluation, and AI infrastructure interview depth.",
};

const sectionReferences = {
  Microservices: [
    { title: "microservices.io patterns", url: "https://microservices.io/patterns/index.html" },
    { title: "AWS microservices guidance", url: "https://aws.amazon.com/microservices/" },
  ],
  Sharding: [
    {
      title: "Wikipedia - Shard (database architecture)",
      url: "https://en.wikipedia.org/wiki/Shard_(database_architecture)",
    },
    { title: "MongoDB sharding concepts", url: "https://www.mongodb.com/docs/manual/sharding/" },
  ],
  Consistency: [
    { title: "Wikipedia - CAP theorem", url: "https://en.wikipedia.org/wiki/CAP_theorem" },
    { title: "Martin Kleppmann consistency notes", url: "https://martin.kleppmann.com/" },
  ],
  Redis: [
    { title: "Redis docs", url: "https://redis.io/docs/latest/" },
    { title: "Redis replication", url: "https://redis.io/docs/latest/operate/oss_and_stack/management/replication/" },
  ],
  Kafka: [
    { title: "Apache Kafka docs", url: "https://kafka.apache.org/documentation/" },
    { title: "Confluent design docs", url: "https://docs.confluent.io/platform/current/" },
  ],
  Communication: [
    { title: "MDN WebSocket API", url: "https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API" },
    { title: "IETF HTTP semantics", url: "https://www.rfc-editor.org/rfc/rfc9110" },
  ],
  "Spring Boot": [
    { title: "Spring Boot docs", url: "https://docs.spring.io/spring-boot/docs/current/reference/html/" },
    { title: "Spring Cloud docs", url: "https://docs.spring.io/spring-cloud/docs/current/reference/html/" },
  ],
  "System Design": [
    { title: "Wikipedia - Systems design", url: "https://en.wikipedia.org/wiki/Systems_design" },
    { title: "Google SRE workbook", url: "https://sre.google/workbook/table-of-contents/" },
  ],
  Elasticsearch: [
    { title: "Elastic search docs", url: "https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html" },
    { title: "OpenSearch query profiling", url: "https://opensearch.org/docs/latest/search-plugins/search-profile/" },
  ],
  Caching: [
    { title: "Wikipedia - Cache (computing)", url: "https://en.wikipedia.org/wiki/Cache_(computing)" },
    { title: "Cloudflare caching", url: "https://developers.cloudflare.com/cache/" },
  ],
  Infrastructure: [
    { title: "Kubernetes concepts", url: "https://kubernetes.io/docs/concepts/" },
    { title: "Terraform docs", url: "https://developer.hashicorp.com/terraform/docs" },
  ],
  Java: [
    { title: "Java language docs", url: "https://docs.oracle.com/en/java/" },
    { title: "JVM spec", url: "https://docs.oracle.com/javase/specs/jvms/se21/html/" },
  ],
  Behavioral: [
    { title: "STAR interview method", url: "https://www.themuse.com/advice/star-interview-method" },
    { title: "Behavioral interviewing guide", url: "https://www.indeed.com/career-advice/interviewing/behavioral-interview-questions" },
  ],
  "X/Twitter": [
    { title: "X developer docs", url: "https://developer.x.com/en/docs" },
    { title: "Wikipedia - Twitter", url: "https://en.wikipedia.org/wiki/Twitter" },
  ],
  "AI & Vectors": [
    { title: "OpenSearch vector search", url: "https://opensearch.org/docs/latest/vector-search/" },
    { title: "Wikipedia - Nearest neighbor search", url: "https://en.wikipedia.org/wiki/Nearest_neighbor_search" },
  ],
};

const sectionNoteTemplates = {
  Microservices: [
    "Start with service boundaries and why each boundary exists for that business domain.",
    "Call out failure controls early: timeouts, retries, circuit breaking, and idempotency.",
    "Explain observability signals you would inspect first when a dependency degrades.",
  ],
  Sharding: [
    "Always justify shard-key choice with real access patterns and cardinality distribution.",
    "Discuss resharding and migration cost before claiming long-term scalability.",
    "Mention hotspot detection and mitigation in both data and traffic paths.",
  ],
  Consistency: [
    "Tie consistency level to business impact and user-visible correctness requirements.",
    "Clarify write/read paths and where stale reads are acceptable or dangerous.",
    "Include conflict resolution and reconciliation strategy, not only replication mode.",
  ],
  Redis: [
    "Connect persistence mode directly to durability requirements and restart behavior.",
    "Describe memory policy and eviction impacts under sustained pressure.",
    "Mention replication lag and failover behavior as operational concerns, not theory.",
  ],
  Kafka: [
    "Anchor ordering guarantees at partition scope and key selection strategy.",
    "Explain producer ack mode and ISR trade-offs with durability and throughput.",
    "Cover consumer group rebalancing and idempotency for reliable processing.",
  ],
  Communication: [
    "Frame protocol choice by latency, directionality, and reliability constraints.",
    "Explicitly discuss timeout, retry, and back-pressure behavior in overload conditions.",
    "Mention observability at request boundary and connection lifecycle levels.",
  ],
  "Spring Boot": [
    "Keep API contracts stable with DTOs and explicit validation boundaries.",
    "Show operational readiness via tracing, health checks, and centralized config.",
    "Highlight framework trade-offs with team scale and maintainability in mind.",
  ],
  "System Design": [
    "Start by quantifying scale assumptions before proposing architecture components.",
    "Compare at least two options and explain why one fails under your constraints.",
    "State failure paths and fallback behavior for each critical dependency.",
  ],
  Elasticsearch: [
    "Differentiate query-phase cost from fetch-phase cost before selecting fixes.",
    "Use profile and rewrite output to prove where latency originates.",
    "Pair text relevance with mapping/index strategy to keep latency predictable.",
  ],
  Caching: [
    "Discuss invalidation strategy and stale data risk alongside hit ratio.",
    "Identify cache stampede and hotspot mitigation before scale testing.",
    "Treat proxy and network limits as first-class bottlenecks in cache layers.",
  ],
  Infrastructure: [
    "Explain control-plane and data-plane responsibilities separately.",
    "Map rollout strategy to blast-radius controls and rollback speed.",
    "Describe logs, metrics, and traces as a coordinated debugging toolkit.",
  ],
  Java: [
    "Separate JVM memory issues from thread-pool or off-heap resource exhaustion.",
    "Prefer clarity on concurrency semantics over memorizing API signatures.",
    "Connect performance tuning to measured bottlenecks and GC evidence.",
  ],
  Behavioral: [
    "Use STAR structure with concrete scale numbers and measurable outcomes.",
    "Name the technical trade-off and why your decision was selected.",
    "Close with follow-up guardrails that prevented recurrence.",
  ],
  "X/Twitter": [
    "Start from symptom and telemetry, then narrow to one bottleneck hypothesis.",
    "Prioritize mitigation and blast-radius reduction before perfect root-cause detail.",
    "Show postmortem guardrails to demonstrate ownership and learning.",
  ],
  "AI & Vectors": [
    "Separate retrieval quality from generation quality when evaluating AI systems.",
    "Discuss recall-latency-memory trade-offs explicitly for ANN index tuning.",
    "Combine metadata filtering with vector similarity for production correctness.",
  ],
};

const keywordNoteRules = [
  {
    test: /(idempotency|retry|exactly-once)/i,
    note: "Whenever retries exist, explicitly mention dedupe keys, replay safety, and bounded retry policy.",
  },
  {
    test: /(cache|redis|memcached|evict|ttl)/i,
    note: "Cache conversations are strongest when you pair hit-rate with invalidation and stale-data controls.",
  },
  {
    test: /(kafka|stream|pub\/sub|queue|consumer)/i,
    note: "Event pipelines should include partition strategy, consumer lag handling, and replay semantics.",
  },
  {
    test: /(vector|rag|embedding|ann|hnsw|ivf|quant)/i,
    note: "AI search answers should distinguish retrieval relevance, ranking quality, and answer faithfulness.",
  },
  {
    test: /(latency|p99|slow|profile|wildcard|query)/i,
    note: "For latency questions, identify phase-level timing first so optimization targets the real bottleneck.",
  },
];

function buildFallbackDeepDive(question, coreAnswer, sectionName) {
  return (
    `${coreAnswer}\n\n` +
    `Why this matters in ${sectionName}: this topic usually appears when interviewers are checking whether you can connect design choices to reliability, latency, and operability under real load.\n\n` +
    `How to answer "${question}" with depth: start with a crisp definition, add one production scenario where the concept helps, name one trade-off or failure mode, and close with the first metric, log, or trace you would inspect to confirm system behavior.`
  );
}

function getDraftDeepDive(questionText) {
  if (generatedDraftAnswers[questionText]) {
    return generatedDraftAnswers[questionText];
  }
  const alias = draftAnswerAliases[questionText];
  if (alias && generatedDraftAnswers[alias]) {
    return generatedDraftAnswers[alias];
  }
  return "";
}

function buildNotes(question, sectionName, tip) {
  const sectionNotes = sectionNoteTemplates[sectionName] || [];
  const keywordNotes = keywordNoteRules
    .filter((rule) => rule.test.test(question))
    .map((rule) => rule.note);

  const baseline = [
    tip ? `Interview framing: ${tip}` : "",
    ...keywordNotes,
    ...sectionNotes,
  ];

  return dedupe(baseline).slice(0, 6);
}

function buildQuestionImages(questionId, questionText) {
  const sourceUrl = `https://en.wikipedia.org/w/index.php?search=${encodeURIComponent(questionText)}`;
  return [
    {
      image_path: `/illustrations/questions/${questionId}.png`,
      caption: "Playwright screenshot of internet search results for this exact question",
      source_title: "Wikipedia search",
      source_url: sourceUrl,
    },
  ];
}

const normalizedSections = sections.map((section) => {
  const sectionReference = sectionReferences[section.name] || [];
  const sectionAsset = sectionAssets[section.name] || sectionAssets["System Design"];

  return {
    id: section.id,
    slug: slugify(section.name),
    name: section.name,
    summary: sectionSummaries[section.name] || "Interview concepts and practical production guidance.",
    references: sectionReference,
    default_illustration: {
      image_path: sectionAsset.imagePath,
      source_title: sectionAsset.sourceTitle,
      source_url: sectionAsset.sourceUrl,
    },
    questions: section.questions.map((qa, idx) => {
      const override = questionRichOverrides[qa.q] || {};
      const deepDive =
        override.deep ||
        getDraftDeepDive(qa.q) ||
        buildFallbackDeepDive(qa.q, qa.a, section.name);
      const questionId = `${slugify(section.name)}-${idx + 1}`;

      return {
        id: questionId,
        order: idx + 1,
        question: qa.q,
        core_answer: qa.a,
        deep_dive: deepDive,
        notes: buildNotes(qa.q, section.name, qa.tip || ""),
        interview_tip: qa.tip || "",
        ascii_diagram: override.illustration || null,
        illustrations: buildQuestionImages(questionId, qa.q),
        references: sectionReference,
      };
    }),
  };
});

const totalQuestions = normalizedSections.reduce((sum, section) => sum + section.questions.length, 0);

const payload = {
  generated_at: new Date().toISOString(),
  version: "2.0.0",
  stats: {
    section_count: normalizedSections.length,
    question_count: totalQuestions,
  },
  sections: normalizedSections,
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, JSON.stringify(payload, null, 2));
console.log(`Wrote ${payload.stats.question_count} questions to ${outputPath}`);
