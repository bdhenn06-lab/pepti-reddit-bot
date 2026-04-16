# Pepti Reddit Intelligence Bot

Monitors 20 subreddits 24/7 for relevant posts, generates responses in the Pepti voice, and delivers them to your phone for approval.

---

## Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Create a Reddit App
1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app"
3. Select "script"
4. Name it anything (e.g. "PeptiBot")
5. Set redirect URI to http://localhost:8080
6. Copy the client_id (under the app name) and client_secret

### 3. Configure your .env file
Fill in all values in .env:
- REDDIT_CLIENT_ID — from step 2
- REDDIT_CLIENT_SECRET — from step 2
- REDDIT_USERNAME — your Reddit account username
- REDDIT_PASSWORD — your Reddit account password
- REDDIT_USER_AGENT — format: PeptiBot/1.0 by u/yourusername
- ANTHROPIC_API_KEY — your Anthropic API key
- TWILIO_ACCOUNT_SID — from twilio.com console
- TWILIO_AUTH_TOKEN — from twilio.com console
- TWILIO_FROM_NUMBER — your Twilio phone number
- TWILIO_TO_NUMBER — your personal phone number
- AUTO_POST — set to "false" to start (approval mode)
- QUIZ_URL — your Pepti quiz URL

### 4. Run the bot
```bash
python main.py
```

---

## How it works

The bot runs 4 scanning tiers on different intervals:

| Tier | Subreddits | Interval |
|------|-----------|----------|
| 1 | r/Peptides, r/Biohacking, r/Nootropics, r/maleoptimization, r/longevity | Every 10 min |
| 2 | r/Supplements, r/bodybuilding, r/gainit, r/hormones, r/sportsscience | Every 30 min |
| 3 | r/entrepreneur, r/startups, r/college, r/youngentrepreneurs | Every hour |
| 4 | r/fitness, r/nutrition, r/sleep, r/ADHD | Every 2 hours |

---

## Scoring system

Posts are scored 1-10 based on keyword relevance:
- Score 10: Direct requests for peptide recommendations
- Score 8: Specific compound mentions (BPC-157, Semax, etc.)
- Score 6: Related pain points (brain fog, slow recovery, etc.)
- Score 4: General optimization topics

Only posts scoring 7+ trigger an alert (configurable via MIN_SCORE in .env)

---

## Response modes

The bot automatically selects the right response mode:

- Mode A: Pure value, zero brand mention. Used for most posts.
- Mode B: Value + soft quiz mention at the end. Used for high-intent posts.
- Mode C: Direct resource mention with quiz link. Only when explicitly asked.

---

## SMS alerts

When a relevant post is found you get a text with:
- Subreddit and relevance score
- Post title and URL
- 3 response options
- Instructions: Reply Y1/Y2/Y3 to post, N to skip

Note: SMS reply processing requires additional webhook setup with Twilio.
For now, manually copy the response from the text and post it on Reddit.

---

## Scheduled reports

- 9am daily: Trending compound report
- 8pm daily: Daily digest (posts found, responses sent)
- Sunday 10am: Weekly performance report

---

## Auto-post mode

When you're ready to enable auto-posting:
1. Set AUTO_POST=true in .env
2. Make sure your Reddit account has sufficient karma (200+)
3. The bot will post Option 1 automatically

---

## Running 24/7 on Windows (Surface Pro)

Option 1 - Run in background:
```bash
pythonw main.py
```

Option 2 - Windows Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "When computer starts"
4. Set action to run: python C:\path\to\pepti_reddit_bot\main.py
5. Check "Run whether user is logged on or not"

Option 3 - Run as Windows Service using NSSM:
1. Download NSSM from nssm.cc
2. Run: nssm install PeptiRedditBot
3. Set path to python.exe and arguments to main.py
4. Start the service

---

## File structure

```
pepti_reddit_bot/
├── main.py           — Master scheduler
├── scanner.py        — Reddit post/comment scanner
├── generator.py      — AI response generator
├── delivery.py       — SMS delivery system
├── analytics.py      — Performance tracking
├── trend_spotter.py  — Compound trend detection
├── config.py         — All settings and keywords
├── .env              — Your credentials (never share this)
├── requirements.txt  — Python dependencies
└── data/
    ├── seen_posts.json      — Tracks processed posts
    ├── pending_approvals.json — Awaiting your approval
    ├── responses_log.json   — History of all responses
    ├── trends.json          — Compound trend data
    └── analytics.db         — SQLite analytics database
```

---

## Important notes

1. Never use a brand new Reddit account. Warm it up for 2-4 weeks first.
2. Never mention dosing or sourcing in any response.
3. Never identify the account as Pepti or any brand.
4. Keep responses genuinely helpful — the value comes first.
5. Start with approval mode (AUTO_POST=false) until you trust the output.
