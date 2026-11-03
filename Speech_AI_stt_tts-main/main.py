
import sys

from blog_generator import load_model, generate_blog
from utils import save_blog


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 30)
    print("AI BLOG GENERATOR")
    print("=" * 30)

    topic = input("Blog topic (e.g. Machine Learning for Beginners): ").strip()
    tone = input("Tone (e.g. Friendly, Professional): ").strip() or "Friendly"
    language = input("Language (e.g. English, Hindi, Telugu): ").strip() or "English"
    sections = input("Number of sections (default 3): ").strip()
    num_sections = int(sections) if sections.isdigit() else 3

    if not topic:
        print("Please enter a topic.")
        return

    generator = load_model()

    print("\nGenerating your blog... this can take a few minutes on CPU.\n")
    blog = generate_blog(generator, topic, tone, language, num_sections)
    path = save_blog(blog, topic)

    print("\n" + "=" * 30)
    print("YOUR BLOG POST")
    print("=" * 30 + "\n")
    print(blog)

    print(f"\nSaved to {path}")


if __name__ == "__main__":
    main()
