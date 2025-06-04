import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Use the OpenAI blog model from environment or default to gpt-4o
OPENAI_BLOG_MODEL = os.getenv("OPENAI_BLOG_MODEL", "gpt-4o")

def classify_keyword_type(keyword: str) -> str:
    """
    Classifies the keyword into one of several types for contextual awareness.
    """
    prompt = (
        f'Classify the keyword "{keyword}" into one of: '
        '[product, service, career, trend, tool, concept, event, place, other]. '
        'Only return the category name.'
    )
    response = client.chat.completions.create(
        model=OPENAI_BLOG_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip().lower()

def generate_blog_title(keyword: str) -> str:
    """
    Generates a catchy, SEO-friendly blog title.
    """
    prompt = (
        f'Write a compelling, original blog post title for "{keyword}". '
        'Make it engaging and SEO-friendly. Only the title, no explanation.'
    )
    response = client.chat.completions.create(
        model=OPENAI_BLOG_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def sanitize_utf8(text: str) -> str:
    """
    Ensures output is safe for UTF-8 encoding/decoding.
    """
    return text.encode("utf-8", "replace").decode("utf-8", "ignore")

def remove_horizontal_rules(markdown_text: str) -> str:
    """
    Removes Markdown horizontal rules (---, ***, ___) from the blog content.
    """
    return re.sub(r'^(?:\s*)([-*_]){3,}(?:\s*)$', '', markdown_text, flags=re.MULTILINE)

def generate_blog_post(keyword: str, seo_data: dict) -> tuple:
    """
    Generates a dynamic, adaptive, human-like blog post for the given keyword.
    Lets the model decide structure, headings, and flow for a natural feel.
    Returns (title, markdown blog content).
    """
    keyword_type = classify_keyword_type(keyword)
    title = generate_blog_title(keyword)
    prompt = f"""
You are an expert blogger in 2025, writing for a global online audience.
Compose a highly engaging, original, and SEO-optimized blog post **in Markdown** for the topic: "{keyword}" ({keyword_type}).
- Structure the article naturally: use only the headings, flow, and section types that best fit the keyword and its audience—do **not** use any rigid or predefined template.
- Write in a conversational, human style. Let your voice and personality shine through, adapting tone and depth to the topic (e.g., lively for travel, practical for tech).
- Reference the latest trends, events, or updates relevant to "{keyword}"—write as if you just published it today, with mentions of what’s new, what’s changing, or what people are talking about in 2025.
- Present facts, stories, and insights like an industry insider. If the topic is a product/service/tool, mention actual use cases or new launches. If it’s a trend, discuss what’s driving it right now.
- Organically include 1–2 affiliate-style recommendations for resources, products, or services *relevant* to "{keyword}"—weave these naturally into the flow, using markdown links with placeholder URLs (e.g., [Awesome Gadget](https://affiliate.com/gadget)).
- Share actionable advice, expert tips, or predictions, and add your own subtle commentary, not just facts.
- Summarize the provided SEO stats somewhere in the post for extra authority:  
    • Search Volume: {seo_data.get('search_volume', 'N/A')},  
    • Keyword Difficulty: {seo_data.get('keyword_difficulty', 'N/A')},  
    • Avg CPC: ${seo_data.get('avg_cpc', 'N/A')}.
- Limit the post to about 800 words.  
- Never mention that you are an AI or that this is an automated post.

**Remember:**  
Let the structure, headings, and story feel fresh, timely, and “written today.” No rigid template—just your best blogging instincts for this keyword.
Write the full article only (no title, no explanation, no code blocks, no HTML).
    """
    response = client.chat.completions.create(
        model=OPENAI_BLOG_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.95  # High creativity for uniqueness
    )
    content = response.choices[0].message.content
    content = sanitize_utf8(content)
    content = remove_horizontal_rules(content)
    return title, content
