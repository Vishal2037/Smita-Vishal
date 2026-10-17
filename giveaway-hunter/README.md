# Giveaway Hunter

A local-first Windows dashboard for finding, reviewing, and tracking giveaways. YouTube search uses the official YouTube Data API when configured. The app also accepts manual links from Instagram, TikTok, Facebook, X, and websites, extracts likely entry instructions from provided descriptions/transcripts, and tracks draft entries.

## Features
- Local SQLite tracker.
- Optional YouTube API search.
- Manual intake for all major platforms.
- Entry checklist extraction and heuristic scam flags.
- Prize, deadline, eligibility, status, and draft tracking.
- Human approval by design; no automated likes, follows, comments, or submissions.

## Windows setup
1. Install Python 3.11+.
2. Open PowerShell in this folder:
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python -m streamlit run app.py
   ```
3. Optional YouTube search: enable YouTube Data API v3 in Google Cloud Console, create an API key, and paste it into the sidebar. Keep the key private. Search quota is limited; searches only run when you click the button.

## Platform coverage
- YouTube: official API search when configured.
- Instagram: API access is limited; consumer accounts are not generally searchable through the professional-account API.
- TikTok: general discovery depends on approved APIs/scopes; standard APIs are not unrestricted global search.
- Facebook and X: access depends on current API permissions and plans.
- Other websites: manual intake now; compliant discovery adapters can be added later.

## Roadmap
1. Optional local Ollama model for structured transcript analysis.
2. Evidence-backed host verification and winner tracking.
3. Permitted public-web discovery adapters.
4. Deadline and winner notifications.
5. Browser-assisted entry preparation only where platform rules permit, with explicit approval.

A heuristic score is not proof of legitimacy. Never pay upfront to claim a prize or disclose passwords, OTPs, or recovery phrases.
