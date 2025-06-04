from apscheduler.schedulers.background import BackgroundScheduler
from ai_generator import generate_blog_post
from seo_fetcher import get_seo_data
from db import save_post_to_mongo, reset_is_today_flags, get_trending_blogs_today
from datetime import datetime
import os
import logging

# Configure logging for debug/info output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Change this keyword as needed for your demo/testing
PREDEFINED_KEYWORD = "The Metaverse for Work"

def write_daily_post():
    """
    Generate and save a new automated blog post for the predefined keyword.
    - Resets 'is_today' for all existing posts so only today's are True.
    - Uses a hardcoded keyword (no user input for automation).
    - Stores post in MongoDB and as a local Markdown file.
    - Prevents duplicate scheduled posts for the same day/keyword.
    """
    try:
        reset_is_today_flags()  # Reset 'today' flag from previous posts

        # Check for an existing automated post for today to avoid duplicates
        todays_automated_posts = get_trending_blogs_today()
        if todays_automated_posts:
            logging.info("[Scheduler] Today's automated blog already exists, skipping creation.")
            return

        keyword = PREDEFINED_KEYWORD
        seo = get_seo_data(keyword)
        title, blog = generate_blog_post(keyword, seo)

        # Save blog to local posts folder
        os.makedirs("posts", exist_ok=True)
        filename = f"posts/daily_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(blog)

        # Save blog to MongoDB, marked as an automated (scheduler) post
        save_post_to_mongo(keyword, seo, blog, title=title, source="scheduler")
        logging.info(f"[Scheduler] Blog saved: {filename}")

    except Exception as e:
        logging.error(f"[Scheduler] Error in write_daily_post: {e}")

def start_scheduler():
    """
    Start the daily background scheduler that calls write_daily_post() at 3am UTC.
    You can change the schedule time for testing/demo, but use 3am UTC for final.
    """
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(write_daily_post, "cron", hour=3, minute=0)  # Run at 3am UTC by default
        scheduler.start()
        logging.info("[Scheduler] BackgroundScheduler started.")
    except Exception as e:
        logging.error(f"[Scheduler] Error starting scheduler: {e}")

