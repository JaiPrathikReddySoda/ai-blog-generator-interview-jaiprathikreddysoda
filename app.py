from seo_fetcher import get_seo_data
from ai_generator import generate_blog_post
from scheduler import start_scheduler
from db import save_post_to_mongo, get_trending_blogs_today, get_all_blogs, collection
from datetime import datetime
import os
import markdown2
import pytz
from bson.objectid import ObjectId
from flask import Flask, request, redirect, render_template_string, jsonify
import logging

# ---- LOGGING SETUP ----
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
start_scheduler()  # Launch the background scheduler for automated blogs

PACIFIC = pytz.timezone("US/Pacific")

def utc_to_pacific(dt_utc):
    """Convert UTC datetime to US/Pacific time for display."""
    if dt_utc is None:
        return ""
    return dt_utc.astimezone(PACIFIC)

@app.route("/", methods=["GET", "POST"])
def dashboard():
    """
    Main dashboard page. Lets user generate a manual blog post by submitting a keyword.
    """
    if request.method == "POST":
        keyword = request.form.get("keyword")
        if keyword:
            logging.info(f"Manual blog generation requested for keyword: '{keyword}'")
            # Track user-submitted keywords for analytics/auditing
            os.makedirs("data", exist_ok=True)
            with open("data/keywords.txt", "a") as f:
                f.write(f"{keyword.strip()}\n")
            # Generate blog content via OpenAI
            try:
                seo_data = get_seo_data(keyword)
                title, blog = generate_blog_post(keyword, seo_data)
                logging.info(f"Generated manual blog for '{keyword}'.")
            except Exception as e:
                logging.error(f"Error generating manual blog for '{keyword}': {e}")
                return f"Error generating blog for '{keyword}'."
            # Save blog as a local file and in MongoDB (marked as manual)
            os.makedirs("posts", exist_ok=True)
            filename = f"posts/manual_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(blog)
            try:
                post_id = save_post_to_mongo(keyword, seo_data, blog, title=title, source="manual")
                logging.info(f"Manual blog saved to MongoDB with ID: {post_id}")
            except Exception as e:
                logging.error(f"Error saving manual blog to MongoDB: {e}")
                return f"Error saving blog for '{keyword}'."
            return redirect(f"/preview/{post_id}")

    # Render dashboard
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI Blog Generator</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-r from-indigo-50 via-white to-blue-50 min-h-screen py-10 px-4">
        <div class="max-w-4xl mx-auto">
            <div class="bg-white p-6 rounded-xl shadow border mb-8">
                <h2 class="text-2xl font-bold mb-4 text-center">📝 AI Blog Generator</h2>
                <form method="POST" class="flex flex-col sm:flex-row gap-4 items-center justify-center">
                    <input name="keyword" type="text" required placeholder="Enter keyword (e.g., AI tools)"
                        class="flex-1 border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <button type="submit"
                        class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition">
                        Generate
                    </button>
                </form>
                <div class="flex justify-center gap-4 mt-6">
                    <a href="/scheduled" class="bg-blue-100 hover:bg-blue-200 px-4 py-2 rounded">🤖 Today's Automated Blog</a>
                    <a href="/archive" class="bg-yellow-100 hover:bg-yellow-200 px-4 py-2 rounded">🕑 Blog Archive</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route("/scheduled")
def scheduled_blogs_today():
    """
    Card-based page displaying today's automated blog post(s) created by the scheduler (source="scheduler").
    """
    try:
        posts = get_trending_blogs_today()
        utc_today = datetime.utcnow().date()
        for post in posts:
            post["date_pacific"] = utc_to_pacific(post["date"])
            post["is_today"] = post["date"].date() == utc_today
        logging.info(f"Fetched {len(posts)} scheduled (automated) blogs for today.")
    except Exception as e:
        logging.error(f"Error fetching scheduled blogs: {e}")
        posts = []
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Today's Automated Blog</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-br from-blue-50 via-white to-indigo-50 min-h-screen p-6">
        <h1 class="text-2xl font-bold mb-8">🤖 Today's Automated Blog (Scheduled)</h1>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {% for post in posts %}
            <div class="bg-blue-50 rounded-xl shadow p-5 border flex flex-col">
                <div class="font-bold text-lg mb-2">{{ post.title }}</div>
                <div class="text-xs text-gray-500 mb-2">
                    {{ post.date_pacific.strftime('%Y-%m-%d %I:%M %p PT') if post.date_pacific else "" }} |
                    <span class="uppercase text-blue-600">{{ post.source }}</span>
                    {% if post.is_today %}
                        <span class="bg-yellow-100 px-2 py-1 rounded text-yellow-800 ml-2">Today</span>
                    {% endif %}
                </div>
                <a href="/preview/{{ post._id }}" class="mt-auto text-blue-700 text-sm hover:underline">🔗 View Blog</a>
            </div>
        {% endfor %}
        {% if not posts %}
            <div class="col-span-full text-center text-gray-400 mt-10">
                <span class="text-3xl">🤖</span><br>
                No automated blogs generated yet today.
            </div>
        {% endif %}
        </div>
    </body>
    </html>
    """, posts=posts)

@app.route("/archive")
def blog_archive():
    """
    Blog archive page. Lists all blogs (manual and automated), in card format, sorted by date.
    """
    try:
        posts = get_all_blogs()
        utc_today = datetime.utcnow().date()
        for post in posts:
            post["date_pacific"] = utc_to_pacific(post["date"])
            post["is_today"] = post["date"].date() == utc_today
        logging.info(f"Fetched blog archive with {len(posts)} posts.")
    except Exception as e:
        logging.error(f"Error fetching blog archive: {e}")
        posts = []
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Blog Archive</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-br from-yellow-50 via-white to-indigo-50 min-h-screen p-6">
        <h1 class="text-2xl font-bold mb-8">🕑 Blog Archive (All Time)</h1>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {% for post in posts %}
            <div class="bg-white rounded-xl shadow p-5 border flex flex-col">
                <div class="font-bold text-lg mb-2">{{ post.title }}</div>
                <div class="text-xs text-gray-500 mb-2">
                    {{ post.date_pacific.strftime('%Y-%m-%d %I:%M %p PT') if post.date_pacific else "" }} |
                    {% if post.source == "manual" %}
                        <span class="bg-green-100 px-2 py-1 rounded text-green-800">Manual</span>
                    {% else %}
                        <span class="bg-blue-100 px-2 py-1 rounded text-blue-800">Scheduler</span>
                    {% endif %}
                    {% if post.is_today %}
                        <span class="bg-yellow-100 px-2 py-1 rounded text-yellow-800 ml-2">Today</span>
                    {% endif %}
                </div>
                <a href="/preview/{{ post._id }}" class="mt-auto text-blue-700 text-sm hover:underline">🔗 View Blog</a>
            </div>
        {% endfor %}
        {% if not posts %}
            <div class="col-span-full text-center text-gray-400 mt-10">
                <span class="text-3xl">🗂️</span><br>
                No blogs yet.
            </div>
        {% endif %}
        </div>
    </body>
    </html>
    """, posts=posts)

@app.route("/preview/<id>")
def preview_post(id):
    """
    Blog preview page for any individual post by its MongoDB ObjectID.
    Strips the first Markdown heading to avoid double titles and uses a card-style layout.
    """
    try:
        post = collection.find_one({"_id": ObjectId(id)})
        if not post:
            logging.error(f"No blog post found for ID '{id}'.")
            return f"No blog post found for ID '{id}'."
    except Exception as e:
        logging.error(f"Invalid blog post ID: {e}")
        return f"Invalid blog post ID."
    # Strip the first heading line if it matches the title
    markdown_content = post.get("content", "").strip()
    lines = markdown_content.split("\n")
    if lines and lines[0].strip().startswith("#"):
        markdown_content = "\n".join(lines[1:]).strip()
    title = post.get("title", "Untitled")
    pacific_time = utc_to_pacific(post.get("date"))
    keyword = post.get("keyword", "")
    blog_source = post.get("source", "")
    html = markdown2.markdown(markdown_content)
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }} - Blog Preview</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {
                background: linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%);
                min-height: 100vh;
                margin: 0;
            }
        </style>
    </head>
    <body>
        <div class="min-h-screen flex flex-col items-center justify-start py-10 px-2 sm:px-0">
            <div class="max-w-2xl w-full bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-indigo-100">
                <!-- Meta bar -->
                <div class="flex flex-col gap-1 mb-4">
                    <span class="text-xs text-gray-400 uppercase tracking-wider">{{ blog_source }} | {{ pacific_time.strftime('%b %d, %Y %I:%M %p PT') if pacific_time else "" }}</span>
                    <span class="text-xs text-gray-500">Keyword: <span class="font-medium text-indigo-700">{{ keyword }}</span></span>
                </div>
                <!-- Title -->
                <h1 class="text-3xl font-bold mb-6 text-indigo-900">{{ title }}</h1>
                <!-- Blog content -->
                <article class="prose max-w-none prose-indigo prose-lg">{{ html|safe }}</article>
                <!-- Actions -->
                <div class="mt-8 flex gap-4 justify-between items-center">
                    <a href="/archive" class="text-indigo-700 hover:underline text-sm">← Back to Archive</a>
                    <button onclick="window.print()" class="px-3 py-1 bg-indigo-100 hover:bg-indigo-200 text-indigo-800 rounded-lg text-xs">Print</button>
                </div>
            </div>
        </div>
    </body>
    </html>
    """, html=html, title=title, pacific_time=pacific_time, keyword=keyword, blog_source=blog_source)

@app.route("/generate", methods=["GET"])
def api_generate():
    """
    API endpoint: Generate a blog post for a given keyword and return as JSON.
    Usage: /generate?keyword=your_topic
    """
    keyword = request.args.get("keyword")
    if not keyword:
        logging.error("API call to /generate missing 'keyword' param.")
        return jsonify({"error": "Missing keyword"}), 400
    try:
        seo_data = get_seo_data(keyword)
        title, content = generate_blog_post(keyword, seo_data)
        logging.info(f"API blog generated for keyword '{keyword}'.")
        return jsonify({
            "title": title,
            "content": content,
            "seo": seo_data
        })
    except Exception as e:
        logging.error(f"Error generating API blog for '{keyword}': {e}")
        return jsonify({"error": "Failed to generate blog"}), 500

@app.route("/api/posts", methods=["GET"])
def api_get_all_posts():
    """
    API endpoint: Returns all blog posts (manual and automated) as JSON.
    Optional query parameters:
        - source: 'manual' or 'scheduler' to filter
        - keyword: filter by keyword (case-insensitive substring)
        - limit: number of posts to return (default 50)
    """
    try:
        source = request.args.get("source")
        keyword = request.args.get("keyword")
        limit = int(request.args.get("limit", 50))
        # Build MongoDB query
        query = {}
        if source:
            query["source"] = source
        if keyword:
            query["keyword"] = {"$regex": keyword, "$options": "i"}
        # Fetch posts
        posts = list(collection.find(query).sort("date", -1).limit(limit))
        for post in posts:
            post["_id"] = str(post["_id"])
            post["date"] = post["date"].isoformat() if post.get("date") else None
        logging.info(f"Returned {len(posts)} posts from /api/posts endpoint.")
        return jsonify(posts)
    except Exception as e:
        logging.error(f"Error in /api/posts: {e}")
        return jsonify({"error": "Failed to fetch posts"}), 500

if __name__ == "__main__":
    app.run(debug=True)
