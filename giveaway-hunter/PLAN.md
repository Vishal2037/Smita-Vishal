# Product plan

## Goal
Find worthwhile giveaways across major platforms, understand entry requirements, and help the user complete eligible entries with explicit approval.

## Architecture
- UI: Streamlit local app.
- Storage: local SQLite.
- Discovery: official YouTube Data API first; manual intake for other platforms until compliant public/approved interfaces are verified.
- Understanding: descriptions/transcripts; deterministic extraction in MVP; optional local Ollama model later.
- Risk checks: official rules, host identity/history, upfront-payment requests, credential requests, eligibility, suspicious URLs.
- Entry: prepare drafts and checklists; user approves external actions. Never bypass CAPTCHA, access controls, or platform restrictions.

## Milestones
1. Dashboard, local DB, YouTube search, manual intake, checklists, risk flags.
2. Local model integration for transcript understanding.
3. Evidence-backed host verification and winner follow-up.
4. Deadline notifications.
5. Platform-specific assisted entry only where explicitly permitted.

## Metrics
- Relevant giveaways per 20 results.
- Fraction with official rules and eligible geography confirmed.
- Median discovery-to-review time.
- Duplicate rate and false-positive scam flags.
- Entries completed and outcomes tracked.
