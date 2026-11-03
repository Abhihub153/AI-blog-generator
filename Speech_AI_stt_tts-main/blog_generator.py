
import torch
from transformers import pipeline

MODEL_NAME = "HuggingFaceTB/SmolLM2-360M-Instruct"


def load_model():
    """Load the text-generation model (downloads on first run)."""
    device = 0 if torch.cuda.is_available() else -1
    print("Loading model... (first run downloads ~700 MB)")
    print("Device:", "GPU" if device == 0 else "CPU")
    generator = pipeline("text-generation", model=MODEL_NAME, device=device)
    print("Model loaded successfully!\n")
    return generator


def ask(generator, instruction, max_new_tokens=250, temperature=0.7):
    """Send one instruction to the model and return the reply text."""
    messages = [{"role": "user", "content": instruction}]
    result = generator(
        messages,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=temperature,
        return_full_text=False,
    )
    output = result[0]["generated_text"]

    # Different transformers versions return either a string or a message list.
    if isinstance(output, list):
        output = output[-1]["content"]
    return output.strip()


def generate_title(generator, topic, tone):
    text = ask(
        generator,
        f"Write one catchy blog post title about '{topic}'. "
        f"Tone: {tone}. Return only the title, nothing else.",
        max_new_tokens=30,
    )
    return text.splitlines()[0].strip(' "*#')


def generate_outline(generator, topic, num_sections):
    text = ask(
        generator,
        f"List {num_sections} short section headings for a blog post about "
        f"'{topic}'. Return one heading per line, no numbering, no extra text.",
        max_new_tokens=80,
    )
    headings = [line.strip(" -*#0123456789.") for line in text.splitlines()]
    headings = [h for h in headings if h]
    return headings[:num_sections]


def generate_intro(generator, topic, tone, language):
    return ask(
        generator,
        f"Write a short introduction (about 80 words) for a blog post about "
        f"'{topic}'. Tone: {tone}. Language: {language}. Return only the text.",
        max_new_tokens=150,
    )


def generate_section(generator, topic, heading, tone, language):
    return ask(
        generator,
        f"Write one paragraph (about 100 words) for the blog section "
        f"'{heading}' in a post about '{topic}'. Tone: {tone}. "
        f"Language: {language}. Return only the paragraph.",
        max_new_tokens=200,
    )


def generate_conclusion(generator, topic, tone, language):
    return ask(
        generator,
        f"Write a short conclusion (about 60 words) for a blog post about "
        f"'{topic}'. Tone: {tone}. Language: {language}. "
        f"End with a call to action. Return only the text.",
        max_new_tokens=120,
    )


def generate_blog(generator, topic, tone="Friendly", language="English",
                  num_sections=3):
    """Generate a complete blog post and return it as one string."""
    print("Writing title...")
    title = generate_title(generator, topic, tone)

    print("Planning sections...")
    headings = generate_outline(generator, topic, num_sections)

    print("Writing introduction...")
    intro = generate_intro(generator, topic, tone, language)

    parts = [f"# {title}", "", intro, ""]

    for i, heading in enumerate(headings, start=1):
        print(f"Writing section {i}/{len(headings)}: {heading}")
        body = generate_section(generator, topic, heading, tone, language)
        parts += [f"## {heading}", "", body, ""]

    print("Writing conclusion...")
    conclusion = generate_conclusion(generator, topic, tone, language)
    parts += ["## Conclusion", "", conclusion]

    return "\n".join(parts)
