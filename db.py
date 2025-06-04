import os
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import Dict, Optional, List, Any

# Load environment variables from .env for MongoDB connection string
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB connection setup
client = MongoClient(MONGO_URI)
db = client["blogDB"]
collection = db["blog_posts"]

def save_post_to_mongo(
    keyword: str,
    seo: Dict[str, Any],
    content: str,
    source: str = "scheduler",
    title: Optional[str] = None
) -> str:
    """
    Save a blog post to MongoDB with UTC timestamp.
    The 'is_today' flag is always set True on insert;
    it is reset for all posts at the start of every scheduler run.
    """
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    post = {
        "keyword": keyword.strip(),
        "title": title if title else "Untitled",
        "seo": seo,
        "content": content,
        "source": source,  # "scheduler" for auto, "manual" for user
        "date": now_utc,
        "is_today": True
    }
    result = collection.insert_one(post)
    print(f"[MongoDB] Blog saved with ID: {result.inserted_id}")
    return str(result.inserted_id)

def reset_is_today_flags() -> None:
    """
    Reset the 'is_today' flag for ALL blog posts.
    This is called at the start of each daily scheduled blog run,
    so only today's new blog(s) are marked as 'is_today': True.
    """
    result = collection.update_many({}, {"$set": {"is_today": False}})
    print(f"[MongoDB] is_today flags reset on {result.modified_count} posts.")

def get_trending_blogs_today() -> List[Dict[str, Any]]:
    """
    Fetch all automated (scheduler) blog posts for today (UTC).
    This powers the /scheduled page.
    """
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now_utc.replace(hour=23, minute=59, second=59, microsecond=999999)
    posts = collection.find({
        "source": "scheduler",
        "date": {"$gte": today_start, "$lte": today_end}
    }).sort("date", -1)
    # Only show posts for TODAY, regardless of is_today flag (is_today is an extra helper for UI, not filtering here)
    return [{**post, "_id": str(post["_id"])} for post in posts]

def get_all_blogs() -> List[Dict[str, Any]]:
    """
    Fetch all blog posts, both manual and scheduler, sorted newest first.
    This powers the /archive page.
    """
    posts = collection.find({}).sort("date", -1)
    return [{**post, "_id": str(post["_id"])} for post in posts]
