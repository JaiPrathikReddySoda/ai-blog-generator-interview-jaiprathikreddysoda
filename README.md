
# AI Blog Generator

## Overview

Welcome to the AI Blog Generator! This project is a complete Python and Flask-based platform that generates human-like, SEO-rich blog posts for any keyword using OpenAI’s most advanced models. You can create blog posts on demand, schedule daily automated content, view a polished blog archive, and integrate with your own workflows via a REST API.  
Whether you're a developer, content manager, or tech enthusiast—this project lets you experience how AI-driven blogging can work in a modern web app.

---

## Key Features

- **One-Click Blog Creation:** Instantly generate a unique, SEO-optimized blog post for any topic through the web UI or API.
- **Modern UI:** Clean, responsive interface for generating, previewing, and archiving blogs.
- **Automated Daily Posting:** Scheduler automatically generates and saves a fresh blog post every day for a chosen keyword.
- **SEO Insights:** Each post includes search volume, difficulty, and CPC data for the keyword.
- **Affiliate Link Support:** Blogs include contextual recommendations with placeholder links.
- **Markdown Output:** All blogs are generated in Markdown, making them easy to style or publish anywhere.
- **Extensible Architecture:** Code is modular—easy to update, extend, or connect to real SEO APIs and databases.
- **RESTful API:** Endpoints available for programmatic access to blog generation and retrieval.

---

## Project Structure

```
ai-blog-generator-interview-jaiprathikreddysoda/
│
├── app.py            # Main Flask app (UI, API, archive, preview, scheduler)
├── ai_generator.py   # Handles OpenAI blog creation
├── seo_fetcher.py    # Returns SEO stats for any keyword
├── scheduler.py      # Runs the daily blog automation
├── db.py             # Manages MongoDB and local file storage
├── requirements.txt  # List of Python dependencies
├── .env.example      # Template for your environment variables
├── README.md         # This documentation
├── posts/            # (Optional) Blog files (Markdown)
├── data/keywords.txt # (Optional) Log of entered keywords
└── ...               # Any helpers or static files
```

---

## Getting Started

### 1. Clone the Project

```bash
git clone https://github.com/JaiPrathikReddySoda/ai-blog-generator-interview-jaiprathikreddysoda.git
cd ai-blog-generator-interview-jaiprathikreddysoda
```

### 2. Set Up Your Python Environment

```bash
python3 -m venv venv
source venv/bin/activate         
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

- Copy the template:
  ```bash
  cp .env.example .env
  ```
- Open `.env` and fill in your OpenAI API key, and choose your model:
  ```
  OPENAI_API_KEY=sk-...
  OPENAI_BLOG_MODEL=gpt-4o
  MONGO_URI=mongodb+srv://..
  ```

---

## How to Use the App

### Run the Flask Web App

```bash
python app.py
```
Open your browser and visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

Here you can:
- Enter a keyword and generate a fresh blog post
- View the latest automated blog from the scheduler
- Browse the full blog archive and preview any post

---

### Use the API Directly

#### Generate a Blog Post

```
GET /generate?keyword=<your_keyword>
```
Example:
```
http://127.0.0.1:5000/generate?keyword=ai%20tools
```
Returns a JSON response with title, blog content (Markdown), and SEO data.  
*Note: API calls do not save posts to your archive—they just return the result.*

#### Get All Stored Blog Posts

```
GET /api/posts
```
**Query Parameters:**
- `source=manual` or `source=scheduler` — filter by post type
- `keyword=<text>` — search by keyword (substring, case-insensitive)
- `limit=<N>` — limit number of results (default 50)

**Example:**
```
http://127.0.0.1:5000/api/posts?source=scheduler&limit=10
```
Returns an array of blog post objects as JSON.

---

## Daily Blog Automation (Scheduler)

This project includes a **built-in daily scheduler** using APScheduler.

- When you start the app, the scheduler runs in the background.
- Every day at midnight (by default), it generates a new blog post for a predefined keyword (edit `PREDEFINED_KEYWORD` in `scheduler.py` to change it).
- The generated blog post is automatically saved, archived, and displayed under "Today's Automated Blog".

**You don’t need to set up a separate cron job or shell script—just keep the Flask app running and automation works!**

*If you want to use system cron jobs instead, you can adapt the `/generate` API endpoint to be called by a shell script or scheduled task.*

---

## Logging

All major actions, API calls, scheduler events, and errors are logged using Python’s built-in logging module (`logging.info` and `logging.error`).  
You can monitor your terminal output to trace blog generation, storage, and API activity for easier debugging and demonstration.

---

## Customization

- **Change the OpenAI Model:**  
  Edit `OPENAI_BLOG_MODEL` in your `.env` file.
- **Use Real SEO Data:**  
  Plug in a live SEO API in `seo_fetcher.py` instead of the mock function.
- **Change Storage:**  
  By default, the app uses MongoDB for storage. You can switch to file-based storage or connect any other database by editing `db.py`.

---

## Troubleshooting & Tips

- If you see OpenAI errors, check your API key and model access.
- For scheduler issues, make sure the Flask process keeps running (use a process manager in production).
- MongoDB problems? Double-check your URI and permissions in `db.py` or your environment.

---

## Example Output

See the included blogs under posts folder for seeing how generated blog post looks like—complete with headings, recommendations, and SEO stats!

---

## Security

- All blog Markdown is rendered to HTML using the `markdown2` library to reduce risk of HTML/script injection.
- Always validate and sanitize any integration code or user input if deploying in production.

---

## License

For educational and demonstration purposes only.

---

## Author

**Jai Prathik Reddy Soda**  
Contact: jaiprathik.reddys@gmail.com
