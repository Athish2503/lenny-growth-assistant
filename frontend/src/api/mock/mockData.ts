import type { Session, Message, Artifact, Settings, Citation, RetrievedChunk } from '@/types';

// ============================================================
// Mock Sessions
// ============================================================
const now = new Date();
const daysAgo = (d: number) => new Date(now.getTime() - d * 86400000).toISOString();

export const mockSessions: Session[] = [
  {
    id: 'session-001',
    title: 'Product-Led Growth Strategy for B2B SaaS',
    user_id: 'user-001',
    created_at: daysAgo(0),
    updated_at: daysAgo(0),
    message_count: 12,
    last_message: 'What activation metrics should I track for our onboarding funnel?',
    last_message_at: daysAgo(0),
  },
  {
    id: 'session-002',
    title: 'Retention Loop Analysis — Notion Case Study',
    user_id: 'user-001',
    created_at: daysAgo(0),
    updated_at: daysAgo(0),
    message_count: 7,
    last_message: 'Analyze Notion\'s retention mechanics',
    last_message_at: daysAgo(0),
  },
  {
    id: 'session-003',
    title: 'Viral Coefficient & Referral Programs',
    user_id: 'user-001',
    created_at: daysAgo(1),
    updated_at: daysAgo(1),
    message_count: 4,
    last_message: 'How do I calculate viral coefficient?',
    last_message_at: daysAgo(1),
  },
  {
    id: 'session-004',
    title: 'Write an essay on pricing psychology',
    user_id: 'user-001',
    created_at: daysAgo(1),
    updated_at: daysAgo(1),
    message_count: 2,
    last_message: 'Essay on pricing psychology in SaaS',
    last_message_at: daysAgo(1),
  },
  {
    id: 'session-005',
    title: 'North Star Metrics Deep Dive',
    user_id: 'user-001',
    created_at: daysAgo(2),
    updated_at: daysAgo(2),
    message_count: 9,
    last_message: 'What is the best north star metric for a marketplace?',
    last_message_at: daysAgo(2),
  },
  {
    id: 'session-006',
    title: 'Onboarding Funnel Optimization',
    user_id: 'user-001',
    created_at: daysAgo(5),
    updated_at: daysAgo(5),
    message_count: 6,
    last_message: 'Best practices for reducing time-to-value',
    last_message_at: daysAgo(5),
  },
  {
    id: 'session-007',
    title: 'User Segmentation for Growth Experiments',
    user_id: 'user-001',
    created_at: daysAgo(7),
    updated_at: daysAgo(7),
    message_count: 5,
    last_message: 'How do I segment users by activation cohorts?',
    last_message_at: daysAgo(7),
  },
];

// ============================================================
// Mock Citations
// ============================================================
export const mockCitations: Citation[] = [
  {
    id: 'cite-001',
    title: 'Lenny\'s Newsletter: Product-Led Growth',
    source: 'Lenny Rachitsky (2023)',
    snippet: 'PLG companies that hit $100M ARR grew 2.4x faster than sales-led counterparts, with substantially lower CAC...',
    relevance_score: 0.94,
    chunk_index: 3,
  },
  {
    id: 'cite-002',
    title: 'Activation Metrics That Matter',
    source: 'Lenny Rachitsky (2022)',
    snippet: 'The single best predictor of long-term retention is whether a user completes the "aha moment" within the first 7 days...',
    relevance_score: 0.87,
    chunk_index: 7,
  },
  {
    id: 'cite-003',
    title: 'The North Star Framework',
    source: 'Lenny Rachitsky (2021)',
    snippet: 'Your North Star Metric is the single metric that best captures the core value your product delivers to customers...',
    relevance_score: 0.81,
    chunk_index: 12,
  },
];

// ============================================================
// Mock Retrieved Chunks
// ============================================================
export const mockChunks: RetrievedChunk[] = [
  {
    id: 'chunk-001',
    content: 'Product-led growth (PLG) is a go-to-market strategy that relies on your product itself as the primary vehicle to acquire, activate, and retain customers. Companies like Slack, Notion, Figma, and Dropbox are canonical examples of PLG done right.',
    source: 'PLG Strategy Guide — Lenny\'s Newsletter 2023',
    score: 0.94,
  },
  {
    id: 'chunk-002',
    content: 'The activation rate is defined as the percentage of new users who reach the "aha moment" — the point at which they experience the core value of your product. For most SaaS products, this should happen within the first session or first week.',
    source: 'Activation Metrics — Lenny\'s Newsletter 2022',
    score: 0.87,
  },
  {
    id: 'chunk-003',
    content: 'Retention curves that flatten indicate product-market fit. If your D30 retention is above 25% for a consumer product or above 40% for a B2B product, you are in strong territory for sustainable growth.',
    source: 'Retention Benchmarks — Lenny\'s Newsletter 2022',
    score: 0.79,
  },
];

// ============================================================
// Mock Messages
// ============================================================
export const mockMessages: Record<string, Message[]> = {
  'session-001': [
    {
      id: 'msg-001',
      session_id: 'session-001',
      role: 'user',
      content: 'What is product-led growth and how does it differ from sales-led growth?',
      created_at: daysAgo(0),
    },
    {
      id: 'msg-002',
      session_id: 'session-001',
      role: 'assistant',
      content: `## Product-Led Growth (PLG) vs. Sales-Led Growth

**Product-Led Growth (PLG)** is a go-to-market strategy where the product itself is the primary driver of customer acquisition, expansion, and retention — rather than a traditional sales team.

### Key Differences

| Dimension | Product-Led | Sales-Led |
|-----------|-------------|-----------|
| Primary Driver | Product experience | Sales team |
| CAC | Low (~$50–500) | High (~$5k–50k) |
| Time-to-Value | Minutes to hours | Weeks to months |
| Scalability | Very high | Linear with headcount |
| Examples | Slack, Figma, Notion | Salesforce, Workday |

### Why PLG Works

The core insight is that **users who experience your product's value before they pay** are far more likely to convert and retain. Key mechanics:

1. **Freemium / Free Trial** — remove friction from initial adoption
2. **Self-serve onboarding** — guide users to the aha moment without human touch
3. **Virality built-in** — product naturally spreads through collaboration or sharing
4. **Usage-based expansion** — revenue grows as users get more value

### When to Use PLG

PLG works best when:
- Your product delivers immediate, demonstrable value
- The product is inherently collaborative or shareable  
- ACV is under $25k (above that, enterprise sales typically wins)
- You can build a self-serve onboarding experience`,
      created_at: daysAgo(0),
      citations: mockCitations,
      metadata: {
        service: 'QAService',
        intent: 'qa',
        retrieval_performed: true,
        confidence_score: 0.91,
        retrieval_time_ms: 342,
        model: 'claude-3-5-sonnet-20241022',
        sources: mockCitations,
      },
    },
    {
      id: 'msg-003',
      session_id: 'session-001',
      role: 'user',
      content: 'What activation metrics should I track for our onboarding funnel?',
      created_at: daysAgo(0),
    },
    {
      id: 'msg-004',
      session_id: 'session-001',
      role: 'assistant',
      content: `## Key Activation Metrics for Onboarding Funnels

The right activation metrics tell you whether users are reaching your **aha moment** — the point where they first experience core product value.

### Primary Metrics to Track

**1. Time-to-Aha-Moment (TtAM)**
- How long it takes from sign-up to the first value experience
- Target: < 5 minutes for consumer apps, < 1 session for B2B

**2. Activation Rate**
- % of new users who complete your defined activation event within 7 days
- Formula: \`Activated Users / Total New Users × 100\`
- Benchmarks: 25–40% is good, 50%+ is excellent

**3. Onboarding Completion Rate**
- % of users who finish your full onboarding sequence
- Break this down step by step to find drop-off points

**4. Feature Adoption Rate**
- Which features do activated users use vs. churned users?
- Run a correlation analysis to identify your "power features"

### How to Define Your Activation Event

The activation event should be:
- Specific and measurable (not just "logged in")
- Correlated with long-term retention
- Achievable in a single session ideally

**Examples by product type:**
- Slack: Sent 2000+ messages as a team
- Dropbox: Uploaded at least one file
- HubSpot: Created and sent first email campaign`,
      created_at: daysAgo(0),
      citations: [mockCitations[1], mockCitations[0]],
      metadata: {
        service: 'QAService',
        intent: 'qa',
        retrieval_performed: true,
        confidence_score: 0.88,
        retrieval_time_ms: 287,
        model: 'claude-3-5-sonnet-20241022',
        sources: [mockCitations[1], mockCitations[0]],
      },
    },
  ],
  'session-004': [
    {
      id: 'msg-e-001',
      session_id: 'session-004',
      role: 'user',
      content: 'Write an essay on pricing psychology in SaaS',
      created_at: daysAgo(1),
    },
    {
      id: 'msg-e-002',
      session_id: 'session-004',
      role: 'assistant',
      content: `# The Hidden Psychology Behind SaaS Pricing

**Hook:** Your pricing page isn't a math problem. It's a psychological battleground.

Most founders obsess over the numbers — $29 vs $39, annual vs monthly. But the real lever? **How your pricing makes people feel.**

Here are 4 psychological principles that separate top SaaS pricing from forgettable ones:

## 1. Anchoring Controls Perception

The first price a customer sees becomes their reference point for everything else. That's why enterprise tiers exist even for companies that never close enterprise deals — they anchor the perception of mid-tier as "reasonable."

Put your highest tier first. Let $499/mo make $99/mo feel like a steal.

## 2. The Magic of "One More Thing"

People don't buy on value — they buy when the **cost of NOT buying** exceeds the price. Frame pricing around pain avoidance, not feature accumulation. "Save 40 hours per month" outperforms "Unlimited exports" every time.

## 3. Decoy Pricing Creates Clear Winners

Three-tier pricing works because the middle tier is the decoy. Make the difference between Starter and Pro small in price but massive in value. The Pro tier wins by default.

## 4. Annual Plans Aren't About Discount — They're About Commitment

When someone pays annually, they psychologically commit to becoming a power user. Conversion to annual = 3x retention improvement in most SaaS cohort analyses.

**Takeaway:** Price to shape behavior, not just capture revenue. The best SaaS pricing creates a psychological pull toward the outcome you want for your customers.`,
      created_at: daysAgo(1),
      metadata: {
        service: 'EssayService',
        intent: 'essay',
        retrieval_performed: false,
        is_essay: true,
        model: 'claude-3-5-sonnet-20241022',
      },
    },
  ],
};

// ============================================================
// Mock Artifacts
// ============================================================
export const mockArtifacts: Artifact[] = [
  {
    id: 'artifact-001',
    session_id: 'session-001',
    title: 'PLG Activation Metrics Dashboard',
    artifact_type: 'markdown',
    version: 1,
    created_at: daysAgo(0),
    content: `# PLG Activation Metrics Dashboard

## Overview
This document outlines the key metrics and tracking framework for your Product-Led Growth activation funnel.

## Tier 1 — Awareness Metrics
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Sign-up Rate | 3.2% | 5.0% | 🔴 Below |
| Email Verification | 72% | 85% | 🟡 Close |
| First Login Rate | 68% | 80% | 🟡 Close |

## Tier 2 — Activation Metrics
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Aha Moment Rate (7d) | 31% | 45% | 🔴 Below |
| Onboarding Completion | 44% | 60% | 🔴 Below |
| Core Feature Used | 38% | 50% | 🔴 Below |

## Tier 3 — Engagement Metrics
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| D7 Retention | 28% | 40% | 🔴 Below |
| D30 Retention | 16% | 25% | 🔴 Below |
| Power User Rate | 8% | 15% | 🔴 Below |

## Recommended Actions
1. **Reduce TtAhaMoment** — cut onboarding steps from 9 to 5
2. **Add progress indicators** — show users how close they are to activation
3. **Personalize first session** — use signup intent to customize onboarding
4. **Build habit loops** — send D3/D7 re-engagement nudges
`,
    metadata: { service: 'ArtifactService', frontend_rendered: false },
  },
  {
    id: 'artifact-002',
    session_id: 'session-001',
    title: 'Activation Dashboard Component',
    artifact_type: 'html',
    version: 1,
    created_at: daysAgo(0),
    content: `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Activation Dashboard</title>
  <style>
    :root {
      --bg: #09090b;
      --surface: #18181b;
      --border: #27272a;
      --text: #fafafa;
      --muted: #a1a1aa;
      --blue: #3b82f6;
      --green: #22c55e;
      --red: #ef4444;
      --yellow: #f59e0b;
    }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; }
    h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 4px; }
    .subtitle { color: var(--muted); font-size: 0.875rem; margin-bottom: 24px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
    .card-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .card-value { font-size: 2rem; font-weight: 700; }
    .card-change { font-size: 0.8125rem; margin-top: 4px; }
    .up { color: var(--green); }
    .down { color: var(--red); }
    .bar { height: 6px; background: #27272a; border-radius: 9999px; margin-top: 12px; overflow: hidden; }
    .bar-fill { height: 100%; border-radius: 9999px; }
  </style>
</head>
<body>
  <h1>Activation Dashboard</h1>
  <p class="subtitle">PLG Metrics — Last 30 days</p>
  <div class="grid">
    <div class="card">
      <div class="card-label">Activation Rate</div>
      <div class="card-value" style="color: var(--yellow)">31%</div>
      <div class="card-change down">↓ 3% vs last month</div>
      <div class="bar"><div class="bar-fill" style="width:31%; background: var(--yellow)"></div></div>
    </div>
    <div class="card">
      <div class="card-label">D7 Retention</div>
      <div class="card-value" style="color: var(--red)">28%</div>
      <div class="card-change up">↑ 2% vs last month</div>
      <div class="bar"><div class="bar-fill" style="width:28%; background: var(--red)"></div></div>
    </div>
    <div class="card">
      <div class="card-label">Avg. TtAhaMoment</div>
      <div class="card-value" style="color: var(--blue)">4.2m</div>
      <div class="card-change up">↑ improving</div>
      <div class="bar"><div class="bar-fill" style="width:60%; background: var(--blue)"></div></div>
    </div>
  </div>
</body>
</html>`,
    metadata: { service: 'ArtifactService', frontend_rendered: false },
  },
];

// ============================================================
// Mock Settings
// ============================================================
export const mockSettings = {
  theme: 'dark' as const,
  provider: 'anthropic' as const,
  model: 'claude-3-5-sonnet-20241022',
  embedding_model: 'text-embedding-3-small',
  temperature: 0.7,
  max_tokens: 4096,
  system_prompt: 'You are Lenny, an expert growth advisor with deep knowledge of product-led growth, SaaS metrics, retention, and growth strategy. You have access to Lenny Rachitsky\'s newsletter archives and can provide detailed, evidence-based answers with citations.',
  stream_responses: true,
};

// ============================================================
// Mock AI Responses (for streaming simulation)
// ============================================================
export const mockResponses = [
  `## Product-Led Growth Key Insights

Based on the relevant content from Lenny's archives, here are the most important frameworks:

**The Activation Hierarchy:**
1. Sign-up → email verification → first login (awareness)
2. First core action → aha moment (activation)  
3. Habit formation → expansion → advocacy (retention)

The most critical insight from the data is that **teams with activation rates above 45% see 3x better D90 retention**. This correlation is stronger than any other metric.

**Quick Wins:**
- Reduce onboarding steps to under 5
- Send a personalized D1 email with their specific use case
- Surface the "magic moment" in the first session proactively`,

  `## Essay: The Growth Loop Mindset

**Hook:** Every sustainable growth system is a loop, not a funnel.

Funnels leak. Loops compound.

The best growth teams in the world — at Notion, Figma, Slack — don't think in linear funnels. They build **closed loops** where the output of one stage becomes the input of the next.

**The Three Loop Types:**

**1. Viral Loops**
One user's action invites more users. Figma's share-to-collaborate feature is a masterclass in this. Every export, every shared link is a free acquisition moment.

**2. Content Loops**
Users create content that attracts new users. Notion templates, Airtable bases, Canva designs — each piece of user-generated content is a top-of-funnel asset.

**3. Product Loops**
The product itself creates more product value as users join. Slack is worthless alone; invaluable with a team. This network effect IS the growth loop.

**Takeaway:** Stop optimizing your funnel. Build a loop. The difference between 30% and 300% YoY growth lives in that mindset shift.`,

  `## Retention Analysis Framework

Retention is the foundation of all sustainable growth. Without it, acquisition is just filling a leaky bucket.

### The Retention Curve

A healthy retention curve:
- Starts high (strong initial activation)
- Falls quickly in the first 7 days (expected)
- Flattens and stabilizes (product-market fit signal)

If your curve never flattens, you don't have PMF yet. Full stop.

### Segmentation Strategy

Don't look at aggregate retention — it hides the signal:

| Segment | What to look for |
|---------|-----------------|
| By activation | Activated vs non-activated users |
| By cohort | Weekly acquisition cohorts |
| By use case | Power users vs casual users |
| By source | Organic vs paid vs referral |

The biggest insight usually comes from comparing activated vs non-activated users' D30 retention. The delta tells you exactly how important activation is to your business.`,
];
