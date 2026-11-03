import json

import requests
import streamlit as st

from utils import save_blog


OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_with_ollama(topic, tone, language, num_sections, model):
    prompt = (
        "Write a complete blog post with Markdown formatting. "
        f"Topic: {topic}\n"
        f"Tone: {tone}\n"
        f"Language: {language}\n"
        f"Include a title, an introduction, exactly {num_sections} section headings "
        "with paragraphs, and a conclusion. Return only the blog post."
    )
    response = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": prompt, "stream": True},
        stream=True,
        timeout=300,
    )
    response.raise_for_status()

    chunks = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        data = json.loads(line)
        chunks.append(data.get("response", ""))
        if data.get("error"):
            raise RuntimeError(data["error"])
        if data.get("done"):
            break
    return "".join(chunks).strip()


st.set_page_config(page_title="AI Blog Generator", page_icon="✍️", layout="wide")
st.title("✍️ AI Blog Generator")
st.caption("Powered by Ollama")

with st.sidebar:
    st.header("Generation settings")
    model = st.text_input("Ollama model", value="llama3.2:latest")
    tone = st.selectbox(
        "Tone",
        ["Friendly", "Professional", "Casual", "Technical", "Creative"],
    )
    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Telugu", "Tamil"],
    )
    num_sections = st.slider("Number of sections", 1, 8, 3)

topic = st.text_input("Blog topic", placeholder="Machine Learning for Beginners")

if st.button("Generate blog", type="primary", use_container_width=True):
    if not topic.strip():
        st.warning("Please enter a blog topic.")
    else:
        with st.spinner(f"Generating with Ollama model {model}..."):
            try:
                blog = generate_with_ollama(
                    topic.strip(), tone, language, num_sections, model
                )
                path = save_blog(blog, topic.strip())
            except requests.RequestException as exc:
                st.error(
                    "Could not connect to Ollama. Make sure it is running "
                    "and the model is installed. "
                    f"Details: {exc}"
                )
            except (RuntimeError, json.JSONDecodeError) as exc:
                st.error(f"Ollama generation failed: {exc}")
            else:
                st.success(f"Saved to {path}")
                st.markdown(blog)
                st.download_button(
                    "Download Markdown",
                    data=blog,
                    file_name=path.name,
                    mime="text/markdown",
                )
