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

createApp({
  data() {
    return {
      loading: true,
      error: "",
      payload: null,
      searchText: "",
      activeSection: "all",
      openQuestionIds: {},
    };
  },
  computed: {
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
    this.syncSimulations();
  },
  updated() {
    this.syncSimulations();
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.handleResize);
    window.removeEventListener("scroll", this.refreshSimulationVisibility);
    this.destroySimulations();
  },
  template: `
    <div class="page-shell">
      <div class="bg-orb bg-orb-1" aria-hidden="true"></div>
      <div class="bg-orb bg-orb-2" aria-hidden="true"></div>

      <header class="hero">
        <p class="kicker">Vue + FastAPI Interview Studio</p>
        <h1>Backend Interview Prep, Fully Expanded</h1>
        <p class="hero-copy">
          Every question now includes a core answer, deep-dive notes, interview framing guidance,
          and internet-sourced illustrations captured with Playwright.
        </p>

        <div class="hero-metrics" v-if="payload">
          <article class="metric-card">
            <h2>{{ payload.stats.section_count }}</h2>
            <p>Sections</p>
          </article>
          <article class="metric-card">
            <h2>{{ payload.stats.question_count }}</h2>
            <p>Total Questions</p>
          </article>
          <article class="metric-card">
            <h2>{{ questionCards.length }}</h2>
            <p>Visible Right Now</p>
          </article>
        </div>
      </header>

      <main class="content" v-if="!loading && !error">
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
