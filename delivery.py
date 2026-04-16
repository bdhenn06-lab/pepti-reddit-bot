import json
import os
from datetime import datetime
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, TWILIO_TO, AUTO_POST

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

PENDING_FILE = "data/pending_approvals.json"
LOG_FILE = "data/responses_log.json"

def load_pending():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_pending(pending):
    with open(PENDING_FILE, "w") as f:
        json.dump(pending, f, indent=2)

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def send_sms(body):
    try:
        message = client.messages.create(
            body=body,
            from_=TWILIO_FROM,
            to=TWILIO_TO,
        )
        print(f"[Delivery] SMS sent: {message.sid}")
        return True
    except Exception as e:
        print(f"[Delivery] SMS error: {e}")
        return False

def format_alert(post, generated):
    score = post.get("score", 0)
    subreddit = post.get("subreddit", "")
    title = post.get("title", "")[:80]
    url = post.get("url", "")
    mode = generated.get("mode", "A")
    competitor = post.get("competitor_mention", False)
    options = generated.get("options", [])

    competitor_flag = " ⚠️ COMPETITOR MENTION" if competitor else ""
    header = f"🧬 PEPTI REDDIT ALERT{competitor_flag}\n"
    header += f"r/{subreddit} | Score: {score}/10 | Mode {mode}\n"
    header += f"'{title}'\n"
    header += f"URL: {url}\n\n"

    body = ""
    if options:
        body += f"OPTION 1 (recommended):\n{options[0][:300]}\n\n"
        if len(options) > 1:
            body += f"OPTION 2:\n{options[1][:200]}\n\n"

    footer = "Reply:\nY1 = post option 1\nY2 = post option 2\nY3 = post option 3\nN = skip"

    full_message = header + body + footer
    if len(full_message) > 1600:
        full_message = header + f"OPTION 1:\n{options[0][:400] if options else 'No options generated'}\n\n" + footer

    return full_message

def deliver_alert(post, generated, reddit=None):
    pending = load_pending()
    post_id = post.get("id")
    pending[post_id] = {
        "post": post,
        "generated": generated,
        "delivered_at": datetime.now().isoformat(),
        "status": "pending",
    }
    save_pending(pending)

    if AUTO_POST and generated.get("options"):
        auto_post_response(post, generated, reddit, option_index=0)
        return

    message = format_alert(post, generated)
    send_sms(message)

def auto_post_response(post, generated, reddit, option_index=0):
    if not reddit:
        print("[Delivery] No reddit instance for auto-post")
        return
    options = generated.get("options", [])
    if not options or option_index >= len(options):
        print("[Delivery] No valid option to post")
        return
    response_text = options[option_index]
    try:
        submission = reddit.submission(id=post.get("id"))
        submission.reply(response_text)
        log_response(post, response_text, "auto")
        print(f"[Delivery] Auto-posted to {post.get('url')}")
    except Exception as e:
        print(f"[Delivery] Auto-post error: {e}")

def log_response(post, response_text, method):
    log = load_log()
    log.append({
        "post_id": post.get("id"),
        "subreddit": post.get("subreddit"),
        "url": post.get("url"),
        "response": response_text,
        "method": method,
        "posted_at": datetime.now().isoformat(),
    })
    save_log(log)

def send_daily_digest(all_found, all_posted):
    message = f"📊 PEPTI REDDIT DAILY DIGEST\n"
    message += f"Posts found: {len(all_found)}\n"
    message += f"Responses posted: {len(all_posted)}\n\n"

    subreddit_counts = {}
    for post in all_found:
        sub = post.get("subreddit", "unknown")
        subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1

    top_subs = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    message += "Top subreddits:\n"
    for sub, count in top_subs:
        message += f"  r/{sub}: {count}\n"

    send_sms(message)
