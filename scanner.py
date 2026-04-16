import json
import os
import time
from datetime import datetime
import praw
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME,
    REDDIT_PASSWORD, REDDIT_USER_AGENT, KEYWORDS, MIN_SCORE,
    SUBREDDITS, COMPETITOR_BRANDS
)

SEEN_FILE = "data/seen_posts.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def get_reddit():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
    )

def score_text(text):
    text_lower = text.lower()
    score = 0
    matched = []
    for points, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                score += points
                matched.append((kw, points))
    return min(score, 10), matched

def is_competitor_mention(text):
    text_lower = text.lower()
    return any(brand in text_lower for brand in COMPETITOR_BRANDS)

def scan_subreddit(reddit, subreddit_name, seen, limit=25):
    results = []
    try:
        sub = reddit.subreddit(subreddit_name)
        for post in sub.new(limit=limit):
            if post.id in seen:
                continue
            full_text = f"{post.title} {post.selftext}"
            score, matched = score_text(full_text)
            competitor = is_competitor_mention(full_text)
            if score >= MIN_SCORE or competitor:
                results.append({
                    "id": post.id,
                    "type": "post",
                    "subreddit": subreddit_name,
                    "title": post.title,
                    "body": post.selftext[:500],
                    "url": f"https://reddit.com{post.permalink}",
                    "score": score,
                    "matched_keywords": matched,
                    "competitor_mention": competitor,
                    "author": str(post.author),
                    "created_utc": post.created_utc,
                    "found_at": datetime.now().isoformat(),
                })
            seen.add(post.id)

        post_comments = sub.comments(limit=limit)
        for comment in post_comments:
            if comment.id in seen:
                continue
            score, matched = score_text(comment.body)
            competitor = is_competitor_mention(comment.body)
            if score >= MIN_SCORE or competitor:
                results.append({
                    "id": comment.id,
                    "type": "comment",
                    "subreddit": subreddit_name,
                    "title": f"Comment in thread",
                    "body": comment.body[:500],
                    "url": f"https://reddit.com{comment.permalink}",
                    "score": score,
                    "matched_keywords": matched,
                    "competitor_mention": competitor,
                    "author": str(comment.author),
                    "created_utc": comment.created_utc,
                    "found_at": datetime.now().isoformat(),
                })
            seen.add(comment.id)

    except Exception as e:
        print(f"[Scanner] Error scanning r/{subreddit_name}: {e}")

    return results

def run_scan(tier="tier1"):
    reddit = get_reddit()
    seen = load_seen()
    all_results = []
    for subreddit_name in SUBREDDITS.get(tier, []):
        print(f"[Scanner] Scanning r/{subreddit_name} ({tier})")
        results = scan_subreddit(reddit, subreddit_name, seen)
        all_results.extend(results)
        time.sleep(2)
    save_seen(seen)
    print(f"[Scanner] Found {len(all_results)} relevant posts in {tier}")
    return all_results
