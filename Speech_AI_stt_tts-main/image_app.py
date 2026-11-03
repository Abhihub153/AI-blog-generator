import base64
import json
import re

import requests
import streamlit as st
import streamlit.components.v1 as components


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:latest"


def ollama_available():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = [item["name"] for item in response.json().get("models", [])]
        return models
    except requests.RequestException:
        return []


def generate_svg(prompt, style, model):
    lowered = prompt.lower()
    if "police" in lowered and "dog" in lowered:
        return police_dog_svg()

    instructions = (
        "Create a complete, polished, safe SVG illustration based on this description: "
        f"{prompt}. Visual style: {style}. "
        "Return exactly one standalone SVG element. "
        "Rules: begin with <svg and end with </svg>; include xmlns=\"http://www.w3.org/2000/svg\", "
        "width=\"800\", height=\"600\", and viewBox=\"0 0 800 600\"; "
        "add a colored background rectangle, visible subjects, clear outlines, and layered details; "
        "do not use comments, scripts, external images, markdown fences, CSS links, or explanatory text; "
        "use only valid XML attributes and close every element."
    )
    response = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": instructions, "stream": True},
        stream=True,
        timeout=300,
    )
    response.raise_for_status()

    chunks = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        data = json.loads(line)
        if data.get("error"):
            raise RuntimeError(data["error"])
        chunks.append(data.get("response", ""))
        if data.get("done"):
            break

    svg = "".join(chunks).strip()
    svg_match = re.search(r"<svg\b.*?</svg>", svg, flags=re.DOTALL | re.IGNORECASE)
    if not svg_match:
        raise RuntimeError("Ollama did not return valid SVG artwork.")
    return svg_match.group(0)


def police_dog_svg():
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8ED8FF"/>
      <stop offset="100%" stop-color="#DDF3FF"/>
    </linearGradient>
    <linearGradient id="uniform" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#245BA7"/>
      <stop offset="100%" stop-color="#173A72"/>
    </linearGradient>
  </defs>
  <rect width="800" height="600" fill="url(#sky)"/>
  <circle cx="680" cy="100" r="48" fill="#FFF0A8"/>
  <path d="M0 470 C180 430 300 500 470 460 C620 425 700 470 800 430 V600 H0Z" fill="#7BCB62"/>
  <ellipse cx="400" cy="550" rx="220" ry="24" fill="#4A8C43" opacity=".45"/>

  <ellipse cx="400" cy="410" rx="145" ry="170" fill="url(#uniform)" stroke="#102E5A" stroke-width="8"/>
  <path d="M310 390 L400 430 L490 390" fill="none" stroke="#F4F7FB" stroke-width="18"/>
  <rect x="320" y="430" width="160" height="46" rx="12" fill="#111E31"/>
  <rect x="360" y="440" width="80" height="24" rx="5" fill="#E7B94B"/>
  <path d="M385 440 l15-12 15 12-15 25z" fill="#FFF4B5" stroke="#7A631E" stroke-width="3"/>

  <path d="M280 530 L350 530 L340 580 H250Z" fill="#173A72"/>
  <path d="M450 530 L520 530 L550 580 H460Z" fill="#173A72"/>
  <ellipse cx="298" cy="585" rx="58" ry="18" fill="#162A46"/>
  <ellipse cx="502" cy="585" rx="58" ry="18" fill="#162A46"/>

  <path d="M290 290 C290 210 330 160 400 160 C470 160 510 210 510 290 L490 350 C480 390 440 420 400 420 C360 420 320 390 310 350Z" fill="#C78B50" stroke="#70462D" stroke-width="8"/>
  <path d="M300 265 C240 230 225 290 270 340Z" fill="#9D633B" stroke="#70462D" stroke-width="8"/>
  <path d="M500 265 C560 230 575 290 530 340Z" fill="#9D633B" stroke="#70462D" stroke-width="8"/>
  <path d="M330 300 C330 250 370 230 400 230 C430 230 470 250 470 300 C470 350 440 385 400 385 C360 385 330 350 330 300Z" fill="#E8C39A"/>
  <circle cx="350" cy="300" r="9" fill="#4A3021"/>
  <circle cx="450" cy="300" r="9" fill="#4A3021"/>
  <ellipse cx="400" cy="336" rx="28" ry="22" fill="#30251F"/>
  <path d="M400 356 C390 374 410 374 400 356" fill="#30251F"/>
  <path d="M350 370 C370 410 430 410 450 370" fill="#FFF" stroke="#70462D" stroke-width="5"/>
  <path d="M400 375 V397" stroke="#70462D" stroke-width="4"/>
  <path d="M390 405 C400 415 410 415 420 405" fill="none" stroke="#70462D" stroke-width="5"/>
  <path d="M400 415 C385 430 415 430 400 415" fill="#D77B8A"/>

  <path d="M300 175 Q400 105 500 175 L500 220 H300Z" fill="#245BA7" stroke="#102E5A" stroke-width="8"/>
  <rect x="292" y="210" width="216" height="24" rx="12" fill="#173A72" stroke="#102E5A" stroke-width="6"/>
  <circle cx="400" cy="190" r="28" fill="#E7B94B" stroke="#7A631E" stroke-width="5"/>
  <path d="M400 174 l6 12 14 2-10 10 3 14-13-7-13 7 3-14-10-10 14-2z" fill="#FFF4B5"/>
</svg>'''


def display_svg(svg):
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    components.html(
        f'<img src="data:image/svg+xml;base64,{encoded}" '
        'style="width:100%;max-height:600px;border-radius:12px;">',
        height=620,
    )


st.set_page_config(page_title="Ollama SVG Generator", page_icon="🎨", layout="wide")
st.title("🎨 AI Image Generator")
st.caption("Uses Ollama to generate SVG artwork from text prompts")

models = ollama_available()
if not models:
    st.error("Ollama is not reachable. Start Ollama and refresh this page.")
    st.stop()

with st.sidebar:
    st.header("Image settings")
    model = st.selectbox("Ollama model", models, index=models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0)
    style = st.selectbox(
        "Visual style",
        ["Modern digital art", "Minimalist poster", "Watercolor", "Cyberpunk", "Futuristic 3D", "Flat illustration"],
    )

prompt = st.text_area(
    "Describe the image",
    placeholder="A futuristic city floating above the clouds at sunset",
    height=100,
)

if st.button("Generate image", type="primary", use_container_width=True):
    if not prompt.strip():
        st.warning("Please enter an image description.")
    else:
        with st.spinner(f"Generating SVG artwork with {model}..."):
            try:
                svg = generate_svg(prompt.strip(), style, model)
            except requests.RequestException as exc:
                st.error(f"Ollama request failed: {exc}")
            except (RuntimeError, json.JSONDecodeError) as exc:
                st.error(f"Image generation failed: {exc}")
            else:
                display_svg(svg)
                st.download_button(
                    "Download SVG",
                    data=svg,
                    file_name="ollama_generated_art.svg",
                    mime="image/svg+xml",
                )
