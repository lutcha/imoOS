import { useState } from "react";

const agents = [
  {
    id: "tenant-expert",
    category: "Architecture",
    categoryId: "00",
    icon: "🏗️",
    name: "tenant-expert",
    tagline: "Multi-tenant architecture specialist",
    model: "sonnet",
    tools: ["Read", "Grep", "Glob", "Bash"],
    memory: true,
    description:
      "Reviews all code involving django-tenants, schema isolation, and cross-tenant operations. Use proactively on every PR.",
    checklist: [
      "Model is in TENANT_APPS, not SHARED_APPS",
      "View has IsTenantMember permission",
      "Celery task uses tenant_context()",
      "S3 uploads prefixed with tenant slug",
    ],
    trigger: "Any multi-tenant code review",
    badge: "critical",
  },
  {
    id: "django-tenants-specialist",
    category: "Architecture",
    categoryId: "00",
    icon: "🗄️",
    name: "django-tenants-specialist",
    tagline: "Migrations & schema management",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    memory: false,
    description:
      "Handles SHARED_APPS vs TENANT_APPS config, schema creation/deletion, migration strategies, and tenant lifecycle.",
    checklist: [
      "NEVER run DROP SCHEMA without confirmation",
      "ALWAYS backup before destructive ops",
      "Test migrations on staging first",
      "Log all schema operations for audit",
    ],
    trigger: "Migrations, schema management",
    badge: "core",
  },
  {
    id: "schema-isolation-auditor",
    category: "Architecture",
    categoryId: "00",
    icon: "🔐",
    name: "schema-isolation-auditor",
    tagline: "Pre-merge security auditor",
    model: "sonnet",
    tools: ["Read", "Grep", "Glob", "Bash"],
    memory: true,
    permissionMode: "plan",
    description:
      "Prevents the most critical SaaS bug: Company A seeing Company B's data. Run before every merge to main.",
    checklist: [
      "No raw SQL bypassing ORM",
      "All APIs have IsTenantMember",
      "Redis/cache keys tenant-prefixed",
      "S3 paths include tenant slug",
    ],
    trigger: "Pre-merge security check",
    badge: "critical",
  },
  {
    id: "drf-viewset-builder",
    category: "Backend",
    categoryId: "01",
    icon: "⚙️",
    name: "drf-viewset-builder",
    tagline: "Generate DRF ViewSets with tenant isolation",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob"],
    memory: false,
    description:
      "Generates complete DRF ViewSets with permissions, filters, pagination, serializers, and isolation tests.",
    checklist: [
      "No __all__ in serializer fields",
      "IsTenantMember permission present",
      "Sensitive fields are read_only",
      "FK validated against tenant scope",
    ],
    trigger: "Generate API endpoints",
    badge: "core",
  },
  {
    id: "model-architect",
    category: "Backend",
    categoryId: "01",
    icon: "📐",
    name: "model-architect",
    tagline: "Design Django models with audit history",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob", "Grep"],
    memory: false,
    description:
      "Designs business models with HistoricalRecords, Cabo Verde context (CVE, +238, islands), and proper relationships.",
    checklist: [
      "Model in TENANT_APPS (no tenant_id FK)",
      "HistoricalRecords() on all models",
      "CVE currency + Cape Verde timezone",
      "PROTECT for critical FK relations",
    ],
    trigger: "Design new models",
    badge: "core",
  },
  {
    id: "celery-task-specialist",
    category: "Backend",
    categoryId: "01",
    icon: "🔄",
    name: "celery-task-specialist",
    tagline: "Safe Celery tasks for multi-tenant",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob", "Grep"],
    memory: false,
    description:
      "Creates tenant-safe Celery tasks with correct tenant_context() wrapping, exponential backoff, and idempotency.",
    checklist: [
      "Pass primitive IDs, never instances",
      "Use tenant_context() wrapper",
      "Exponential backoff retry logic",
      "Tasks are idempotent (safe to retry)",
    ],
    trigger: "Background tasks",
    badge: "core",
  },
  {
    id: "nextjs-tenant-routing",
    category: "Frontend",
    categoryId: "02",
    icon: "🌐",
    name: "nextjs-tenant-routing",
    tagline: "Tenant-aware Next.js routing & auth",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob", "Grep"],
    memory: false,
    description:
      "Implements subdomain detection, JWT tenant extraction, API header injection, and middleware routing for Next.js.",
    checklist: [
      "Tenant from JWT, not just URL",
      "API calls include X-Tenant-Schema",
      "403 triggers redirect to correct tenant",
      "No hardcoded tenant values",
    ],
    trigger: "Frontend tenant handling",
    badge: "core",
  },
  {
    id: "react-component-builder",
    category: "Frontend",
    categoryId: "02",
    icon: "⚛️",
    name: "react-component-builder",
    tagline: "TypeScript + Tailwind components",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob"],
    memory: false,
    description:
      "Generates React components with TypeScript, Tailwind design tokens, React Query with tenant cache keys, and offline support.",
    checklist: [
      "Strict TypeScript (no implicit any)",
      "Tenant in React Query key",
      "Loading/error/empty states",
      "Offline queue for mutations",
    ],
    trigger: "Build UI components",
    badge: "core",
  },
  {
    id: "tailwind-design-system",
    category: "Frontend",
    categoryId: "02",
    icon: "🎨",
    name: "tailwind-design-system",
    tagline: "Design tokens + tenant branding",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob"],
    memory: false,
    description:
      "Maintains Tailwind design tokens with CSS variable overrides for tenant branding (colors, logos) and WCAG AA accessibility.",
    checklist: [
      "CSS vars for tenant primary color",
      "Base 4px spacing system",
      "Inter + JetBrains Mono fonts",
      "WCAG AA contrast ratios",
    ],
    trigger: "Design tokens, theming",
    badge: "core",
  },
  {
    id: "isolation-test-writer",
    category: "Testing",
    categoryId: "03",
    icon: "🧪",
    name: "isolation-test-writer",
    tagline: "CRITICAL: Tenant isolation tests",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob", "Grep"],
    memory: false,
    description:
      "Writes pytest tests verifying data isolation between tenants. MANDATORY on every PR — failure = critical data leak.",
    checklist: [
      "Test both directions (A→B and B→A)",
      "API-level tests, not just model-level",
      "Deterministic (no random data)",
      "Transaction rollback for cleanup",
    ],
    trigger: "After any new model/ViewSet",
    badge: "critical",
  },
  {
    id: "e2e-test-runner",
    category: "Testing",
    categoryId: "03",
    icon: "🎭",
    name: "e2e-test-runner",
    tagline: "Playwright E2E for multi-tenant",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    memory: false,
    description:
      "Creates Playwright E2E tests covering login flows, cross-tenant access prevention, tenant switcher, and WCAG accessibility.",
    checklist: [
      "Cross-tenant URL access blocked",
      "Tenant switcher redirects correctly",
      "Login flow per subdomain",
      "AxeBuilder accessibility scan",
    ],
    trigger: "Before major releases",
    badge: "core",
  },
  {
    id: "security-scanner",
    category: "Testing",
    categoryId: "03",
    icon: "🛡️",
    name: "security-scanner",
    tagline: "OWASP + LGPD compliance scanner",
    model: "sonnet",
    tools: ["Read", "Grep", "Glob", "Bash"],
    memory: true,
    permissionMode: "plan",
    description:
      "Scans for OWASP Top 10 vulnerabilities, LGPD compliance (consent, erasure, portability), and secret management issues.",
    checklist: [
      "No raw SQL with user input",
      "No |safe in Django templates",
      "No hardcoded secrets in code",
      "Bandit + Safety checks pass",
    ],
    trigger: "Before production releases",
    badge: "critical",
  },
  {
    id: "crm-module-expert",
    category: "Modules",
    categoryId: "04",
    icon: "🏘️",
    name: "crm-module-expert",
    tagline: "Leads, visits, reservations, pipeline",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob", "Grep"],
    memory: false,
    description:
      "Specialist for CRM: lead qualification with AI scoring, reservation locks with select_for_update(), calendar integration, and Kanban pipeline.",
    checklist: [
      "select_for_update() for reservations",
      "WhatsApp + email reminders",
      "Atlantic/Cape_Verde timezone",
      "Auto-advance pipeline rules",
    ],
    trigger: "CRM features",
    badge: "module",
  },
  {
    id: "construction-module-expert",
    category: "Modules",
    categoryId: "04",
    icon: "🏗️",
    name: "construction-module-expert",
    tagline: "Daily logs, WBS, offline mobile sync",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob", "Grep"],
    memory: false,
    description:
      "Handles offline-first mobile sync, dynamic inspection checklists, WBS progress with earned value calculations, and geotagged photos.",
    checklist: [
      "Offline queue with retry logic",
      "JSON inspection templates",
      "Earned Value = Budget × %",
      "EXIF stripping for privacy",
    ],
    trigger: "Construction features",
    badge: "module",
  },
  {
    id: "marketplace-integration-expert",
    category: "Modules",
    categoryId: "04",
    icon: "🔗",
    name: "marketplace-integration-expert",
    tagline: "imos.cv webhooks & sync",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Glob", "Grep"],
    memory: false,
    description:
      "Manages ImoOS ↔ imos.cv integration: listing publication, webhook signature validation, conflict resolution, and funnel analytics.",
    checklist: [
      "Webhook signature validation",
      "Conflict strategy: imoos_wins",
      "Conversion funnel tracking",
      "Handle lead.created events",
    ],
    trigger: "imos.cv integration",
    badge: "module",
  },
  {
    id: "docker-compose-expert",
    category: "DevOps",
    categoryId: "05",
    icon: "🐳",
    name: "docker-compose-expert",
    tagline: "PostgreSQL, Redis, Celery setup",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Bash", "Glob"],
    memory: false,
    description:
      "Configures Docker Compose with PostgreSQL 15, Redis 7, Celery workers, Celery Beat, and healthchecks for local/production.",
    checklist: [
      "Healthchecks on db and redis",
      ".env.example for all secrets",
      "Gunicorn with 4 workers",
      "Volume persistence config",
    ],
    trigger: "Docker setup",
    badge: "devops",
  },
  {
    id: "migration-orchestrator",
    category: "DevOps",
    categoryId: "05",
    icon: "🔀",
    name: "migration-orchestrator",
    tagline: "Safe multi-tenant migration rollout",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    memory: false,
    description:
      "Plans and executes batched migrations across all tenant schemas with backup, verification, and rollback procedures.",
    checklist: [
      "Backup before migration",
      "Batch in groups of 10",
      "Rate-limit to avoid DB overload",
      "Verify count after migration",
    ],
    trigger: "Migration rollout",
    badge: "devops",
  },
  {
    id: "ci-cd-pipeline-expert",
    category: "DevOps",
    categoryId: "05",
    icon: "🚀",
    name: "ci-cd-pipeline-expert",
    tagline: "GitHub Actions CI/CD pipeline",
    model: "sonnet",
    tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    memory: false,
    description:
      "Configures GitHub Actions for lint, test, security scan, Docker build, and deploy to staging/production with smoke tests.",
    checklist: [
      "Isolation tests gate PRs",
      "Coverage ≥ 80% on core apps",
      "Bandit + Safety in CI",
      "Slack notify on deploy",
    ],
    trigger: "CI/CD configuration",
    badge: "devops",
  },
];

const categories = [
  { id: "all", label: "All Agents", icon: "◈" },
  { id: "Architecture", label: "Architecture", icon: "🏗️", color: "#7C3AED" },
  { id: "Backend", label: "Backend", icon: "⚙️", color: "#0F766E" },
  { id: "Frontend", label: "Frontend", icon: "⚛️", color: "#1D4ED8" },
  { id: "Testing", label: "Testing", icon: "🧪", color: "#B45309" },
  { id: "Modules", label: "Modules", icon: "📦", color: "#047857" },
  { id: "DevOps", label: "DevOps", icon: "🚀", color: "#9D174D" },
];

const badgeConfig = {
  critical: { label: "CRITICAL", bg: "#FEF2F2", text: "#991B1B", border: "#FECACA" },
  core: { label: "CORE", bg: "#EFF6FF", text: "#1E40AF", border: "#BFDBFE" },
  module: { label: "MODULE", bg: "#F0FDF4", text: "#14532D", border: "#BBF7D0" },
  devops: { label: "DEVOPS", bg: "#FAF5FF", text: "#6B21A8", border: "#E9D5FF" },
};

const categoryColors = {
  Architecture: "#7C3AED",
  Backend: "#0F766E",
  Frontend: "#1D4ED8",
  Testing: "#B45309",
  Modules: "#047857",
  DevOps: "#9D174D",
};

export default function ImoOSAgentsDashboard() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [search, setSearch] = useState("");

  const filtered = agents.filter((a) => {
    const matchCat = activeCategory === "all" || a.category === activeCategory;
    const matchSearch =
      !search ||
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.description.toLowerCase().includes(search.toLowerCase()) ||
      a.trigger.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  const criticalCount = agents.filter((a) => a.badge === "critical").length;
  const withMemory = agents.filter((a) => a.memory).length;

  return (
    <div style={{ fontFamily: "'DM Mono', 'JetBrains Mono', monospace", background: "#0A0A0F", minHeight: "100vh", color: "#E2E8F0" }}>
      {/* Header */}
      <div style={{ borderBottom: "1px solid #1E1E2E", background: "#0D0D1A", padding: "24px 32px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", maxWidth: 1200, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ width: 40, height: 40, background: "linear-gradient(135deg, #6366F1, #8B5CF6)", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>
              🤖
            </div>
            <div>
              <div style={{ fontSize: 18, fontWeight: 700, color: "#F1F5F9", letterSpacing: "-0.5px" }}>
                ImoOS <span style={{ color: "#6366F1" }}>Claude Subagents</span>
              </div>
              <div style={{ fontSize: 11, color: "#64748B", marginTop: 2 }}>
                .claude/agents/ — 18 production-ready specialists
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 20 }}>
            {[
              { v: agents.length, l: "agents" },
              { v: criticalCount, l: "critical", color: "#EF4444" },
              { v: withMemory, l: "with memory", color: "#8B5CF6" },
            ].map((s, i) => (
              <div key={i} style={{ textAlign: "center" }}>
                <div style={{ fontSize: 22, fontWeight: 700, color: s.color || "#6366F1" }}>{s.v}</div>
                <div style={{ fontSize: 10, color: "#475569", textTransform: "uppercase", letterSpacing: 1 }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 32px" }}>
        {/* Search + Filter */}
        <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search agents by name, description, trigger..."
            style={{
              flex: 1, minWidth: 240, padding: "10px 16px",
              background: "#111827", border: "1px solid #1F2937",
              borderRadius: 8, color: "#E2E8F0", fontSize: 13,
              outline: "none", fontFamily: "inherit",
            }}
          />
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              style={{
                padding: "8px 14px", borderRadius: 8, fontSize: 12, cursor: "pointer",
                border: activeCategory === cat.id ? `1px solid ${cat.color || "#6366F1"}` : "1px solid #1F2937",
                background: activeCategory === cat.id ? `${cat.color || "#6366F1"}22` : "#111827",
                color: activeCategory === cat.id ? (cat.color || "#6366F1") : "#64748B",
                fontFamily: "inherit", transition: "all 0.15s",
              }}
            >
              {cat.icon} {cat.label}
            </button>
          ))}
        </div>

        {/* Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 16 }}>
          {filtered.map((agent) => {
            const bc = badgeConfig[agent.badge];
            const catColor = categoryColors[agent.category] || "#6366F1";
            const isSelected = selectedAgent?.id === agent.id;

            return (
              <div
                key={agent.id}
                onClick={() => setSelectedAgent(isSelected ? null : agent)}
                style={{
                  background: "#111827",
                  border: isSelected ? `1px solid ${catColor}` : "1px solid #1F2937",
                  borderRadius: 12, padding: 20, cursor: "pointer",
                  transition: "all 0.2s",
                  boxShadow: isSelected ? `0 0 0 1px ${catColor}40, 0 4px 20px ${catColor}20` : "none",
                }}
              >
                {/* Card Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 22 }}>{agent.icon}</span>
                    <div>
                      <div style={{ fontSize: 12, color: catColor, fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.5 }}>
                        {agent.category}
                      </div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "#F1F5F9", marginTop: 1 }}>
                        {agent.name}
                      </div>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                    {agent.memory && (
                      <span style={{ fontSize: 10, padding: "2px 6px", background: "#1E1340", color: "#8B5CF6", border: "1px solid #312E81", borderRadius: 4 }}>
                        MEM
                      </span>
                    )}
                    <span style={{ fontSize: 10, padding: "2px 6px", background: bc.bg, color: bc.text, border: `1px solid ${bc.border}`, borderRadius: 4 }}>
                      {bc.label}
                    </span>
                  </div>
                </div>

                {/* Tagline */}
                <div style={{ fontSize: 12, color: "#94A3B8", marginBottom: 12 }}>{agent.tagline}</div>

                {/* Description */}
                <div style={{ fontSize: 12, color: "#64748B", lineHeight: 1.6, marginBottom: 14 }}>
                  {agent.description}
                </div>

                {/* Tools */}
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
                  {agent.tools.map((t) => (
                    <span key={t} style={{ fontSize: 10, padding: "2px 8px", background: "#0F172A", color: "#475569", border: "1px solid #1E293B", borderRadius: 4 }}>
                      {t}
                    </span>
                  ))}
                </div>

                {/* Trigger */}
                <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 10px", background: "#0F172A", borderRadius: 6 }}>
                  <span style={{ fontSize: 10, color: "#475569" }}>INVOKE WHEN</span>
                  <span style={{ fontSize: 11, color: "#94A3B8" }}>{agent.trigger}</span>
                </div>

                {/* Expanded Checklist */}
                {isSelected && (
                  <div style={{ marginTop: 16, borderTop: "1px solid #1E293B", paddingTop: 16 }}>
                    <div style={{ fontSize: 10, color: "#475569", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>
                      Checklist
                    </div>
                    {agent.checklist.map((item, i) => (
                      <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 6 }}>
                        <span style={{ color: catColor, marginTop: 1, flexShrink: 0 }}>▸</span>
                        <span style={{ fontSize: 12, color: "#94A3B8", lineHeight: 1.5 }}>{item}</span>
                      </div>
                    ))}
                    <div style={{ marginTop: 12, padding: "8px 10px", background: "#0A0A0F", borderRadius: 6, fontFamily: "inherit" }}>
                      <span style={{ fontSize: 10, color: "#475569" }}>FILE PATH </span>
                      <span style={{ fontSize: 11, color: "#6366F1" }}>
                        .claude/agents/{agent.categoryId}-{agent.category.toLowerCase()}/{agent.name}.md
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Install Instructions */}
        <div style={{ marginTop: 32, background: "#111827", border: "1px solid #1F2937", borderRadius: 12, padding: 24 }}>
          <div style={{ fontSize: 13, color: "#6366F1", fontWeight: 600, marginBottom: 16 }}>
            ⚡ Quick Setup
          </div>
          {[
            { cmd: "mkdir -p imos/.claude/agents/{00-architecture,01-backend,02-frontend,03-testing,04-modules,05-devops}", label: "1. Create structure" },
            { cmd: "# Copy all .md files from the downloaded folder into the respective subdirs", label: "2. Add agents" },
            { cmd: "cd imos && claude agents", label: "3. Verify (lists all 18)" },
            { cmd: 'git add .claude/agents/ && git commit -m "feat: add 18 Claude Code subagents"', label: "4. Commit" },
          ].map((step, i) => (
            <div key={i} style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 10, color: "#475569", marginBottom: 4 }}>{step.label}</div>
              <div style={{ background: "#0A0A0F", border: "1px solid #1E293B", borderRadius: 6, padding: "10px 14px", fontSize: 12, color: "#94A3B8", wordBreak: "break-all" }}>
                $ {step.cmd}
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 16, textAlign: "center", fontSize: 11, color: "#334155" }}>
          Click any agent card to expand checklist & file path · ImoOS PropTech SaaS · Cabo Verde 🇨🇻
        </div>
      </div>
    </div>
  );
}
