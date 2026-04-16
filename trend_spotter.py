import json
import os
from datetime import datetime
from collections import Counter
import praw
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME,
    REDDIT_PASSWORD, REDDIT_USER_AGENT, SUBREDDITS
)

TRENDS_FILE = "data/trends.json"

COMPOUNDS = [
    "bpc-157", "bpc157", "tb-500", "tb500", "semax", "bromantane",
    "epithalon", "mk-677", "mk677", "igf-1", "igf1", "ghk-cu",
    "melanotan", "aod-9604", "ipamorelin", "cjc-1295", "dihexa",
    "selank", "pt-141", "pt141", "kisspeptin", "follistatin",
    "ghrp-6", "ghrp6", "hexarelin", "tesamorelin", "sermorelin",
    "tirzepatide", "semaglutide", "retatrutide", "cagrilintide",
]

def load_trends():
    if os.path.exists(TRENDS_FILE):
        with open(TRENDS_FILE, "r") as f:
            return json.load(f)
    return {"weekly": {}, "history": []}

def save_trends(trends):
    with open(TRENDS_FILE, "w") as f:
        json.dump(trends, f, indent=2)

def get_reddit():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
    )

def scan_for_trends():
    reddit = get_reddit()
    compound_counter = Counter()
    all_subs = []
    for tier_subs in SUBREDDITS.values():
        all_subs.extend(tier_subs)

    for subreddit_name in all_subs:
        try:
            sub = reddit.subreddit(subreddit_name)
            for post in sub.hot(limit=50):
                text = f"{post.title} {post.selftext}".lower()
                for compound in COMPOUNDS:
                    if compound in text:
                        compound_counter[compound] += 1
        except Exception as e:
            print(f"[Trends] Error scanning r/{subreddit_name}: {e}")

    trends = load_trends()
    week_key = datetime.now().strftime("%Y-W%W")

    if week_key not in trends["weekly"]:
        trends["weekly"][week_key] = {}

    for compound, count in compound_counter.most_common(20):
        prev = trends["weekly"].get(week_key, {}).get(compound, 0)
        trends["weekly"][week_key][compound] = prev + count

    trends["history"].append({
        "scanned_at": datetime.now().isoformat(),
        "top_compounds": compound_counter.most_common(10),
    })

    if len(trends["history"]) > 100:
        trends["history"] = trends["history"][-100:]

    save_trends(trends)
    return compound_counter.most_common(10)

def get_rising_compounds():
    trends = load_trends()
    weeks = sorted(trends["weekly"].keys())
    if len(weeks) < 2:
        return []

    current_week = trends["weekly"].get(weeks[-1], {})
    prev_week = trends["weekly"].get(weeks[-2], {}) if len(weeks) > 1 else {}

    rising = []
    for compound, count in current_week.items():
        prev_count = prev_week.get(compound, 0)
        if prev_count == 0 and count > 2:
            rising.append((compound, count, "new"))
        elif prev_count > 0:
            growth = (count - prev_count) / prev_count
            if growth > 0.5:
                rising.append((compound, count, f"+{int(growth*100)}%"))

    return sorted(rising, key=lambda x: x[1], reverse=True)[:5]

def format_trend_alert(top_compounds, rising):
    message = "📈 PEPTI TREND REPORT\n\n"
    message += "Top compounds this week:\n"
    for compound, count in top_compounds[:5]:
        message += f"  {compound}: {count} mentions\n"

    if rising:
        message += "\n🚀 Rising compounds:\n"
        for compound, count, change in rising:
            message += f"  {compound}: {change}\n"
        message += "\nConsider creating content on rising compounds first."

    return message
