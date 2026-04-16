import time
import os
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from scanner import run_scan
from generator import generate_responses
from delivery import deliver_alert, send_daily_digest, log_response
from analytics import init_db, log_post_found, send_weekly_report
from trend_spotter import scan_for_trends, get_rising_compounds, format_trend_alert
from config import TWILIO_FROM, TWILIO_TO, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

from twilio.rest import Client

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

os.makedirs("data", exist_ok=True)

daily_found = []
daily_posted = []

def send_sms(body):
    try:
        twilio_client.messages.create(body=body, from_=TWILIO_FROM, to=TWILIO_TO)
    except Exception as e:
        print(f"[Main] SMS error: {e}")

def run_tier(tier):
    print(f"\n[Main] Running scan: {tier} at {datetime.now().strftime('%H:%M:%S')}")
    try:
        results = run_scan(tier)
        for post in results:
            log_post_found(post)
            daily_found.append(post)
            print(f"[Main] Processing: {post['title'][:60]} (score: {post['score']})")
            generated = generate_responses(post)
            if generated.get("options"):
                deliver_alert(post, generated)
                time.sleep(3)
    except Exception as e:
        print(f"[Main] Scan error for {tier}: {e}")

def run_tier1():
    run_tier("tier1")

def run_tier2():
    run_tier("tier2")

def run_tier3():
    run_tier("tier3")

def run_tier4():
    run_tier("tier4")

def run_daily_digest():
    print("[Main] Sending daily digest")
    send_daily_digest(daily_found, daily_posted)
    daily_found.clear()
    daily_posted.clear()

def run_trend_report():
    print("[Main] Running trend scan")
    try:
        top_compounds = scan_for_trends()
        rising = get_rising_compounds()
        if top_compounds or rising:
            message = format_trend_alert(top_compounds, rising)
            send_sms(message)
    except Exception as e:
        print(f"[Main] Trend error: {e}")

def run_weekly_report():
    print("[Main] Sending weekly report")
    send_weekly_report()

def startup_message():
    send_sms(
        "🧬 Pepti Reddit Bot is LIVE\n"
        "Scanning 20 subreddits 24/7\n"
        "You'll get alerts when relevant posts are found.\n"
        "Reply Y1/Y2/Y3 to approve, N to skip."
    )

if __name__ == "__main__":
    print("[Main] Initializing Pepti Reddit Bot...")
    init_db()
    startup_message()

    scheduler = BlockingScheduler()

    scheduler.add_job(
        run_tier1,
        IntervalTrigger(minutes=10),
        id="tier1",
        name="Tier 1 scan (core subreddits)",
        max_instances=1,
    )

    scheduler.add_job(
        run_tier2,
        IntervalTrigger(minutes=30),
        id="tier2",
        name="Tier 2 scan",
        max_instances=1,
    )

    scheduler.add_job(
        run_tier3,
        IntervalTrigger(minutes=60),
        id="tier3",
        name="Tier 3 scan",
        max_instances=1,
    )

    scheduler.add_job(
        run_tier4,
        IntervalTrigger(minutes=120),
        id="tier4",
        name="Tier 4 scan",
        max_instances=1,
    )

    scheduler.add_job(
        run_daily_digest,
        CronTrigger(hour=20, minute=0),
        id="daily_digest",
        name="Daily digest at 8pm",
    )

    scheduler.add_job(
        run_trend_report,
        CronTrigger(hour=9, minute=0),
        id="trend_report",
        name="Daily trend report at 9am",
    )

    scheduler.add_job(
        run_weekly_report,
        CronTrigger(day_of_week="sun", hour=10, minute=0),
        id="weekly_report",
        name="Weekly report Sunday 10am",
    )

    print("[Main] All jobs scheduled. Bot is running.")
    print("[Main] Schedules:")
    print("  Tier 1 (core): every 10 min")
    print("  Tier 2: every 30 min")
    print("  Tier 3: every 60 min")
    print("  Tier 4: every 2 hours")
    print("  Daily digest: 8pm")
    print("  Trend report: 9am daily")
    print("  Weekly report: Sunday 10am")

    run_tier1()

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[Main] Bot stopped.")
        scheduler.shutdown()
