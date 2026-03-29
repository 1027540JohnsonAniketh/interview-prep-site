const { createApp } = Vue;

const ANIMATION_PATTERNS = [
  {
    test: /(microservice|service mesh|saga|strangler|bulkhead|circuit breaker|api gateway)/i,
    kind: "microservices",
    description: "Microservice patterns separate service ownership while controlling cross-service failures.",
    steps: [
      "Define bounded context and service data ownership",
      "Route cross-cutting traffic through an API gateway",
      "Coordinate cross-service state with saga/event flow",
      "Apply retries, circuit breakers, and bulkheads on dependencies",
      "Validate reliability using latency, error, and saturation signals",
    ],
  },
  {
    test: /(load balancer|round robin|least connections|weighted)/i,
    kind: "load-balancing",
    description: "Requests flow through a balancer and are distributed across healthy servers.",
    steps: [
      "Receive incoming requests at the edge balancer",
      "Run algorithm (round-robin, least-connections, or weighted)",
      "Route to the selected backend instance",
      "Observe latency/error and adjust routing choices",
      "Scale or drain servers without dropping traffic",
    ],
  },
  {
    test: /(shard|consistent hashing|rebalance|partition key)/i,
    kind: "sharding",
    description: "Data and traffic are routed by key to stable partitions, then rebalanced when needed.",
    steps: [
      "Choose a high-cardinality immutable shard key",
      "Route request to target shard from shard function",
      "Execute read/write on local shard data",
      "Detect hotspots and skew in shard metrics",
      "Rebalance with minimum key movement and downtime",
    ],
  },
  {
    test: /(cap theorem|eventual consistency|causal|read-your-writes|consistency)/i,
    kind: "consistency",
    description: "Consistency guarantees define what users see under replication lag or partition.",
    steps: [
      "Write is accepted by source of truth node",
      "Replication propagates change to peers",
      "Reads may return stale or latest value",
      "Conflict policy resolves divergent updates",
      "System converges and lag metrics return to baseline",
    ],
  },
  {
    test: /(redis|psync|fullresync|aof|rdb|repl-backlog|sentinel)/i,
    kind: "redis",
    description: "Redis write path and replica sync behavior drive latency and durability outcomes.",
    steps: [
      "Client command executes in-memory on primary",
      "Primary appends persistence state (AOF/RDB)",
      "Replica sync (PSYNC/FULLRESYNC) catches baseline",
      "Backlog replays missed writes after reconnect",
      "Clients read from healthy nodes with monitored lag",
    ],
  },
  {
    test: /(kafka|isr|consumer group|partition|tiered storage|offset)/i,
    kind: "kafka",
    description: "Events move from producer to partition leaders and then to consumer groups.",
    steps: [
      "Producer sends event with partition key",
      "Leader appends event and replicates to ISR",
      "Committed offset becomes visible to consumers",
      "Consumer group processes partition stream in order",
      "Retention/tiered storage handles historical segments",
    ],
  },
  {
    test: /(websocket|sse|long polling|request-response|sidecar|push)/i,
    kind: "communication",
    description: "Protocol choice determines connection lifecycle, latency, and delivery semantics.",
    steps: [
      "Client opens channel (HTTP, SSE, or WebSocket)",
      "Server accepts and establishes flow control rules",
      "Messages stream synchronously or asynchronously",
      "Retries/back-pressure protect downstream services",
      "Telemetry closes the loop on protocol performance",
    ],
  },
  {
    test: /(eureka|spring cloud|gateway|config server|circuit breaker|dto|mapstruct|controlleradvice)/i,
    kind: "spring",
    description: "Spring platform components coordinate discovery, routing, config, and resilience.",
    steps: [
      "Service registers and receives externalized config",
      "Gateway applies auth, routing, and policy filters",
      "Business service maps DTOs and validates input",
      "Circuit breaker isolates unstable dependencies",
      "Observability confirms healthy request behavior",
    ],
  },
  {
    test: /(spotify|subscribe|music streaming|back-of-envelope|hotspot|system design)/i,
    kind: "system-design",
    description: "Architecture decisions evolve from assumptions, load shape, and failure priorities.",
    steps: [
      "Estimate users, QPS, payload, and growth profile",
      "Split traffic into sync and async execution paths",
      "Design data model, cache, and durable storage flow",
      "Add retry/idempotency for failure scenarios",
      "Validate p95/p99 and iterate bottleneck fixes",
    ],
  },
  {
    test: /(elasticsearch|opensearch|wildcard|profile|lucene|query phase|fetch phase|inverted index)/i,
    kind: "search",
    description: "Search latency is explained by rewrite cost, query execution, and fetch overhead.",
    steps: [
      "Query rewrites to executable Lucene clauses",
      "Shard query phase matches and scores candidates",
      "Coordinator merges top hits across shards",
      "Fetch phase loads documents and highlights",
      "Profile output directs mapping/query optimization",
    ],
  },
  {
    test: /(cache|memcached|cache-aside|stampede|ttl|eviction)/i,
    kind: "cache",
    description: "Healthy cache systems protect origin stores while controlling freshness and hotspots.",
    steps: [
      "Request checks cache for key hit/miss",
      "Miss path loads data from source of truth",
      "Result populates cache with TTL and metadata",
      "Coalescing/locks reduce stampede under expiry",
      "Hit ratio and tail latency drive tuning decisions",
    ],
  },
  {
    test: /(dns|cdn|kubernetes|iac|terraform|canary|blue-green|observability)/i,
    kind: "infra",
    description: "Infrastructure reliability comes from safe rollout loops and observability feedback.",
    steps: [
      "Traffic resolves through DNS/CDN entry points",
      "Platform schedules workloads on healthy capacity",
      "Canary rollout shifts controlled traffic slices",
      "Metrics/traces detect regressions quickly",
      "Rollback or promote based on SLO/error budget",
    ],
  },
  {
    test: /(outofmemory|gc|jvm|concurrenthashmap|completablefuture|java)/i,
    kind: "java",
    description: "JVM behavior couples allocation, concurrency, and garbage collection performance.",
    steps: [
      "Requests allocate objects and schedule async work",
      "Heap and thread pools absorb runtime pressure",
      "GC cycles reclaim memory and pause work briefly",
      "Latency spikes reveal hot code paths or leaks",
      "Tuning + code fixes restore stable throughput",
    ],
  },
  {
    test: /(behavioral|tell me about a time|star|technical disagreement|production debugging)/i,
    kind: "behavioral",
    description: "STAR answers are strongest when technical action and measurable impact are explicit.",
    steps: [
      "Situation: define production context and constraints",
      "Task: clarify ownership and success criteria",
      "Action: explain technical decisions and trade-offs",
      "Result: quantify impact with concrete metrics",
      "Learning: show guardrails to prevent recurrence",
    ],
  },
  {
    test: /(twitter|x\/twitter|wal|cursor|p99|distributed lock)/i,
    kind: "twitter",
    description: "High-scale reliability work starts from telemetry, then narrows to one dominant bottleneck.",
    steps: [
      "Detect symptom via p99/error/throughput signals",
      "Trace call path to isolate dominant bottleneck",
      "Apply mitigation with minimal blast radius",
      "Verify recovery under representative traffic",
      "Document guardrails and alert thresholds",
    ],
  },
  {
    test: /(vector|rag|hnsw|ivf|embedding|ann|quantization|turboquant)/i,
    kind: "ai-vectors",
    description: "Vector systems combine retrieval quality, ranking logic, and grounded answer generation.",
    steps: [
      "Embed query into vector space representation",
      "Retrieve candidates from ANN index structure",
      "Apply metadata filters and reranking policy",
      "Generate answer with retrieved evidence context",
      "Evaluate retrieval, faithfulness, and task success",
    ],
  },
];

const SECTION_ANIMATION_DEFAULTS = {
  Microservices: ANIMATION_PATTERNS.find((p) => p.kind === "microservices"),
  Sharding: ANIMATION_PATTERNS.find((p) => p.kind === "sharding"),
  Consistency: ANIMATION_PATTERNS.find((p) => p.kind === "consistency"),
  Redis: ANIMATION_PATTERNS.find((p) => p.kind === "redis"),
  Kafka: ANIMATION_PATTERNS.find((p) => p.kind === "kafka"),
  Communication: ANIMATION_PATTERNS.find((p) => p.kind === "communication"),
  "Spring Boot": ANIMATION_PATTERNS.find((p) => p.kind === "spring"),
  "System Design": ANIMATION_PATTERNS.find((p) => p.kind === "system-design"),
  Elasticsearch: ANIMATION_PATTERNS.find((p) => p.kind === "search"),
  Caching: ANIMATION_PATTERNS.find((p) => p.kind === "cache"),
  Infrastructure: ANIMATION_PATTERNS.find((p) => p.kind === "infra"),
  Java: ANIMATION_PATTERNS.find((p) => p.kind === "java"),
  Behavioral: ANIMATION_PATTERNS.find((p) => p.kind === "behavioral"),
  "X/Twitter": ANIMATION_PATTERNS.find((p) => p.kind === "twitter"),
  "AI & Vectors": ANIMATION_PATTERNS.find((p) => p.kind === "ai-vectors"),
};

const SIMULATION_FAMILY_BY_KIND = {
  microservices: "fanout",
  "load-balancing": "fanout",
  communication: "fanout",
  spring: "fanout",
  kafka: "fanout",
  cache: "fanout",
  infra: "fanout",
  "system-design": "fanout",
  twitter: "fanout",
  sharding: "ring",
  consistency: "ring",
  redis: "ring",
  "ai-vectors": "ring",
  search: "pipeline",
  java: "pipeline",
  behavioral: "pipeline",
};

const SIMULATION_LABELS = {
  microservices: {
    source: "Client",
    hub: "Gateway",
    workers: ["Service A", "Service B", "Service C", "Event Bus"],
    sink: "Data Stores",
  },
  "load-balancing": {
    source: "Requests",
    hub: "Load Balancer",
    workers: ["App 1", "App 2", "App 3", "App 4"],
    sink: "Databases",
  },
  sharding: {
    source: "Request",
    hub: "Shard Router",
    workers: ["Shard 1", "Shard 2", "Shard 3", "Shard 4"],
    sink: "Replica Read",
  },
  consistency: {
    source: "Write",
    hub: "Primary",
    workers: ["Replica A", "Replica B", "Replica C", "Replica D"],
    sink: "Read Path",
  },
  redis: {
    source: "Client",
    hub: "Redis Primary",
    workers: ["Replica 1", "Replica 2", "AOF", "RDB"],
    sink: "Consumers",
  },
  kafka: {
    source: "Producer",
    hub: "Partition Leader",
    workers: ["Follower 1", "Follower 2", "Consumer G1", "Consumer G2"],
    sink: "Retention/Tier",
  },
  communication: {
    source: "Client",
    hub: "Protocol Layer",
    workers: ["HTTP", "SSE", "WebSocket", "Async Queue"],
    sink: "Business Service",
  },
  spring: {
    source: "Client",
    hub: "Gateway",
    workers: ["Discovery", "Config", "Service", "Circuit Breaker"],
    sink: "Persistent Data",
  },
  "system-design": {
    source: "Users",
    hub: "Edge",
    workers: ["API", "Cache", "Queue", "Worker"],
    sink: "Storage",
  },
  search: {
    stages: ["Query", "Rewrite", "Shard Match", "Merge", "Fetch"],
  },
  cache: {
    source: "Client",
    hub: "Cache Layer",
    workers: ["Cache Hit", "Cache Miss", "Refresh", "Invalidation"],
    sink: "Origin Store",
  },
  infra: {
    source: "Traffic",
    hub: "Ingress",
    workers: ["Canary", "Stable", "Metrics", "Alerts"],
    sink: "SLO Decision",
  },
  java: {
    stages: ["Request", "Heap/Threads", "GC Cycle", "Optimization", "Response"],
  },
  behavioral: {
    stages: ["Situation", "Task", "Action", "Result", "Learning"],
  },
  twitter: {
    source: "Alert",
    hub: "Trace",
    workers: ["Mitigate", "Verify", "Stabilize", "Document"],
    sink: "Recovered",
  },
  "ai-vectors": {
    source: "Prompt",
    hub: "Embedding",
    workers: ["ANN Index", "Metadata Filter", "Reranker", "Context Builder"],
    sink: "Grounded Answer",
  },
};

const SIMULATION_PALETTE_GROUP_BY_KIND = {
  microservices: "teal",
  "load-balancing": "teal",
  communication: "teal",
  spring: "teal",
  cache: "teal",
  kafka: "blue",
  sharding: "blue",
  consistency: "blue",
  redis: "blue",
  search: "amber",
  infra: "amber",
  "system-design": "amber",
  twitter: "amber",
  java: "violet",
  behavioral: "violet",
  "ai-vectors": "violet",
};

const SIMULATION_PALETTES = {
  teal: {
    backgroundStart: "#f4fcfa",
    backgroundEnd: "#fdf7ef",
    edge: "rgba(12, 116, 108, 0.25)",
    flow: "rgba(10, 138, 128, 0.56)",
    nodeFill: "#f2fffd",
    nodeStroke: "#82c9c2",
    packet: "#0f766e",
    packetGlow: "rgba(15, 118, 110, 0.22)",
    text: "#164e49",
  },
  blue: {
    backgroundStart: "#f3f8ff",
    backgroundEnd: "#f9f6ff",
    edge: "rgba(46, 84, 164, 0.26)",
    flow: "rgba(47, 109, 235, 0.58)",
    nodeFill: "#f4f8ff",
    nodeStroke: "#8db5ff",
    packet: "#2457cc",
    packetGlow: "rgba(36, 87, 204, 0.22)",
    text: "#1e3a8a",
  },
  amber: {
    backgroundStart: "#fff9ef",
    backgroundEnd: "#fff5f0",
    edge: "rgba(170, 104, 36, 0.23)",
    flow: "rgba(215, 123, 33, 0.57)",
    nodeFill: "#fffaf1",
    nodeStroke: "#e5b584",
    packet: "#c26a2e",
    packetGlow: "rgba(194, 106, 46, 0.24)",
    text: "#7c3f13",
  },
  violet: {
    backgroundStart: "#f8f5ff",
    backgroundEnd: "#f8fbff",
    edge: "rgba(103, 79, 177, 0.23)",
    flow: "rgba(117, 91, 202, 0.58)",
    nodeFill: "#faf7ff",
    nodeStroke: "#bfa8f6",
    packet: "#6f4fc4",
    packetGlow: "rgba(111, 79, 196, 0.24)",
    text: "#4c2b95",
  },
};

function createSeededRandom(seed) {
  let value = Math.floor(Math.abs(seed || 1)) % 2147483647;
  if (value <= 0) {
    value += 2147483646;
  }
  return () => {
    value = (value * 48271) % 2147483647;
    return (value - 1) / 2147483646;
  };
}

function isElementVisible(element) {
  if (!element) {
    return false;
  }
  const rect = element.getBoundingClientRect();
  const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
  return rect.bottom >= -120 && rect.top <= viewportHeight + 120;
}

function dedupeEdges(paths, extraEdges = []) {
  const seen = new Set();
  const edges = [];

  const addEdge = (from, to) => {
    if (!from || !to) {
      return;
    }
    const key = `${from}->${to}`;
    if (seen.has(key)) {
      return;
    }
    seen.add(key);
    edges.push([from, to]);
  };

  paths.forEach((path) => {
    for (let index = 0; index < path.length - 1; index += 1) {
      addEdge(path[index], path[index + 1]);
    }
  });
  extraEdges.forEach(([from, to]) => addEdge(from, to));
  return edges;
}

function labelsForKind(kind) {
  return (
    SIMULATION_LABELS[kind] || {
      source: "Input",
      hub: "Router",
      workers: ["Worker A", "Worker B", "Worker C", "Worker D"],
      sink: "Output",
    }
  );
}

function familyForKind(kind) {
  return SIMULATION_FAMILY_BY_KIND[kind] || "fanout";
}

function paletteForKind(kind) {
  const paletteGroup = SIMULATION_PALETTE_GROUP_BY_KIND[kind] || "teal";
  return SIMULATION_PALETTES[paletteGroup] || SIMULATION_PALETTES.teal;
}

function buildSimulationTopology(kind, rng) {
  const family = familyForKind(kind);
  const labels = labelsForKind(kind);

  if (family === "pipeline") {
    const stageLabels = labels.stages || ["Input", "Transform", "Process", "Validate", "Output"];
    const nodes = stageLabels.map((label, index) => ({
      id: `stage-${index}`,
      label,
      x: 0.1 + index * (0.8 / Math.max(1, stageLabels.length - 1)),
      y: 0.52 + (index % 2 === 0 ? -0.08 : 0.08),
      role: index === 0 ? "source" : index === stageLabels.length - 1 ? "sink" : "worker",
    }));
    const path = nodes.map((node) => node.id);
    return {
      nodes,
      paths: [path],
      edges: dedupeEdges([path]),
    };
  }

  if (family === "ring") {
    const workerLabels = (labels.workers || []).slice(0, 4);
    const workerCount = Math.max(3, workerLabels.length || 4);
    const workers = [];
    for (let index = 0; index < workerCount; index += 1) {
      const angle = (-0.9 + (Math.PI * 1.8 * index) / workerCount) % (Math.PI * 2);
      workers.push({
        id: `worker-${index}`,
        label: workerLabels[index] || `Node ${index + 1}`,
        x: 0.62 + Math.cos(angle) * 0.2,
        y: 0.5 + Math.sin(angle) * 0.26,
        role: "worker",
      });
    }

    const nodes = [
      { id: "source", label: labels.source || "Input", x: 0.1, y: 0.5, role: "source" },
      { id: "hub", label: labels.hub || "Coordinator", x: 0.3, y: 0.5, role: "hub" },
      ...workers,
      { id: "sink", label: labels.sink || "Output", x: 0.9, y: 0.5, role: "sink" },
    ];

    const paths = workers.map((worker, index) => [
      "source",
      "hub",
      worker.id,
      workers[(index + 1) % workers.length].id,
      "sink",
    ]);

    const ringEdges = workers.map((worker, index) => [
      worker.id,
      workers[(index + 1) % workers.length].id,
    ]);

    return {
      nodes,
      paths,
      edges: dedupeEdges(paths, ringEdges),
    };
  }

  const workerLabels = (labels.workers || []).slice(0, 4);
  const workerCount = Math.max(3, Math.min(4, workerLabels.length || 4));
  const nodes = [
    { id: "source", label: labels.source || "Input", x: 0.08, y: 0.5, role: "source" },
    { id: "hub", label: labels.hub || "Router", x: 0.29, y: 0.5, role: "hub" },
    { id: "sink", label: labels.sink || "Output", x: 0.9, y: 0.5, role: "sink" },
  ];

  for (let index = 0; index < workerCount; index += 1) {
    const verticalSpread = workerCount === 1 ? 0.5 : 0.2 + (index * 0.6) / (workerCount - 1);
    nodes.push({
      id: `worker-${index}`,
      label: workerLabels[index] || `Worker ${index + 1}`,
      x: 0.6,
      y: verticalSpread,
      role: "worker",
    });
  }

  const paths = nodes
    .filter((node) => node.id.startsWith("worker-"))
    .map((worker) => ["source", "hub", worker.id, "sink"]);

  return {
    nodes,
    paths,
    edges: dedupeEdges(paths),
  };
}

function createConceptSimulation(canvas, options = {}) {
  const context = canvas.getContext("2d");
  if (!context) {
    return null;
  }

  const seed = Number.isFinite(options.seed) ? options.seed : 1;
  const random = createSeededRandom(seed);
  const kind = options.kind || "load-balancing";
  const topology = buildSimulationTopology(kind, random);
  const palette = paletteForKind(kind);

  const nodeMap = {};
  topology.nodes.forEach((node) => {
    nodeMap[node.id] = node;
  });

  const state = {
    width: 0,
    height: 0,
    packetSpawnAccumulator: random() * 0.28,
    packetSpawnInterval: 0.24 + random() * 0.18,
    packets: [],
    nodeHeat: {},
    flowOffset: random() * 120,
    lastTimestamp: 0,
    rafId: null,
    active: false,
  };

  topology.nodes.forEach((node) => {
    state.nodeHeat[node.id] = 0;
  });

  function toPoint(nodeId) {
    const node = nodeMap[nodeId];
    return {
      x: node.x * state.width,
      y: node.y * state.height,
    };
  }

  function resize() {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) {
      return;
    }
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, Math.round(rect.width * dpr));
    canvas.height = Math.max(1, Math.round(rect.height * dpr));
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    state.width = rect.width;
    state.height = rect.height;
    draw();
  }

  function spawnPacket() {
    if (!topology.paths.length) {
      return;
    }
    const path = topology.paths[Math.floor(random() * topology.paths.length)];
    if (!path || path.length < 2) {
      return;
    }
    state.packets.push({
      path,
      segment: 0,
      progress: 0,
      speed: 0.42 + random() * 0.3,
      radius: 3 + random() * 1.2,
    });
  }

  function update(dt) {
    state.packetSpawnAccumulator += dt;
    while (state.packetSpawnAccumulator >= state.packetSpawnInterval) {
      state.packetSpawnAccumulator -= state.packetSpawnInterval;
      spawnPacket();
    }

    state.flowOffset += dt * 42;
    Object.keys(state.nodeHeat).forEach((nodeId) => {
      state.nodeHeat[nodeId] = Math.max(0, state.nodeHeat[nodeId] - dt * 0.9);
    });

    const nextPackets = [];

    state.packets.forEach((packet) => {
      let remaining = dt * packet.speed;
      while (remaining > 0) {
        const segmentRemaining = 1 - packet.progress;
        if (remaining < segmentRemaining) {
          packet.progress += remaining;
          remaining = 0;
          break;
        }

        remaining -= segmentRemaining;
        const destinationId = packet.path[packet.segment + 1];
        if (destinationId && Object.hasOwn(state.nodeHeat, destinationId)) {
          state.nodeHeat[destinationId] = Math.min(1.2, state.nodeHeat[destinationId] + 0.62);
        }

        packet.segment += 1;
        packet.progress = 0;

        if (packet.segment >= packet.path.length - 1) {
          remaining = 0;
          packet.done = true;
        }
      }

      if (!packet.done) {
        nextPackets.push(packet);
      }
    });

    state.packets = nextPackets.slice(-220);
  }

  function drawBackground() {
    const background = context.createLinearGradient(0, 0, 0, state.height);
    background.addColorStop(0, palette.backgroundStart);
    background.addColorStop(1, palette.backgroundEnd);
    context.fillStyle = background;
    context.fillRect(0, 0, state.width, state.height);

    context.strokeStyle = "rgba(148, 163, 184, 0.12)";
    context.lineWidth = 1;
    for (let x = 28; x < state.width; x += 42) {
      context.beginPath();
      context.moveTo(x, 0);
      context.lineTo(x, state.height);
      context.stroke();
    }
  }

  function drawEdges() {
    context.save();
    context.lineCap = "round";

    topology.edges.forEach(([fromId, toId]) => {
      const from = toPoint(fromId);
      const to = toPoint(toId);
      context.beginPath();
      context.strokeStyle = palette.edge;
      context.lineWidth = 2;
      context.moveTo(from.x, from.y);
      context.lineTo(to.x, to.y);
      context.stroke();
    });

    context.setLineDash([8, 10]);
    context.lineDashOffset = -state.flowOffset;
    topology.edges.forEach(([fromId, toId]) => {
      const from = toPoint(fromId);
      const to = toPoint(toId);
      context.beginPath();
      context.strokeStyle = palette.flow;
      context.lineWidth = 2.2;
      context.moveTo(from.x, from.y);
      context.lineTo(to.x, to.y);
      context.stroke();
    });
    context.setLineDash([]);
    context.restore();
  }

  function drawPackets() {
    state.packets.forEach((packet) => {
      const fromId = packet.path[packet.segment];
      const toId = packet.path[packet.segment + 1];
      const from = toPoint(fromId);
      const to = toPoint(toId);
      const x = from.x + (to.x - from.x) * packet.progress;
      const y = from.y + (to.y - from.y) * packet.progress;

      context.beginPath();
      context.fillStyle = palette.packet;
      context.shadowColor = palette.packetGlow;
      context.shadowBlur = 9;
      context.arc(x, y, packet.radius, 0, Math.PI * 2);
      context.fill();
      context.shadowBlur = 0;
    });
  }

  function drawNodes() {
    topology.nodes.forEach((node) => {
      const point = toPoint(node.id);
      const heat = state.nodeHeat[node.id] || 0;
      const radius = node.role === "worker" ? 14 : 16;

      if (heat > 0.02) {
        context.beginPath();
        context.fillStyle = palette.packetGlow;
        context.arc(point.x, point.y, radius + heat * 8, 0, Math.PI * 2);
        context.fill();
      }

      context.beginPath();
      context.fillStyle = palette.nodeFill;
      context.strokeStyle = palette.nodeStroke;
      context.lineWidth = 2;
      context.arc(point.x, point.y, radius, 0, Math.PI * 2);
      context.fill();
      context.stroke();

      context.fillStyle = palette.text;
      context.font = "600 11px 'Sora', sans-serif";
      context.textAlign = "center";
      context.textBaseline = "top";
      context.fillText(node.label, point.x, point.y + radius + 8);
    });
  }

  function draw() {
    if (!state.width || !state.height) {
      return;
    }
    context.clearRect(0, 0, state.width, state.height);
    drawBackground();
    drawEdges();
    drawPackets();
    drawNodes();
  }

  function frame(timestamp) {
    if (!state.active) {
      return;
    }
    if (!state.lastTimestamp) {
      state.lastTimestamp = timestamp;
    }
    const dt = Math.min(0.05, (timestamp - state.lastTimestamp) / 1000);
    state.lastTimestamp = timestamp;
    update(dt);
    draw();
    state.rafId = requestAnimationFrame(frame);
  }

  function start() {
    if (state.active) {
      return;
    }
    state.active = true;
    state.lastTimestamp = 0;
    state.rafId = requestAnimationFrame(frame);
  }

  function stop() {
    state.active = false;
    if (state.rafId) {
      cancelAnimationFrame(state.rafId);
      state.rafId = null;
    }
  }

  function setActive(value) {
    if (value) {
      start();
      return;
    }
    stop();
    draw();
  }

  function destroy() {
    stop();
    state.packets = [];
  }

  resize();

  return {
    canvas,
    kind,
    resize,
    setActive,
    destroy,
  };
}

const PYTHON_QUEST_STORAGE_KEY = "python-quest-progress-v1";
const PYTHON_QUEST_REALMS = [
  {
    title: "Syntax Springs",
    code: "ST-01",
    accent: "#0f766e",
    soft: "#dff7f3",
    glow: "#92ddd2",
    blurb: "Shape variables, types, and f-strings before you push deeper into the map.",
  },
  {
    title: "Loop Lagoon",
    code: "CF-02",
    accent: "#2563eb",
    soft: "#e4efff",
    glow: "#9fc4ff",
    blurb: "Steer through branches, ranges, and loop control without drifting off course.",
  },
  {
    title: "Function Forge",
    code: "FN-03",
    accent: "#7c3aed",
    soft: "#efe6ff",
    glow: "#ceb2ff",
    blurb: "Craft reusable spells with parameters, returns, and concise lambda tricks.",
  },
  {
    title: "Structure Summit",
    code: "DS-04",
    accent: "#b45309",
    soft: "#fff0df",
    glow: "#ffd19b",
    blurb: "Traverse lists, tuples, sets, and dictionaries like a prepared explorer.",
  },
  {
    title: "Object Observatory",
    code: "OO-05",
    accent: "#dc2626",
    soft: "#ffe4e4",
    glow: "#ffb0b0",
    blurb: "Learn how classes, methods, and inheritance line up into bigger systems.",
  },
  {
    title: "Hash Harbor",
    code: "HM-06",
    accent: "#0f766e",
    soft: "#dcfce7",
    glow: "#9fe7b5",
    blurb: "Dock with dictionaries, hashing, and collision rules that keep lookups fast.",
  },
  {
    title: "Generator Grove",
    code: "CG-07",
    accent: "#4f46e5",
    soft: "#e7e8ff",
    glow: "#b6b8ff",
    blurb: "Unlock compact comprehensions and lazy streams without losing clarity.",
  },
  {
    title: "Exception Expanse",
    code: "EH-08",
    accent: "#be123c",
    soft: "#ffe4ec",
    glow: "#ffb1c3",
    blurb: "Contain failures with precise exception handling and clean recovery paths.",
  },
  {
    title: "File Fjord",
    code: "FI-09",
    accent: "#0369a1",
    soft: "#e0f2fe",
    glow: "#9cd8f7",
    blurb: "Navigate files, JSON, CSV, and pathlib with safe open-close patterns.",
  },
  {
    title: "Decorator Dome",
    code: "DC-10",
    accent: "#9333ea",
    soft: "#f3e8ff",
    glow: "#ddb3ff",
    blurb: "Finish the journey with closures, wrappers, and higher-order Python magic.",
  },
];
const VALID_WORKSPACES = ["interview", "quest", "python"];
const INITIAL_ROUTE_STATE = readRouteState();

function normalizeWorkspace(value) {
  return VALID_WORKSPACES.includes(value) ? value : "interview";
}

function readRouteState() {
  if (typeof window === "undefined") {
    return { workspace: "interview", lessonSlug: "" };
  }

  const url = new URL(window.location.href);
  return {
    workspace: normalizeWorkspace(url.searchParams.get("workspace")),
    lessonSlug: (url.searchParams.get("lesson") || "").trim().toLowerCase(),
  };
}

function createEmptyQuestProgress() {
  return {
    completedLessons: {},
    quizWins: {},
    codeWins: {},
    recentLesson: "",
  };
}

function loadQuestProgress() {
  if (typeof window === "undefined") {
    return createEmptyQuestProgress();
  }

  try {
    const raw = window.localStorage.getItem(PYTHON_QUEST_STORAGE_KEY);
    return raw ? JSON.parse(raw) : createEmptyQuestProgress();
  } catch (_error) {
    return createEmptyQuestProgress();
  }
}

function normalizeQuestProgress(progress, lessons) {
  const base = createEmptyQuestProgress();
  const lessonSlugs = new Set((lessons || []).map((lesson) => lesson.slug));
  const coerceFlags = (source) =>
    Object.entries(source && typeof source === "object" ? source : {}).reduce((acc, [slug, value]) => {
      if (lessonSlugs.has(slug) && Boolean(value)) {
        acc[slug] = true;
      }
      return acc;
    }, {});

  return {
    completedLessons: coerceFlags(progress?.completedLessons),
    quizWins: coerceFlags(progress?.quizWins),
    codeWins: coerceFlags(progress?.codeWins),
    recentLesson: lessonSlugs.has(progress?.recentLesson) ? progress.recentLesson : "",
  };
}

function questRealmForIndex(index) {
  return PYTHON_QUEST_REALMS[index % PYTHON_QUEST_REALMS.length];
}

function questVisibleLearnCards(cards) {
  return (cards || [])
    .filter((card) => card && ["concept", "checkpoint", "code"].includes(card.kind))
    .slice(0, 6);
}

createApp({
  data() {
    return {
      loading: true,
      error: "",
      payload: null,
      searchText: "",
      activeSection: "all",
      activeWorkspace: INITIAL_ROUTE_STATE.workspace,
      openQuestionIds: {},
      pythonStatusChecked: false,
      pythonAvailable: false,
      pythonReason: "",
      pythonSessionId: "",
      pythonCursor: 0,
      pythonTerminalText: "",
      pythonInput: "",
      pythonBusy: false,
      pythonError: "",
      pythonPollTimer: null,
      pythonPollInFlight: false,
      pythonQuestRequestedLessonSlug: INITIAL_ROUTE_STATE.lessonSlug,
      pythonQuestLoading: false,
      pythonQuestError: "",
      pythonQuestLessonsData: [],
      pythonQuestValidationEnabled: false,
      pythonQuestValidationReason: "",
      pythonQuestSelectedLessonSlug: "",
      pythonQuestQuizSelections: {},
      pythonQuestQuizResults: {},
      pythonQuestCodeDrafts: {},
      pythonQuestCodeResults: {},
      pythonQuestSubmittingSlug: "",
      pythonQuestProgress: createEmptyQuestProgress(),
    };
  },
  computed: {
    heroContent() {
      if (this.activeWorkspace === "quest") {
        return {
          kicker: "Python Quest Academy",
          title: "Learn Python Through Boss Quizzes, Code Gates, and Unlockable Realms",
          copy:
            "Each realm is generated from the real lesson modules in this repo, so the game stays aligned with the curriculum you already maintain.",
          metrics: [
            { label: "Realms", value: this.pythonQuestLessons.length || 10 },
            { label: "Unlocked", value: this.questUnlockedLessonCount },
            { label: "XP Earned", value: this.questXp },
          ],
        };
      }

      if (this.activeWorkspace === "python") {
        return {
          kicker: "Python Interactive Lab",
          title: "Run the Existing Lesson CLI Inside the Browser",
          copy:
            "Use the original terminal-driven Python course directly from the app, with live session management and quick action controls.",
          metrics: [
            { label: "Lessons", value: 10 },
            { label: "CLI Access", value: this.pythonAvailable ? "Live" : "Local" },
            { label: "Session", value: this.pythonSessionId ? "Running" : "Ready" },
          ],
        };
      }

      return {
        kicker: "Vue + FastAPI Interview Studio",
        title: "Backend Interview Prep, Fully Expanded",
        copy:
          "Every question now includes a core answer, deep-dive notes, interview framing guidance, and internet-sourced illustrations captured with Playwright.",
        metrics: this.payload
          ? [
              { label: "Sections", value: this.payload.stats.section_count },
              { label: "Total Questions", value: this.payload.stats.question_count },
              { label: "Visible Right Now", value: this.questionCards.length },
            ]
          : [],
      };
    },
    sections() {
      return this.payload?.sections || [];
    },
    totalQuestions() {
      return this.payload?.stats?.question_count || 0;
    },
    questionCards() {
      const items = [];
      const search = this.searchText.trim().toLowerCase();

      this.sections.forEach((section) => {
        if (this.activeSection !== "all" && section.slug !== this.activeSection) {
          return;
        }

        section.questions.forEach((question) => {
          const blob = [
            section.name,
            question.question,
            question.core_answer,
            question.deep_dive,
            (question.notes || []).join(" "),
          ]
            .join(" ")
            .toLowerCase();

          if (search && !blob.includes(search)) {
            return;
          }

          items.push({
            ...question,
            sectionName: section.name,
            sectionSlug: section.slug,
            animation: this.buildAnimation(question, section.name),
          });
        });
      });

      return items;
    },
    visibleCountBySection() {
      const counts = {};
      this.sections.forEach((section) => {
        counts[section.slug] = 0;
      });

      this.questionCards.forEach((question) => {
        counts[question.sectionSlug] = (counts[question.sectionSlug] || 0) + 1;
      });

      return counts;
    },
    activeSectionTitle() {
      if (this.activeSection === "all") {
        return "All Sections";
      }
      const section = this.sections.find((item) => item.slug === this.activeSection);
      return section ? section.name : "All Sections";
    },
    pythonQuestLessons() {
      return this.pythonQuestLessonsData;
    },
    questCompletedLessonCount() {
      return this.pythonQuestLessons.reduce(
        (total, lesson) => total + (this.questLessonCompleted(lesson.slug) ? 1 : 0),
        0,
      );
    },
    questUnlockedLessonCount() {
      return this.pythonQuestLessons.reduce(
        (total, lesson, index) => total + (this.questLessonUnlocked(index) ? 1 : 0),
        0,
      );
    },
    questXp() {
      return this.pythonQuestLessons.reduce((total, lesson) => {
        const slug = lesson.slug;
        return (
          total +
          (this.pythonQuestProgress.quizWins[slug] ? 20 : 0) +
          (this.pythonQuestProgress.codeWins[slug] ? 30 : 0) +
          (this.pythonQuestProgress.completedLessons[slug] ? 25 : 0)
        );
      }, 0);
    },
    selectedQuestLessonIndex() {
      return this.pythonQuestLessons.findIndex(
        (lesson) => lesson.slug === this.pythonQuestSelectedLessonSlug,
      );
    },
    selectedQuestLesson() {
      return this.pythonQuestLessons[this.selectedQuestLessonIndex] || null;
    },
    selectedQuestLearnDeck() {
      return questVisibleLearnCards(this.selectedQuestLesson?.learn_cards || []);
    },
    selectedQuestQuizDeck() {
      return (this.selectedQuestLesson?.quiz || []).slice(0, 3);
    },
    selectedQuestChallenge() {
      return this.selectedQuestLesson?.practice?.[0] || null;
    },
    questProgressPercent() {
      if (!this.pythonQuestLessons.length) {
        return 0;
      }
      return Math.round((this.questCompletedLessonCount / this.pythonQuestLessons.length) * 100);
    },
    questNextObjective() {
      const lesson = this.selectedQuestLesson;
      if (!lesson) {
        return this.pythonQuestLoading
          ? "Assembling the lesson map from your Python modules..."
          : "Choose an unlocked realm to begin.";
      }

      if (!this.questQuizPassed(lesson.slug)) {
        return "Win the Boss Quiz to stabilize this realm.";
      }
      if (!this.questCodePassed(lesson.slug)) {
        return "Clear the Code Forge with runnable Python to unlock the next path.";
      }

      const nextLesson = this.pythonQuestLessons[this.selectedQuestLessonIndex + 1];
      if (nextLesson) {
        return `${nextLesson.realm.title} is the next unlock on the route.`;
      }
      return "All realms cleared. Use the CLI lab to keep practicing at full depth.";
    },
  },
  methods: {
    questionHash(value) {
      let hash = 0;
      const text = String(value || "");
      for (let index = 0; index < text.length; index += 1) {
        hash = (hash << 5) - hash + text.charCodeAt(index);
        hash |= 0;
      }
      return Math.abs(hash);
    },
    buildAnimation(question, sectionName) {
      const questionText = question?.question || "";
      const answerText = question?.core_answer || "";
      const matchedFromQuestion = ANIMATION_PATTERNS.find((pattern) =>
        pattern.test.test(questionText),
      );
      const matchedFromAnswer = matchedFromQuestion
        ? null
        : ANIMATION_PATTERNS.find((pattern) => pattern.test.test(answerText));
      const matched = matchedFromQuestion || matchedFromAnswer;
      const base = matched || SECTION_ANIMATION_DEFAULTS[sectionName] || ANIMATION_PATTERNS[0];
      const hash = this.questionHash(question?.id || `${questionText} ${answerText}`);
      const duration = 7 + (hash % 4);
      const packets = 2 + (hash % 3);
      return {
        kind: base.kind,
        description: base.description,
        steps: base.steps.slice(0, 5),
        duration,
        packets,
      };
    },
    getRefElement(name) {
      const item = this.$refs[name];
      if (!item) {
        return null;
      }
      return Array.isArray(item) ? item[0] : item;
    },
    destroySimulations() {
      if (!this._simulationControllers) {
        return;
      }
      Object.values(this._simulationControllers).forEach((controller) => {
        if (controller && typeof controller.destroy === "function") {
          controller.destroy();
        }
      });
      this._simulationControllers = {};
    },
    refreshSimulationVisibility() {
      if (!this._simulationControllers) {
        return;
      }
      Object.values(this._simulationControllers).forEach((controller) => {
        if (!controller || !controller.canvas || typeof controller.setActive !== "function") {
          return;
        }
        controller.setActive(isElementVisible(controller.canvas));
      });
    },
    syncSimulations() {
      if (this.activeWorkspace !== "interview") {
        this.destroySimulations();
        return;
      }

      if (!this._simulationControllers) {
        this._simulationControllers = {};
      }

      const openCards = this.questionCards.filter((item) => this.isOpen(item.id));
      const openIds = new Set(openCards.map((item) => item.id));

      Object.entries(this._simulationControllers).forEach(([questionId, controller]) => {
        if (openIds.has(questionId)) {
          return;
        }
        controller.destroy();
        delete this._simulationControllers[questionId];
      });

      openCards.forEach((item) => {
        const refName = `sim-${item.id}`;
        const canvas = this.getRefElement(refName);
        if (!canvas) {
          return;
        }

        const nextKind = item.animation?.kind || "load-balancing";
        const nextSeed = this.questionHash(item.id || item.question);
        const existing = this._simulationControllers[item.id];

        if (existing && existing.canvas === canvas && existing.kind === nextKind) {
          return;
        }

        if (existing) {
          existing.destroy();
          delete this._simulationControllers[item.id];
        }

        const controller = createConceptSimulation(canvas, {
          kind: nextKind,
          seed: nextSeed,
        });
        if (controller) {
          this._simulationControllers[item.id] = controller;
        }
      });

      this.refreshSimulationVisibility();
    },
    handleResize() {
      if (!this._simulationControllers) {
        return;
      }
      Object.values(this._simulationControllers).forEach((controller) => {
        if (controller && typeof controller.resize === "function") {
          controller.resize();
        }
      });
      this.refreshSimulationVisibility();
    },
    syncRouteState() {
      if (typeof window === "undefined") {
        return;
      }
      const url = new URL(window.location.href);
      if (this.activeWorkspace === "interview") {
        url.searchParams.delete("workspace");
      } else {
        url.searchParams.set("workspace", this.activeWorkspace);
      }

      if (this.activeWorkspace === "quest" && this.pythonQuestSelectedLessonSlug) {
        url.searchParams.set("lesson", this.pythonQuestSelectedLessonSlug);
      } else {
        url.searchParams.delete("lesson");
      }

      window.history.replaceState({}, "", url);
    },
    persistQuestProgress() {
      if (typeof window === "undefined") {
        return;
      }
      window.localStorage.setItem(
        PYTHON_QUEST_STORAGE_KEY,
        JSON.stringify(this.pythonQuestProgress),
      );
    },
    updateQuestProgress(mutator) {
      const next = {
        completedLessons: { ...this.pythonQuestProgress.completedLessons },
        quizWins: { ...this.pythonQuestProgress.quizWins },
        codeWins: { ...this.pythonQuestProgress.codeWins },
        recentLesson: this.pythonQuestProgress.recentLesson || "",
      };

      mutator(next);

      Object.keys({ ...next.quizWins, ...next.codeWins }).forEach((slug) => {
        if (next.quizWins[slug] && next.codeWins[slug]) {
          next.completedLessons[slug] = true;
        }
      });

      this.pythonQuestProgress = next;
      this.persistQuestProgress();
    },
    questRealmStyle(realm) {
      return {
        "--quest-accent": realm.accent,
        "--quest-soft": realm.soft,
        "--quest-glow": realm.glow,
      };
    },
    questLessonUnlocked(index) {
      if (index <= 0) {
        return true;
      }
      const previousLesson = this.pythonQuestLessons[index - 1];
      return previousLesson ? Boolean(this.pythonQuestProgress.completedLessons[previousLesson.slug]) : false;
    },
    questLessonCompleted(slug) {
      return Boolean(this.pythonQuestProgress.completedLessons[slug]);
    },
    questQuizPassed(slug) {
      return Boolean(this.pythonQuestProgress.quizWins[slug]);
    },
    questCodePassed(slug) {
      return Boolean(this.pythonQuestProgress.codeWins[slug]);
    },
    ensureQuestSelection() {
      if (!this.pythonQuestLessons.length) {
        return;
      }

      const trySelect = (slug) => {
        const index = this.pythonQuestLessons.findIndex((lesson) => lesson.slug === slug);
        if (index >= 0 && this.questLessonUnlocked(index)) {
          this.pythonQuestSelectedLessonSlug = slug;
          return true;
        }
        return false;
      };

      if (
        this.pythonQuestSelectedLessonSlug &&
        trySelect(this.pythonQuestSelectedLessonSlug)
      ) {
        this.syncRouteState();
        return;
      }

      if (this.pythonQuestRequestedLessonSlug && trySelect(this.pythonQuestRequestedLessonSlug)) {
        this.pythonQuestRequestedLessonSlug = "";
        this.syncRouteState();
        return;
      }

      if (this.pythonQuestProgress.recentLesson && trySelect(this.pythonQuestProgress.recentLesson)) {
        this.syncRouteState();
        return;
      }

      const fallback =
        this.pythonQuestLessons.find((_lesson, index) => this.questLessonUnlocked(index)) ||
        this.pythonQuestLessons[0];
      this.pythonQuestSelectedLessonSlug = fallback.slug;
      this.syncRouteState();
    },
    async fetchPythonQuestCatalog(force = false) {
      if (this.pythonQuestLessons.length && !force) {
        this.ensureQuestSelection();
        return;
      }

      this.pythonQuestLoading = true;
      this.pythonQuestError = "";

      try {
        const response = await fetch("/api/python-quest");
        if (!response.ok) {
          throw new Error(`Failed to load Python quest (${response.status})`);
        }
        const payload = await response.json();
        const lessons = (payload.lessons || []).map((lesson, index) => ({
          ...lesson,
          realm: questRealmForIndex(index),
        }));

        this.pythonQuestLessonsData = lessons;
        this.pythonQuestValidationEnabled = Boolean(payload.validation_enabled);
        this.pythonQuestValidationReason = payload.validation_reason || "";
        this.pythonQuestProgress = normalizeQuestProgress(loadQuestProgress(), lessons);

        const nextDrafts = { ...this.pythonQuestCodeDrafts };
        lessons.forEach((lesson) => {
          if (typeof nextDrafts[lesson.slug] === "string") {
            return;
          }
          nextDrafts[lesson.slug] = lesson.practice?.[0]?.starter_code || "";
        });
        this.pythonQuestCodeDrafts = nextDrafts;
        this.ensureQuestSelection();
      } catch (error) {
        this.pythonQuestError = error?.message || "Unable to load the Python quest";
      } finally {
        this.pythonQuestLoading = false;
      }
    },
    setWorkspace(value) {
      this.activeWorkspace = value;
      this.syncRouteState();
      if (value === "python") {
        this.fetchPythonStatus();
      }
      if (value === "quest") {
        this.fetchPythonQuestCatalog();
      }
    },
    selectQuestLesson(slug) {
      const index = this.pythonQuestLessons.findIndex((lesson) => lesson.slug === slug);
      if (index < 0 || !this.questLessonUnlocked(index)) {
        return;
      }

      this.pythonQuestSelectedLessonSlug = slug;
      this.updateQuestProgress((progress) => {
        progress.recentLesson = slug;
      });
      this.syncRouteState();
    },
    selectQuestAnswer(lessonSlug, questionIndex, optionIndex) {
      const nextSelections = {
        ...this.pythonQuestQuizSelections,
        [lessonSlug]: [...(this.pythonQuestQuizSelections[lessonSlug] || [])],
      };
      nextSelections[lessonSlug][questionIndex] = optionIndex;
      this.pythonQuestQuizSelections = nextSelections;

      if (this.pythonQuestQuizResults[lessonSlug]) {
        const nextResults = { ...this.pythonQuestQuizResults };
        delete nextResults[lessonSlug];
        this.pythonQuestQuizResults = nextResults;
      }
    },
    questOptionClass(lessonSlug, questionIndex, optionIndex, question) {
      const selected = this.pythonQuestQuizSelections[lessonSlug]?.[questionIndex] === optionIndex;
      const graded = this.pythonQuestQuizResults[lessonSlug];
      return {
        selected,
        correct: Boolean(graded) && question.answer === optionIndex,
        wrong: Boolean(graded) && selected && question.answer !== optionIndex,
      };
    },
    submitQuestQuiz(lesson) {
      const quizDeck = (lesson?.quiz || []).slice(0, 3);
      if (!quizDeck.length) {
        return;
      }

      const answers = this.pythonQuestQuizSelections[lesson.slug] || [];
      const correct = quizDeck.reduce(
        (total, question, index) => total + (answers[index] === question.answer ? 1 : 0),
        0,
      );
      const passed = correct >= Math.max(2, Math.ceil(quizDeck.length * 0.66));

      this.pythonQuestQuizResults = {
        ...this.pythonQuestQuizResults,
        [lesson.slug]: {
          total: quizDeck.length,
          correct,
          passed,
        },
      };

      this.updateQuestProgress((progress) => {
        progress.quizWins[lesson.slug] = progress.quizWins[lesson.slug] || passed;
        progress.recentLesson = lesson.slug;
      });
    },
    prefillQuestStarter(lesson) {
      const starter = lesson?.practice?.[0]?.starter_code || "# Solve the challenge here";
      this.pythonQuestCodeDrafts = {
        ...this.pythonQuestCodeDrafts,
        [lesson.slug]: starter,
      };
    },
    async submitQuestCode(lesson) {
      const challenge = lesson?.practice?.[0];
      if (!challenge) {
        return;
      }

      if (!this.pythonQuestValidationEnabled) {
        this.pythonQuestCodeResults = {
          ...this.pythonQuestCodeResults,
          [lesson.slug]: {
            ok: false,
            message:
              this.pythonQuestValidationReason ||
              "Code validation is unavailable from this client right now.",
            hint: challenge.hint,
            stdout: "",
          },
        };
        return;
      }

      const code = (this.pythonQuestCodeDrafts[lesson.slug] || "").trimEnd();
      if (!code.trim()) {
        this.pythonQuestCodeResults = {
          ...this.pythonQuestCodeResults,
          [lesson.slug]: {
            ok: false,
            message: "Write a solution before running the challenge.",
            hint: challenge.hint,
            stdout: "",
          },
        };
        return;
      }

      this.pythonQuestSubmittingSlug = lesson.slug;
      try {
        const response = await fetch("/api/python-quest/validate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            lesson_slug: lesson.slug,
            challenge_index: challenge.index,
            code,
          }),
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload?.detail || `Quest validation failed (${response.status})`);
        }

        this.pythonQuestCodeResults = {
          ...this.pythonQuestCodeResults,
          [lesson.slug]: payload,
        };

        this.updateQuestProgress((progress) => {
          progress.codeWins[lesson.slug] = progress.codeWins[lesson.slug] || Boolean(payload.ok);
          progress.recentLesson = lesson.slug;
        });
      } catch (error) {
        this.pythonQuestCodeResults = {
          ...this.pythonQuestCodeResults,
          [lesson.slug]: {
            ok: false,
            message: error?.message || "Unable to validate challenge",
            hint: challenge.hint,
            stdout: "",
          },
        };
      } finally {
        this.pythonQuestSubmittingSlug = "";
      }
    },
    async fetchPythonStatus(force = false) {
      if (this.pythonStatusChecked && !force) {
        return;
      }
      try {
        const response = await fetch("/api/python-cli/status");
        if (!response.ok) {
          throw new Error(`Failed to read Python lab status (${response.status})`);
        }
        const payload = await response.json();
        this.pythonAvailable = Boolean(payload.available && payload.module_exists);
        this.pythonReason = payload.reason || "";
      } catch (error) {
        this.pythonAvailable = false;
        this.pythonReason = error?.message || "Python lab status unavailable";
      } finally {
        this.pythonStatusChecked = true;
      }
    },
    startPythonPolling() {
      if (this.pythonPollTimer) {
        return;
      }
      this.pythonPollTimer = window.setInterval(() => {
        this.pollPythonOutput();
      }, 700);
    },
    stopPythonPolling() {
      if (!this.pythonPollTimer) {
        return;
      }
      window.clearInterval(this.pythonPollTimer);
      this.pythonPollTimer = null;
    },
    scrollPythonTerminal() {
      const terminal = this.$refs.pythonTerminal;
      if (!terminal) {
        return;
      }
      terminal.scrollTop = terminal.scrollHeight;
    },
    markPythonSessionClosed(reason = "") {
      this.stopPythonPolling();
      this.pythonSessionId = "";
      this.pythonCursor = 0;
      if (reason) {
        this.pythonError = reason;
      }
      if (!this.pythonTerminalText.endsWith("\n[session closed]\n")) {
        this.pythonTerminalText += "\n[session closed]\n";
        this.$nextTick(() => this.scrollPythonTerminal());
      }
    },
    async startPythonSession() {
      if (this.pythonSessionId) {
        return;
      }
      await this.fetchPythonStatus();
      if (!this.pythonAvailable) {
        this.pythonError = this.pythonReason || "Python CLI is unavailable";
        return;
      }

      this.pythonBusy = true;
      this.pythonError = "";
      this.pythonTerminalText = "";
      this.pythonCursor = 0;

      try {
        const response = await fetch("/api/python-cli/sessions", { method: "POST" });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload?.detail || `Failed to start Python session (${response.status})`);
        }
        this.pythonSessionId = payload.session_id;
        this.pythonCursor = payload.cursor || 0;
        this.pythonTerminalText = payload.output || "";
        this.startPythonPolling();
        this.$nextTick(() => this.scrollPythonTerminal());
      } catch (error) {
        this.pythonError = error?.message || "Unable to start Python session";
      } finally {
        this.pythonBusy = false;
      }
    },
    async pollPythonOutput() {
      if (!this.pythonSessionId || this.pythonPollInFlight) {
        return;
      }

      this.pythonPollInFlight = true;
      try {
        const response = await fetch(
          `/api/python-cli/sessions/${this.pythonSessionId}/output?cursor=${this.pythonCursor}`,
        );
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload?.detail || `Output polling failed (${response.status})`);
        }

        if (payload.output) {
          this.pythonTerminalText += payload.output;
          this.$nextTick(() => this.scrollPythonTerminal());
        }
        this.pythonCursor = payload.cursor || this.pythonCursor;

        if (!payload.alive) {
          this.markPythonSessionClosed("Python session ended. Start a new session to continue.");
        }
      } catch (error) {
        if (String(error?.message || "").toLowerCase().includes("not found")) {
          this.markPythonSessionClosed("Python CLI session not found. Start a new session.");
          return;
        }
        this.pythonError = error?.message || "Python output polling failed";
        this.stopPythonPolling();
      } finally {
        this.pythonPollInFlight = false;
      }
    },
    async sendPythonInput(overrideText = null) {
      if (!this.pythonSessionId) {
        return;
      }
      const text =
        overrideText === null || typeof overrideText === "object"
          ? this.pythonInput
          : String(overrideText);

      this.pythonTerminalText += text === "" ? "\n" : `${text}\n`;
      if (overrideText === null || typeof overrideText === "object") {
        this.pythonInput = "";
      }
      this.$nextTick(() => this.scrollPythonTerminal());

      try {
        const response = await fetch(`/api/python-cli/sessions/${this.pythonSessionId}/input`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload?.detail || `Failed to send input (${response.status})`);
        }
      } catch (error) {
        if (String(error?.message || "").toLowerCase().includes("not found")) {
          this.markPythonSessionClosed("Python CLI session not found. Start a new session.");
          return;
        }
        this.pythonError = error?.message || "Failed to send Python input";
      }
    },
    async stopPythonSession(quiet = false) {
      this.stopPythonPolling();
      const sessionId = this.pythonSessionId;
      this.pythonSessionId = "";
      this.pythonCursor = 0;

      if (!sessionId) {
        return;
      }

      try {
        await fetch(`/api/python-cli/sessions/${sessionId}`, { method: "DELETE" });
      } catch (error) {
        this.pythonError = error?.message || "Failed to close Python session";
      }

      if (!quiet) {
        this.pythonTerminalText += "\n[session closed]\n";
        this.$nextTick(() => this.scrollPythonTerminal());
      }
    },
    async fetchPayload() {
      try {
        this.loading = true;
        this.error = "";
        const response = await fetch("/api/sections");
        if (!response.ok) {
          throw new Error(`Failed to fetch content (${response.status})`);
        }
        this.payload = await response.json();
      } catch (error) {
        this.error = error?.message || "Unable to load interview content";
      } finally {
        this.loading = false;
      }
    },
    setSection(slug) {
      this.activeSection = slug;
    },
    isOpen(questionId) {
      return Boolean(this.openQuestionIds[questionId]);
    },
    toggleQuestion(questionId) {
      this.openQuestionIds = {
        ...this.openQuestionIds,
        [questionId]: !this.openQuestionIds[questionId],
      };
    },
    openAllVisible() {
      const nextState = { ...this.openQuestionIds };
      this.questionCards.forEach((question) => {
        nextState[question.id] = true;
      });
      this.openQuestionIds = nextState;
    },
    closeAllVisible() {
      const nextState = { ...this.openQuestionIds };
      this.questionCards.forEach((question) => {
        nextState[question.id] = false;
      });
      this.openQuestionIds = nextState;
    },
  },
  async mounted() {
    this._simulationControllers = {};
    window.addEventListener("resize", this.handleResize);
    window.addEventListener("scroll", this.refreshSimulationVisibility);
    await this.fetchPayload();
    if (this.activeWorkspace === "python") {
      this.fetchPythonStatus();
    }
    if (this.activeWorkspace === "quest") {
      this.fetchPythonQuestCatalog();
    }
    this.syncRouteState();
    this.syncSimulations();
  },
  updated() {
    this.syncSimulations();
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.handleResize);
    window.removeEventListener("scroll", this.refreshSimulationVisibility);
    this.stopPythonPolling();
    this.stopPythonSession(true);
    this.destroySimulations();
  },
  template: `
    <div class="page-shell">
      <div class="bg-orb bg-orb-1" aria-hidden="true"></div>
      <div class="bg-orb bg-orb-2" aria-hidden="true"></div>

      <header class="hero">
        <p class="kicker">{{ heroContent.kicker }}</p>
        <h1>{{ heroContent.title }}</h1>
        <p class="hero-copy">{{ heroContent.copy }}</p>

        <div class="hero-metrics" v-if="heroContent.metrics && heroContent.metrics.length">
          <article class="metric-card" v-for="metric in heroContent.metrics" :key="metric.label">
            <h2>{{ metric.value }}</h2>
            <p>{{ metric.label }}</p>
          </article>
        </div>
      </header>

      <main class="content" v-if="!loading && !error">
        <section class="workspace-switcher">
          <button
            class="workspace-tab"
            :class="{ active: activeWorkspace === 'interview' }"
            @click="setWorkspace('interview')"
          >
            Interview Prep Studio
          </button>
          <button
            class="workspace-tab"
            :class="{ active: activeWorkspace === 'quest' }"
            @click="setWorkspace('quest')"
          >
            Python Quest Academy
          </button>
          <button
            class="workspace-tab"
            :class="{ active: activeWorkspace === 'python' }"
            @click="setWorkspace('python')"
          >
            Python Interactive Lab
          </button>
        </section>

        <template v-if="activeWorkspace === 'interview'">
        <section class="control-panel">
          <label class="search-label" for="search">Search Questions</label>
          <input
            id="search"
            class="search-input"
            type="search"
            v-model="searchText"
            placeholder="Try: kafka ordering, redis replication, wildcard query"
          />

          <div class="section-row">
            <button
              class="section-pill"
              :class="{ active: activeSection === 'all' }"
              @click="setSection('all')"
            >
              All
              <span>{{ questionCards.length }}</span>
            </button>

            <button
              v-for="section in sections"
              :key="section.slug"
              class="section-pill"
              :class="{ active: activeSection === section.slug }"
              @click="setSection(section.slug)"
            >
              {{ section.name }}
              <span>{{ visibleCountBySection[section.slug] || 0 }}</span>
            </button>
          </div>

          <div class="toolbar">
            <p class="toolbar-summary">
              Showing <strong>{{ questionCards.length }}</strong> question(s) from
              <strong>{{ activeSectionTitle }}</strong>
            </p>
            <div class="toolbar-actions">
              <button class="ghost-btn" @click="openAllVisible">Open Visible</button>
              <button class="ghost-btn" @click="closeAllVisible">Close Visible</button>
            </div>
          </div>
        </section>

        <section class="question-grid" v-if="questionCards.length">
          <article
            class="question-card"
            v-for="(item, index) in questionCards"
            :key="item.id"
            :class="{ open: isOpen(item.id) }"
            :style="{ '--stagger': (index % 12) * 45 + 'ms' }"
          >
            <button class="question-head" @click="toggleQuestion(item.id)">
              <div class="question-head-main">
                <p class="section-tag">{{ item.sectionName }}</p>
                <h3>{{ item.question }}</h3>
              </div>
              <div class="question-chevron">▾</div>
            </button>

            <div class="question-body" v-if="isOpen(item.id)">
              <div class="answer-block">
                <h4>Core Answer</h4>
                <p>{{ item.core_answer }}</p>
              </div>

              <div class="answer-block">
                <h4>Deep Dive</h4>
                <p>{{ item.deep_dive }}</p>
              </div>

              <div class="answer-block" v-if="item.notes && item.notes.length">
                <h4>Interview Notes</h4>
                <ul class="notes-list">
                  <li v-for="(note, noteIndex) in item.notes" :key="noteIndex">{{ note }}</li>
                </ul>
              </div>

              <div class="answer-block" v-if="item.ascii_diagram">
                <h4>Quick Diagram</h4>
                <pre class="ascii-diagram">{{ item.ascii_diagram }}</pre>
              </div>

              <div class="answer-block" v-if="item.animation && item.animation.steps && item.animation.steps.length">
                <h4>Animated Concept Walkthrough</h4>
                <div
                  class="concept-animation"
                  :class="'concept-animation-' + item.animation.kind"
                  :style="{ '--flow-duration': item.animation.duration + 's' }"
                >
                  <div class="concept-rail">
                    <span
                      class="concept-packet"
                      v-for="packetIndex in item.animation.packets"
                      :key="item.id + '-pkt-' + packetIndex"
                      :style="{ '--packet-delay': ((packetIndex - 1) * 1.15) + 's' }"
                    ></span>
                  </div>

                  <div class="concept-steps">
                    <div
                      class="concept-step"
                      v-for="(step, stepIndex) in item.animation.steps"
                      :key="item.id + '-step-' + stepIndex"
                      :style="{ animationDelay: ((stepIndex * item.animation.duration) / item.animation.steps.length).toFixed(2) + 's' }"
                    >
                      <div class="concept-step-num">{{ stepIndex + 1 }}</div>
                      <div class="concept-step-copy">{{ step }}</div>
                    </div>
                  </div>
                </div>
                <p class="concept-note">{{ item.animation.description }}</p>
              </div>

              <div class="answer-block" v-if="item.animation">
                <h4>Interactive Concept Simulation</h4>
                <div class="simulation-shell" :class="'simulation-shell-' + item.animation.kind">
                  <canvas
                    class="concept-canvas"
                    :ref="'sim-' + item.id"
                    width="960"
                    height="280"
                    :aria-label="'Concept simulation for ' + item.question"
                  ></canvas>
                </div>
                <p class="concept-note">
                  Live flow model for this question: packet routing, stage progression, and feedback loops.
                </p>
              </div>

              <div class="answer-block" v-if="item.illustrations && item.illustrations.length">
                <h4>Internet Illustrations</h4>
                <div class="illustration-grid">
                  <figure
                    class="illustration-card"
                    v-for="(image, imageIndex) in item.illustrations"
                    :key="item.id + '-img-' + imageIndex"
                  >
                    <img :src="image.image_path" :alt="image.source_title" loading="lazy" />
                    <figcaption>
                      <span>{{ image.caption }}</span>
                      <small v-if="image.source_title">{{ image.source_title }}</small>
                      <a
                        v-if="image.source_url"
                        :href="image.source_url"
                        target="_blank"
                        rel="noopener"
                      >Source</a>
                    </figcaption>
                  </figure>
                </div>
              </div>

              <div class="answer-block" v-if="item.references && item.references.length">
                <h4>References</h4>
                <div class="reference-list">
                  <a
                    v-for="(reference, refIndex) in item.references"
                    :key="item.id + '-ref-' + refIndex"
                    :href="reference.url"
                    target="_blank"
                    rel="noopener"
                  >
                    {{ reference.title }}
                  </a>
                </div>
              </div>
            </div>
          </article>
        </section>

        <section class="empty-state" v-else>
          <h3>No questions match this filter</h3>
          <p>Try clearing search text or switching sections.</p>
        </section>
        </template>

        <section class="quest-lab" v-else-if="activeWorkspace === 'quest'">
          <div class="quest-overview">
            <div class="quest-overview-copy">
              <p class="quest-kicker">Curriculum-driven browser game mode</p>
              <h2>Travel through ten Python realms without leaving the site</h2>
              <p>
                Each realm pulls from your lesson modules, then turns the material into quick
                learn cards, a boss quiz, and a code gate that can validate real Python locally.
              </p>
              <div class="quest-progress-meta">
                <div class="quest-progress-bar">
                  <span :style="{ width: questProgressPercent + '%' }"></span>
                </div>
                <small>{{ questCompletedLessonCount }} / {{ pythonQuestLessons.length || 10 }} realms cleared</small>
              </div>
            </div>

            <aside class="quest-journal">
              <p class="quest-journal-label">Current Objective</p>
              <h3>{{ selectedQuestLesson ? selectedQuestLesson.realm.title : 'Summoning lesson map' }}</h3>
              <p>
                {{ selectedQuestLesson ? selectedQuestLesson.realm.blurb : 'Pulling the lesson content into quest format now.' }}
              </p>
              <small>{{ questNextObjective }}</small>
            </aside>
          </div>

          <div class="python-lab-status">
            <span class="status-chip" :class="{ active: pythonQuestValidationEnabled }">
              {{ pythonQuestValidationEnabled ? "Code Forge Ready" : "Code Forge Local Only" }}
            </span>
            <small v-if="pythonQuestValidationReason">{{ pythonQuestValidationReason }}</small>
          </div>

          <section class="state-block" v-if="pythonQuestLoading">
            <p>Assembling the Python realms from your lesson modules...</p>
          </section>

          <p class="python-error" v-else-if="pythonQuestError">{{ pythonQuestError }}</p>

          <div class="quest-layout" v-else-if="pythonQuestLessons.length">
            <section class="quest-map">
              <button
                v-for="(lesson, index) in pythonQuestLessons"
                :key="lesson.slug"
                class="quest-node"
                :class="{
                  locked: !questLessonUnlocked(index),
                  selected: pythonQuestSelectedLessonSlug === lesson.slug,
                  complete: questLessonCompleted(lesson.slug),
                }"
                :style="questRealmStyle(lesson.realm)"
                @click="selectQuestLesson(lesson.slug)"
              >
                <div class="quest-node-top">
                  <span class="quest-node-code">{{ lesson.realm.code }}</span>
                  <span class="quest-node-badge">
                    {{ questLessonCompleted(lesson.slug) ? "Cleared" : (questLessonUnlocked(index) ? "Open" : "Locked") }}
                  </span>
                </div>
                <h3>{{ lesson.realm.title }}</h3>
                <p>{{ lesson.title }}</p>
                <small>{{ lesson.summary }}</small>
              </button>
            </section>

            <section class="quest-panel" v-if="selectedQuestLesson">
              <div class="quest-panel-hero" :style="questRealmStyle(selectedQuestLesson.realm)">
                <div>
                  <p class="quest-realm-code">
                    {{ selectedQuestLesson.realm.code }} · {{ selectedQuestLesson.title }}
                  </p>
                  <h3>{{ selectedQuestLesson.realm.title }}</h3>
                  <p>{{ selectedQuestLesson.realm.blurb }}</p>
                </div>

                <div class="quest-status-strip">
                  <span class="quest-status-pill" :class="{ done: questQuizPassed(selectedQuestLesson.slug) }">Boss Quiz</span>
                  <span class="quest-status-pill" :class="{ done: questCodePassed(selectedQuestLesson.slug) }">Code Forge</span>
                  <span class="quest-status-pill" :class="{ done: questLessonCompleted(selectedQuestLesson.slug) }">Realm Clear</span>
                </div>
              </div>

              <section class="quest-module">
                <div class="quest-module-head">
                  <div>
                    <p class="section-tag">Scout Notes</p>
                    <h3>Study the lesson before you engage the boss.</h3>
                  </div>
                </div>

                <div class="quest-learn-grid">
                  <article
                    class="quest-learn-card"
                    :class="'kind-' + card.kind"
                    v-for="(card, cardIndex) in selectedQuestLearnDeck"
                    :key="selectedQuestLesson.slug + '-learn-' + cardIndex"
                  >
                    <template v-if="card.kind === 'code'">
                      <p class="quest-learn-kicker">Code Pattern {{ cardIndex + 1 }}</p>
                      <pre class="quest-snippet">{{ card.code }}</pre>
                      <p class="quest-output-label">Output</p>
                      <pre class="quest-snippet">{{ card.output }}</pre>
                    </template>

                    <template v-else-if="card.kind === 'checkpoint'">
                      <p class="quest-learn-kicker">Checkpoint</p>
                      <h4>{{ card.title }}</h4>
                      <p>Use this station to frame the next mechanic in the lesson.</p>
                    </template>

                    <template v-else>
                      <p class="quest-learn-kicker">Concept</p>
                      <h4>{{ card.title }}</h4>
                      <p>{{ card.body }}</p>
                    </template>
                  </article>
                </div>
              </section>

              <section class="quest-module">
                <div class="quest-module-head">
                  <div>
                    <p class="section-tag">Boss Quiz</p>
                    <h3>Defend the realm with fast concept checks.</h3>
                  </div>
                  <button class="ghost-btn" @click="submitQuestQuiz(selectedQuestLesson)">
                    Resolve Boss Battle
                  </button>
                </div>

                <div class="quest-quiz-stack">
                  <article
                    class="quest-question-card"
                    v-for="(question, questionIndex) in selectedQuestQuizDeck"
                    :key="selectedQuestLesson.slug + '-quiz-' + questionIndex"
                  >
                    <p class="quest-learn-kicker">Encounter {{ questionIndex + 1 }}</p>
                    <h4>{{ question.question }}</h4>

                    <div class="quest-option-list">
                      <button
                        v-for="(option, optionIndex) in question.options"
                        :key="selectedQuestLesson.slug + '-option-' + questionIndex + '-' + optionIndex"
                        class="quest-option"
                        :class="questOptionClass(selectedQuestLesson.slug, questionIndex, optionIndex, question)"
                        @click="selectQuestAnswer(selectedQuestLesson.slug, questionIndex, optionIndex)"
                      >
                        {{ option }}
                      </button>
                    </div>

                    <p class="quest-explanation" v-if="pythonQuestQuizResults[selectedQuestLesson.slug]">
                      {{ question.explanation }}
                    </p>
                  </article>
                </div>

                <p
                  class="quest-result"
                  v-if="pythonQuestQuizResults[selectedQuestLesson.slug]"
                  :class="{
                    success: pythonQuestQuizResults[selectedQuestLesson.slug].passed,
                    fail: !pythonQuestQuizResults[selectedQuestLesson.slug].passed,
                  }"
                >
                  {{ pythonQuestQuizResults[selectedQuestLesson.slug].passed ? "Boss defeated." : "The boss is still standing." }}
                  Score: {{ pythonQuestQuizResults[selectedQuestLesson.slug].correct }}/{{ pythonQuestQuizResults[selectedQuestLesson.slug].total }}.
                </p>
              </section>

              <section class="quest-module">
                <div class="quest-module-head">
                  <div>
                    <p class="section-tag">Code Forge</p>
                    <h3>Write live Python to unlock the next route.</h3>
                  </div>

                  <div class="toolbar-actions">
                    <button class="ghost-btn" @click="prefillQuestStarter(selectedQuestLesson)">
                      Load Starter
                    </button>
                    <button class="ghost-btn" @click="setWorkspace('python')">
                      Open CLI Lab
                    </button>
                    <button
                      class="ghost-btn"
                      :disabled="pythonQuestSubmittingSlug === selectedQuestLesson.slug || !selectedQuestChallenge"
                      @click="submitQuestCode(selectedQuestLesson)"
                    >
                      {{ pythonQuestSubmittingSlug === selectedQuestLesson.slug ? "Running..." : "Run Challenge" }}
                    </button>
                  </div>
                </div>

                <div class="quest-code-panel" v-if="selectedQuestChallenge">
                  <p class="quest-prompt">{{ selectedQuestChallenge.prompt }}</p>
                  <p class="quest-hint">Hint: {{ selectedQuestChallenge.hint }}</p>

                  <textarea
                    class="quest-editor"
                    v-model="pythonQuestCodeDrafts[selectedQuestLesson.slug]"
                    spellcheck="false"
                    :placeholder="selectedQuestChallenge.starter_code || '# Solve the challenge here'"
                  ></textarea>

                  <p class="quest-callout" v-if="!pythonQuestValidationEnabled">
                    Code validation stays local-only by default for safety. The mission text still lines up with the browser CLI lab.
                  </p>

                  <p
                    class="quest-result"
                    v-if="pythonQuestCodeResults[selectedQuestLesson.slug]"
                    :class="{
                      success: pythonQuestCodeResults[selectedQuestLesson.slug].ok,
                      fail: !pythonQuestCodeResults[selectedQuestLesson.slug].ok,
                    }"
                  >
                    {{ pythonQuestCodeResults[selectedQuestLesson.slug].message }}
                  </p>

                  <pre
                    class="quest-stdout"
                    v-if="pythonQuestCodeResults[selectedQuestLesson.slug] && pythonQuestCodeResults[selectedQuestLesson.slug].stdout"
                  >{{ pythonQuestCodeResults[selectedQuestLesson.slug].stdout }}</pre>
                </div>
              </section>
            </section>
          </div>
        </section>

        <section class="python-lab" v-else>
          <h2>Python Interactive Learning</h2>
          <p>
            This runs your existing <code>python/run.py</code> lesson CLI inside the app.
            Pick a lesson and mode exactly like terminal usage.
          </p>

          <div class="python-lab-status">
            <span class="status-chip" :class="{ active: pythonAvailable }">
              {{ pythonAvailable ? "CLI Available" : "CLI Restricted" }}
            </span>
            <small v-if="pythonReason">{{ pythonReason }}</small>
          </div>

          <div class="python-controls">
            <button class="ghost-btn" @click="fetchPythonStatus(true)">Refresh Status</button>
            <button class="ghost-btn" :disabled="pythonBusy || pythonSessionId || !pythonAvailable" @click="startPythonSession">
              Start Session
            </button>
            <button class="ghost-btn" :disabled="!pythonSessionId" @click="stopPythonSession()">
              Stop Session
            </button>
          </div>

          <pre class="python-terminal" ref="pythonTerminal">{{ pythonTerminalText || "Start a session to begin interactive Python learning..." }}</pre>

          <form class="python-input-row" @submit.prevent="sendPythonInput()">
            <input
              class="search-input"
              type="text"
              v-model="pythonInput"
              :disabled="!pythonSessionId"
              placeholder="Type input (example: 1, L, P, Q, B, q) and press Enter"
            />
            <button class="ghost-btn" type="submit" :disabled="!pythonSessionId">
              Send
            </button>
          </form>
          <div class="python-quick-actions">
            <button class="ghost-btn" :disabled="!pythonSessionId" @click="sendPythonInput('')">Enter</button>
            <button class="ghost-btn" :disabled="!pythonSessionId" @click="sendPythonInput('B')">Back</button>
            <button class="ghost-btn" :disabled="!pythonSessionId" @click="sendPythonInput('L')">Learn</button>
            <button class="ghost-btn" :disabled="!pythonSessionId" @click="sendPythonInput('P')">Practice</button>
            <button class="ghost-btn" :disabled="!pythonSessionId" @click="sendPythonInput('Q')">Quiz</button>
            <button class="ghost-btn" :disabled="!pythonSessionId" @click="sendPythonInput('q')">Quit</button>
          </div>

          <p class="python-error" v-if="pythonError">{{ pythonError }}</p>
        </section>
      </main>

      <section class="state-block" v-if="loading">
        <p>Loading your interview knowledge base...</p>
      </section>

      <section class="state-block error" v-if="error">
        <p>{{ error }}</p>
      </section>
    </div>
  `,
}).mount("#app");
