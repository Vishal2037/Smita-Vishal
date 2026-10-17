from __future__ import annotations
import os, re, sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "giveaways.db"
STATUSES = ["Found", "Review", "Ready to enter", "Entered", "Won", "Lost", "Expired", "Rejected"]
PLATFORMS = ["YouTube", "Instagram", "TikTok", "Facebook", "X", "Website", "Other"]
PRIZE_TYPES = ["Cash", "Gift card", "Electronics", "PC / GPU", "Phone", "AI tools / credits", "Subscription", "Other"]
SCAM_TERMS = ["pay shipping", "processing fee", "claim fee", "send crypto", "seed phrase", "password", "gift card payment", "verification fee"]
ENTRY_TERMS = ["comment", "subscribe", "follow", "like", "tag", "share", "retweet", "repost", "fill out", "form", "email", "register"]
GIVEAWAY_TERMS = ["giveaway", "give away", "win", "winner", "prize", "free", "contest", "raffle", "draw"]

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS giveaways (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
        platform TEXT NOT NULL DEFAULT 'Other', creator TEXT DEFAULT '', prize_type TEXT DEFAULT 'Other',
        prize_value REAL DEFAULT 0, currency TEXT DEFAULT 'USD', deadline TEXT DEFAULT '',
        eligibility TEXT DEFAULT '', instructions TEXT DEFAULT '', prepared_entry TEXT DEFAULT '',
        credibility INTEGER DEFAULT 50, risk_notes TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'Found',
        source TEXT DEFAULT 'Manual', created_at TEXT NOT NULL)""")
    conn.commit()
    return conn

def assess(title, creator, url, instructions):
    text = f"{title} {creator} {url} {instructions}".lower()
    flags, positives = [], []
    for term in SCAM_TERMS:
        if term in text: flags.append(f"Potential scam indicator: “{term}”")
    if any(x in text for x in ["official rules", "terms and conditions", "eligibility", "ends on", "deadline"]):
        positives.append("Formal rules or deadline language detected")
    if any(x in text for x in ["winner announced", "past winners", "previous winners", "winner proof"]):
        positives.append("Mentions winner announcements or prior winners; verify independently")
    if not url.startswith("https://"): flags.append("Link is not HTTPS or has no secure URL")
    if not instructions.strip(): flags.append("Entry instructions have not been reviewed yet")
    if any(term in text for term in GIVEAWAY_TERMS): positives.append("Giveaway-related language detected")
    score = 50 + min(20, len(positives) * 8) - min(60, len(flags) * 18)
    if not any(term in text for term in GIVEAWAY_TERMS): score -= 15
    return max(0, min(100, score)), flags, positives

def extract_instructions(text):
    sentences = re.split(r"(?<=[.!?\n])\s+", text.strip())
    return [s.strip(" •-*\t") for s in sentences if s.strip() and any(t in s.lower() for t in ENTRY_TERMS)][:20]

st.set_page_config(page_title="Giveaway Hunter", page_icon="🎁", layout="wide")
st.title("🎁 Giveaway Hunter")
st.caption("Local-first giveaway research dashboard · review and approve every entry")
st.info("Safety by design: this MVP never likes, follows, comments, or submits forms automatically.")
conn = db()

with st.sidebar:
    st.header("Discovery")
    api_key = st.text_input("YouTube Data API key", value=os.getenv("YOUTUBE_API_KEY", ""), type="password",
        help="Optional. Enable YouTube Data API v3 in Google Cloud. Key is used for searches you initiate.")
    query = st.text_input("Keywords", "giveaway OR win free")
    recency = st.selectbox("Upload window", ["Any time", "Today", "This week", "This month"], index=2)
    max_results = st.slider("Results per search", 5, 25, 10)
    search_clicked = st.button("Search YouTube", type="primary", use_container_width=True)
    st.divider()
    st.caption("Other platforms support manual intake in this MVP. We will only add discovery through permitted APIs/public sources.")

if search_clicked:
    if not api_key:
        st.error("Add a YouTube Data API key to search, or use manual intake below.")
    else:
        try:
            import requests
            params = {"part":"snippet", "q":query, "type":"video", "maxResults":max_results, "key":api_key, "order":"date"}
            if recency != "Any time":
                days = {"Today":1, "This week":7, "This month":30}[recency]
                params["publishedAfter"] = (datetime.now(timezone.utc)-timedelta(days=days)).isoformat(timespec="seconds").replace("+00:00","Z")
            response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=20)
            response.raise_for_status()
            results = []
            for item in response.json().get("items", []):
                snippet, vid = item.get("snippet", {}), item.get("id", {}).get("videoId")
                if not vid: continue
                title, desc = snippet.get("title", ""), snippet.get("description", "")
                if any(t in f"{title} {desc}".lower() for t in GIVEAWAY_TERMS):
                    results.append({"title":title, "url":f"https://www.youtube.com/watch?v={vid}", "platform":"YouTube",
                                    "creator":snippet.get("channelTitle",""), "instructions":desc[:5000], "source":"YouTube Data API"})
            st.session_state.search_results = results
            st.success(f"Found {len(results)} likely giveaway video(s). Review before saving.")
        except Exception as exc: st.error(f"YouTube search failed: {exc}")

for i, item in enumerate(st.session_state.get("search_results", [])):
    with st.container(border=True):
        st.markdown(f"**{item['title']}**")
        st.caption(f"{item['creator']} · {item['url']}")
        if st.button("Save for review", key=f"save_{i}"):
            score, flags, _ = assess(item["title"], item["creator"], item["url"], item["instructions"])
            try:
                conn.execute("""INSERT INTO giveaways(title,url,platform,creator,instructions,credibility,risk_notes,status,source,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""", (item["title"],item["url"],item["platform"],item["creator"],item["instructions"],
                    score,"; ".join(flags),"Review",item["source"],datetime.now(timezone.utc).isoformat()))
                conn.commit(); st.success("Saved.")
            except sqlite3.IntegrityError: st.warning("This URL is already saved.")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader("Add a giveaway")
    with st.form("add_form", clear_on_submit=True):
        title = st.text_input("Title *")
        url = st.text_input("Public giveaway/video URL *", placeholder="https://...")
        c1,c2 = st.columns(2)
        platform = c1.selectbox("Platform", PLATFORMS)
        prize_type = c2.selectbox("Prize type", PRIZE_TYPES)
        creator = st.text_input("Creator / brand")
        c3,c4 = st.columns(2)
        prize_value = c3.number_input("Estimated prize value", min_value=0.0, step=10.0)
        currency = c4.selectbox("Currency", ["USD","INR","GBP","EUR","Other"])
        deadline = st.text_input("Deadline (as stated)")
        eligibility = st.text_input("Eligibility / country restrictions")
        instructions = st.text_area("Description, transcript, or rules", height=150)
        submitted = st.form_submit_button("Add to tracker", type="primary")
        if submitted:
            if not title.strip() or not url.strip().startswith("https://"):
                st.error("Enter a title and complete HTTPS URL.")
            else:
                score, flags, _ = assess(title, creator, url, instructions)
                try:
                    conn.execute("""INSERT INTO giveaways(title,url,platform,creator,prize_type,prize_value,currency,deadline,eligibility,instructions,credibility,risk_notes,status,source,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (title.strip(),url.strip(),platform,creator.strip(),prize_type,prize_value,currency,
                    deadline.strip(),eligibility.strip(),instructions.strip(),score,"; ".join(flags),"Review","Manual",datetime.now(timezone.utc).isoformat()))
                    conn.commit(); st.success("Added. Review the flags and instructions below.")
                except sqlite3.IntegrityError: st.error("That URL is already in your tracker.")

with right:
    st.subheader("Instruction extractor")
    raw = st.text_area("Paste video transcript or giveaway rules", height=220, key="extract_text")
    if st.button("Extract entry checklist"):
        found = extract_instructions(raw)
        st.session_state.extracted = found or ["No obvious entry instructions found. Read the official rules manually."]
    for line in st.session_state.get("extracted", []): st.markdown(f"- {line}")
    st.caption("Keyword-based extraction for the MVP. Local-LLM extraction is a planned next step.")

st.divider()
st.subheader("Giveaway tracker")
rows = conn.execute("SELECT * FROM giveaways ORDER BY created_at DESC").fetchall()
if not rows: st.write("No giveaways saved yet. Search YouTube or add one manually.")
else:
    selected_status = st.multiselect("Filter by status", STATUSES, default=["Found","Review","Ready to enter"])
    visible = [r for r in rows if not selected_status or r["status"] in selected_status]
    for r in visible:
        with st.expander(f"{r['title']} · {r['platform']} · Heuristic score {r['credibility']}/100"):
            st.markdown(f"[Open giveaway]({r['url']})")
            st.write(f"**Creator:** {r['creator'] or 'Unknown'} | **Prize:** {r['prize_type']} ({r['prize_value']:,.2f} {r['currency']})")
            st.write(f"**Deadline:** {r['deadline'] or 'Not identified'} | **Eligibility:** {r['eligibility'] or 'Not checked'}")
            if r["risk_notes"]: st.warning(r["risk_notes"])
            checklist = extract_instructions(r["instructions"])
            st.write("**Likely entry steps**")
            if checklist:
                for line in checklist: st.markdown(f"- {line}")
            else: st.write("No instructions extracted. Review official rules.")
            rules = st.text_area("Source text / rules", value=r["instructions"], key=f"rules_{r['id']}", height=100)
            draft = st.text_area("Prepared entry (edit before use)", value=r["prepared_entry"], key=f"draft_{r['id']}", height=80)
            a,b,c = st.columns([2,2,1])
            status = a.selectbox("Status", STATUSES, index=STATUSES.index(r["status"]) if r["status"] in STATUSES else 0, key=f"status_{r['id']}")
            if b.button("Save review", key=f"update_{r['id']}"):
                score, flags, _ = assess(r["title"], r["creator"], r["url"], rules)
                conn.execute("UPDATE giveaways SET instructions=?,prepared_entry=?,status=?,credibility=?,risk_notes=? WHERE id=?",
                             (rules,draft,status,score,"; ".join(flags),r["id"]))
                conn.commit(); st.success("Review saved."); st.rerun()
            if c.button("Delete", key=f"delete_{r['id']}"):
                conn.execute("DELETE FROM giveaways WHERE id=?",(r["id"],)); conn.commit(); st.rerun()

st.divider()
st.caption("Scores are heuristics, not proof. Verify official rules, eligibility, host identity, and winner history independently. Never share passwords, OTPs, recovery phrases, or pay an upfront prize-claim fee.")
