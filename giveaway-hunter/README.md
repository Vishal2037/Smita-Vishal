# Giveaway Hunter

A local-first Windows dashboard for finding, reviewing, and tracking giveaways.

## Current features
- YouTube discovery through the official YouTube Data API (optional API key).
- Cross-platform public-web search for indexed Instagram, TikTok, Facebook, X, Reddit, YouTube, and selected giveaway-host sites using a search provider.
- Manual intake for any platform.
- Local SQLite tracker, duplicate URL checks, prize/deadline/eligibility fields.
- Basic instruction extraction and heuristic scam flags.
- Draft entry preparation and status tracking.
- Human approval by design; the app never auto-likes, follows, comments, or submits forms.

## Windows setup
1. Open PowerShell in this folder.
2. Run:
   ```powershell
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```
3. Optional YouTube search: enable YouTube Data API v3 in Google Cloud Console, create an API key, and paste it into the sidebar.

## Important limitations
- Public-web search is best-effort. Search engines do not index every post, and social platforms may hide content behind login or restrict automated access.
- A result is only a lead. Verify the official rules, host identity, deadline, eligibility, and whether entries are still open.
- Search-provider availability and terms may change. Do not use scraping to bypass authentication, CAPTCHAs, rate limits, or platform restrictions.
- AI/video analysis, robust winner verification, reminders, and assisted submission are roadmap items, not completed features.

## Roadmap
1. Local Ollama model for transcript and rules extraction.
2. Approved/public platform-specific discovery connectors where they provide materially better coverage.
3. Evidence-backed host verification and winner tracking.
4. Deadline reminders.
5. Browser-assisted entry preparation only where platform rules permit, with explicit human confirmation.

[executed on device: Vishal (076fbc72-706e-48da-9906-48ff11fef637)]