
import re
from pathlib import Path

OUTPUT_DIR = Path("output")


def make_filename(topic):
    """Turn a topic into a safe file name, e.g. 'AI in Healthcare' -> ai_in_healthcare."""
    slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")
    return slug or "blog"


def save_blog(blog_text, topic):
    """Save the blog as a Markdown file inside the output/ folder."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{make_filename(topic)}.md"
    path.write_text(blog_text, encoding="utf-8")
    return path
