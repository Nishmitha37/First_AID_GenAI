import streamlit as st
from groq import Groq
import os
import tempfile
import base64
from streamlit_mic_recorder import mic_recorder

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="MediGuide — AI First Aid Assistant",
    page_icon="assets/favicon.ico",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:wght@600&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1a1a2e;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 780px; }

/* ── Background ── */
.stApp {
    background: #f5f4f0;
}

/* ── Header ── */
.app-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid #e0ddd6;
    margin-bottom: 2rem;
}
.app-header .brand {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2rem;
    font-weight: 600;
    color: #1a1a2e;
    letter-spacing: -0.5px;
}
.app-header .tagline {
    font-size: 0.85rem;
    color: #888;
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* ── Section label ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 0.6rem;
    margin-top: 1.8rem;
}

/* ── Quick select buttons ── */
.stButton > button {
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 6px;
    color: #1a1a2e;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    padding: 0.5rem 0.8rem;
    width: 100%;
    transition: all 0.18s ease;
    letter-spacing: 0.01em;
}
.stButton > button:hover {
    background: #1a1a2e;
    color: #ffffff;
    border-color: #1a1a2e;
    transform: translateY(-1px);
    box-shadow: 0 3px 10px rgba(26,26,46,0.12);
}
.stButton > button:active {
    transform: translateY(0px);
}

/* ── Primary action button ── */
.primary-btn > button {
    background: #c0392b !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    padding: 0.65rem 1.4rem !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
}
.primary-btn > button:hover {
    background: #a93226 !important;
    box-shadow: 0 4px 14px rgba(192,57,43,0.25) !important;
    transform: translateY(-1px) !important;
}

/* ── Text input ── */
.stTextInput > div > div > input {
    border: 1px solid #ddd;
    border-radius: 6px;
    background: #fff;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    padding: 0.65rem 1rem;
    color: #1a1a2e;
    transition: border-color 0.18s;
}
.stTextInput > div > div > input:focus {
    border-color: #1a1a2e;
    box-shadow: 0 0 0 2px rgba(26,26,46,0.06);
}

/* ── File uploader ── */
.stFileUploader > div {
    border: 1.5px dashed #ccc;
    border-radius: 8px;
    background: #fafaf8;
    transition: border-color 0.18s;
}
.stFileUploader > div:hover {
    border-color: #1a1a2e;
}

/* ── Result card ── */
.result-card {
    background: #ffffff;
    border: 1px solid #e8e5df;
    border-radius: 10px;
    padding: 1.8rem 2rem;
    margin-top: 1.5rem;
    line-height: 1.75;
    font-size: 0.92rem;
    color: #2c2c3e;
    box-shadow: 0 2px 16px rgba(0,0,0,0.04);
}
.result-card h4 {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    margin-bottom: 0.4rem;
    color: #1a1a2e;
}

/* ── Risk badges ── */
.risk-high {
    background: #fdf0ef;
    border: 1px solid #e8b4b0;
    border-left: 4px solid #c0392b;
    border-radius: 6px;
    padding: 0.8rem 1.1rem;
    font-size: 0.85rem;
    color: #7b241c;
    font-weight: 500;
    margin-top: 1rem;
}
.risk-moderate {
    background: #fef9ec;
    border: 1px solid #e8d89b;
    border-left: 4px solid #d4ac0d;
    border-radius: 6px;
    padding: 0.8rem 1.1rem;
    font-size: 0.85rem;
    color: #7d6608;
    font-weight: 500;
    margin-top: 1rem;
}
.risk-mild {
    background: #edfaf1;
    border: 1px solid #a9dfbf;
    border-left: 4px solid #27ae60;
    border-radius: 6px;
    padding: 0.8rem 1.1rem;
    font-size: 0.85rem;
    color: #1d6a37;
    font-weight: 500;
    margin-top: 1rem;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #e8e5df; margin: 1.5rem 0; }

/* ── Spinner ── */
.stSpinner > div { color: #c0392b !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #1a1a2e;
}
section[data-testid="stSidebar"] * {
    color: #ccc !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #fff !important;
}
.sidebar-number {
    font-size: 1.15rem;
    font-weight: 600;
    color: #e74c3c !important;
}
.sidebar-label {
    font-size: 0.78rem;
    color: #aaa !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Success/info override ── */
.stSuccess, .stInfo { border-radius: 6px; }
.stAlert { font-size: 0.88rem; }

/* ── Image preview ── */
.stImage img {
    border-radius: 8px;
    border: 1px solid #e0ddd6;
}

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    background: #eeece7;
    border-radius: 8px;
    padding: 3px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    color: #888;
    background: transparent;
    padding: 0.5rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #1a1a2e !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# ------------------ GROQ CLIENT ------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ------------------ HELPERS ------------------
def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        audio_path = f.name
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="text"
        )
    os.unlink(audio_path)
    return transcription.strip()

def get_first_aid_guidance(situation: str) -> str:
    prompt = f"""You are a certified first aid expert. Provide clear, safe, and widely accepted first aid guidance.

Rules:
- Give only safe, evidence-based first aid steps.
- Do NOT prescribe medications or doses.
- Do NOT give advice that requires professional medical training.
- Use plain, calm, professional language. No emoji.

Situation: {situation}

Respond in this exact format:

Situation Assessment:
[Brief identification of the condition in 1-2 sentences]

Immediate Steps:
1. [Step one]
2. [Step two]
3. [Step three]
4. [Step four if needed]

What to Avoid:
- [Item]
- [Item]

When to Seek Emergency Care:
- [Indicator]
- [Indicator]
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def analyze_image_for_first_aid(image_bytes: bytes, media_type: str) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """You are a first aid expert analyzing a medical image or photo of an injury/condition.

Examine the image carefully and provide:

1. Condition Identified:
[What condition, injury, or situation you observe]

2. Severity Estimate:
[Mild / Moderate / Severe — with brief reasoning]

3. Immediate First Aid Steps:
1. [Step]
2. [Step]
3. [Step]

4. What to Avoid:
- [Item]
- [Item]

5. When to Seek Emergency Care:
- [Indicator]
- [Indicator]

Use plain, professional language. No emoji. If the image does not show a medical condition or injury, clearly state that and explain what you see instead."""
                    }
                ]
            }
        ],
        max_tokens=700
    )
    return response.choices[0].message.content


def render_risk_badge(ai_result: str):
    lower = ai_result.lower()
    if any(w in lower for w in ["severe", "unconscious", "not breathing", "immediate", "call emergency", "critical"]):
        st.markdown('<div class="risk-high">High Risk — Seek immediate emergency medical attention.</div>', unsafe_allow_html=True)
    elif any(w in lower for w in ["moderate", "pain", "bleeding", "infection", "consult"]):
        st.markdown('<div class="risk-moderate">Moderate Risk — Consider visiting a doctor or urgent care.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="risk-mild">Mild Condition — Basic first aid should be sufficient. Monitor for changes.</div>', unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "query" not in st.session_state:
    st.session_state.query = ""
if "run_query" not in st.session_state:
    st.session_state.run_query = False
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.markdown("## MediGuide")
    st.markdown("<p style='font-size:0.78rem; color:#888; letter-spacing:0.08em; text-transform:uppercase;'>AI First Aid Reference</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("This tool provides basic first aid guidance using AI. It is intended as a quick reference, not a replacement for professional medical care.")
    st.markdown("---")
    st.markdown("**Emergency Numbers — India**")
    st.markdown('<p><span class="sidebar-number">108</span><br><span class="sidebar-label">Ambulance</span></p>', unsafe_allow_html=True)
    st.markdown('<p><span class="sidebar-number">100</span><br><span class="sidebar-label">Police</span></p>', unsafe_allow_html=True)
    st.markdown('<p><span class="sidebar-number">101</span><br><span class="sidebar-label">Fire</span></p>', unsafe_allow_html=True)
    st.markdown('<p><span class="sidebar-number">112</span><br><span class="sidebar-label">National Emergency</span></p>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Not a substitute for professional medical advice. Always call emergency services in life-threatening situations.")

# ------------------ HEADER ------------------
st.markdown("""
<div class="app-header">
    <div class="brand">MediGuide</div>
    <div class="tagline">AI-Powered First Aid Assistant</div>
</div>
""", unsafe_allow_html=True)

# ------------------ TABS ------------------
tab1, tab2 = st.tabs(["Describe Situation", "Upload Image"])

# ===== TAB 1: TEXT / VOICE =====
with tab1:

    # Quick select
    st.markdown('<div class="section-label">Common Situations</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    situations = [
        ("Burns", "burn injury"),
        ("Deep Cut", "deep cut"),
        ("Fainting", "person fainted"),
        ("Choking", "choking emergency"),
        ("Bleeding", "heavy bleeding"),
    ]
    for col, (label, query) in zip([col1, col2, col3, col4, col5], situations):
        if col.button(label):
            st.session_state.query = query
            st.session_state.run_query = True

    # Voice input
    st.markdown('<div class="section-label">Voice Input</div>', unsafe_allow_html=True)
    audio = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key="recorder"
    )

    if audio and audio.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio["id"]
        with st.spinner("Transcribing audio..."):
            transcribed = transcribe_audio(audio["bytes"])
        if transcribed:
            st.session_state.query = transcribed
            st.session_state.run_query = True
            st.info(f'Transcribed: "{transcribed}"')

    # Text input
    st.markdown('<div class="section-label">Describe the Emergency</div>', unsafe_allow_html=True)

    def on_text_submit():
        val = st.session_state.text_input_box.strip()
        if val:
            st.session_state.query = val
            st.session_state.run_query = True

    st.text_input(
        label="Type and press Enter",
        key="text_input_box",
        placeholder="e.g. burn on forearm, deep cut on hand, someone fainted...",
        label_visibility="collapsed",
        on_change=on_text_submit
    )

    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("Get First Aid Guidance", key="text_btn"):
        val = st.session_state.get("text_input_box", "").strip()
        if val:
            st.session_state.query = val
            st.session_state.run_query = True
    st.markdown('</div>', unsafe_allow_html=True)

    # Result
    if st.session_state.run_query and st.session_state.query:
        final_query = st.session_state.query
        st.session_state.run_query = False

        with st.spinner("Analyzing situation..."):
            result = get_first_aid_guidance(final_query)

        st.markdown(f'<div class="section-label" style="margin-top:2rem;">Guidance for: {final_query}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-card">{result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        render_risk_badge(result)

# ===== TAB 2: IMAGE RECOGNITION =====
with tab2:
    st.markdown('<div class="section-label">Upload an Image</div>', unsafe_allow_html=True)
    st.caption("Upload a photo of the injury or condition. The AI will identify it and provide relevant first aid guidance.")

    uploaded_file = st.file_uploader(
        label="Choose an image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded image", use_container_width=True)

        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        analyze_btn = st.button("Analyze Image", key="img_btn")
        st.markdown('</div>', unsafe_allow_html=True)

        if analyze_btn:
            file_bytes = uploaded_file.read()
            media_type = uploaded_file.type or "image/jpeg"

            with st.spinner("Analyzing image..."):
                image_result = analyze_image_for_first_aid(file_bytes, media_type)

            st.markdown('<div class="section-label" style="margin-top:2rem;">Image Analysis Result</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-card">{image_result.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            render_risk_badge(image_result)

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("MediGuide is an informational tool only. It does not replace professional medical diagnosis or treatment. In emergencies, call 112 immediately.")