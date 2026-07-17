import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader
from PIL import Image
import json
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.1-flash-lite"

if "history" not in st.session_state:
    st.session_state.history = []
def clear_inputs():
    st.session_state.resume_input = ""
    st.session_state.jd_input = ""


def clear_history():
    st.session_state.history = []


    

st.set_page_config(page_title="Resume ↔ JD Matcher", page_icon="🎯", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap" rel="stylesheet">
<style>
    .stApp {
        background:
            radial-gradient(900px 500px at 12% -8%, rgba(99,102,241,.20), transparent 60%),
            radial-gradient(800px 500px at 88% 8%, rgba(20,184,166,.14), transparent 60%),
            #0B0F1A;
    }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem; max-width: 1080px; }
    #MainMenu, footer, header { visibility: hidden; }

    .hero { text-align: center; padding: 1.5rem 0 2rem; }
    .hero h1 {
        font-size: 2.9rem; font-weight: 800; letter-spacing: -1.5px;
        margin: 0; line-height: 1.1;
        background: linear-gradient(100deg, #A5B4FC 0%, #FFFFFF 45%, #5EEAD4 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero p { color: #94A3B8; font-size: 1.02rem; margin-top: .7rem; }

    .panel {
        background: rgba(255,255,255,.03);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 14px; padding: 4px 18px 14px;
    }
    .panel-title {
        font-size: .72rem; font-weight: 600; letter-spacing: 1.4px;
        text-transform: uppercase; color: #818CF8; margin: 14px 0 8px;
    }

    .stTextArea textarea, .stFileUploader section {
        background: rgba(255,255,255,.04) !important;
        border: 1px solid rgba(255,255,255,.10) !important;
        border-radius: 10px !important;
        color: #E5E7EB !important;
    }
    .stTextArea textarea:focus { border-color: #6366F1 !important; }

    .stButton > button {
        border-radius: 10px; font-weight: 600; height: 3.1rem;
        border: none; letter-spacing: .3px;
        background: linear-gradient(100deg, #6366F1, #14B8A6);
        transition: transform .12s ease, box-shadow .12s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(99,102,241,.35);
    }

    .scorebox {
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 14px; padding: 22px 26px; margin-bottom: 4px;
    }
    .scoreval { font-size: 3.4rem; font-weight: 800; line-height: 1; letter-spacing: -2px; }
    .scoresub { color: #94A3B8; font-size: .8rem; letter-spacing: 1.2px; text-transform: uppercase; }

    .chip {
        display: inline-block; padding: 6px 13px; margin: 4px 5px 4px 0;
        border-radius: 999px; font-size: .82rem; font-weight: 500;
    }
    .chip-yes { background: rgba(16,185,129,.13); color: #6EE7B7; border: 1px solid rgba(16,185,129,.28); }
    .chip-no  { background: rgba(244,63,94,.11);  color: #FDA4AF; border: 1px solid rgba(244,63,94,.26); }

    .card {
        background: rgba(255,255,255,.035);
        border: 1px solid rgba(255,255,255,.08);
        border-left: 3px solid #6366F1;
        border-radius: 10px; padding: 15px 18px; margin-bottom: 9px;
        color: #CBD5E1; font-size: .93rem; line-height: 1.6;
    }
    .card b { color: #A5B4FC; margin-right: 6px; }
    .stProgress > div > div > div { background: linear-gradient(90deg, #6366F1, #14B8A6); }
</style>
""", unsafe_allow_html=True)

def extract_pdf(file):
    reader = PdfReader(file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def extract_image(file):
    img = Image.open(file)
    model = genai.GenerativeModel(MODEL_NAME)
    resp = model.generate_content(
        ["Extract all text from this resume image. Return plain text only, no commentary.", img]
    )
    return resp.text.strip()


def read_upload(file):
    if file.type == "application/pdf":
        return extract_pdf(file)
    return extract_image(file)


def build_prompt(resume, jd):
    return f"""You are a resume analyst. Compare the resume against the job description.

Return ONLY valid JSON. No markdown, no backticks, no explanation before or after.

Use exactly this structure:
{{
  "match_score": <number 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
}}

RESUME:
{resume}

JOB DESCRIPTION:
{jd}
"""


st.markdown("""
<div class="hero">
    <h1>Resume ↔ JD Matcher</h1>
    <p>Upload your resume, drop in a job description, and see exactly where you stand.</p>
</div>
""", unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    st.markdown('<div class="panel-title">Your Resume</div>', unsafe_allow_html=True)
    upload = st.file_uploader("Upload PDF or image", type=["pdf", "png", "jpg", "jpeg"])
    resume = ""
    if upload:
        with st.spinner("Reading file..."):
            try:
                resume = read_upload(upload)
                st.success(f"Extracted {len(resume)} characters")
                with st.expander("Preview extracted text"):
                    st.text(resume[:1500])
            except Exception as e:
                st.error(f"Could not read file: {e}")
    else:
        resume = st.text_area("Or paste it here", height=280,key="resume_input", label_visibility="collapsed",
                              placeholder="Paste your resume...")

with right:
    st.markdown('<div class="panel-title">Job Description</div>', unsafe_allow_html=True)
    jd = st.text_area("JD", height=340, key="jd_input",label_visibility="collapsed",
                      placeholder="Paste the job description...")

st.divider()

if st.button("Analyze", type="primary", use_container_width=True):
    if len(resume.strip()) < 200:
        st.warning("Resume looks too short — add more detail or upload a file.")
    elif len(jd.strip()) < 50:
        st.warning("Job description looks too short.")
    else:
        with st.spinner("Analyzing..."):
            raw = ""
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(build_prompt(resume, jd))

                raw = response.text.strip()
                raw = raw.replace("```json", "").replace("```", "").strip()
                data = json.loads(raw)

                st.session_state.history.append({
                    "score": data["match_score"],
                    "jd": jd.strip()[:70],
                    "missing": data["missing_skills"],
                })

                score = data["match_score"]
                if score >= 75:
                    verdict, color = "Strong match", "🟢"
                elif score >= 50:
                    verdict, color = "Partial match", "🟡"
                else:
                    verdict, color = "Weak match", "🔴"

                hue = "#34D399" if score >= 75 else "#FBBF24" if score >= 50 else "#FB7185"
                st.markdown(f"""
                <div class="scorebox">
                    <div class="scoresub">Match Score</div>
                    <div class="scoreval" style="color:{hue}">{score}<span style="font-size:1.4rem;color:#64748B">/100</span></div>
                    <div style="color:{hue};font-weight:600;margin-top:6px">{color} {verdict}</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(score / 100)

                st.divider()

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<div class="panel-title">✅ Matching Skills</div>', unsafe_allow_html=True)
                    chips = "".join(
                        f'<span class="chip chip-yes">{s}</span>'
                        for s in data["matching_skills"]
                    )
                    st.markdown(chips or "_None found_", unsafe_allow_html=True)
                with c2:
                    st.markdown('<div class="panel-title">❌ Missing Skills</div>', unsafe_allow_html=True)
                    chips = "".join(
                        f'<span class="chip chip-no">{s}</span>'
                        for s in data["missing_skills"]
                    )
                    st.markdown(chips or "_None found_", unsafe_allow_html=True)

                st.divider()

                st.markdown('<div class="panel-title">💡 Suggestions</div>', unsafe_allow_html=True)
                for i, s in enumerate(data["suggestions"], 1):
                    st.markdown(
                        f'<div class="card"><b>{i}.</b> {s}</div>',
                        unsafe_allow_html=True
                    )

            except json.JSONDecodeError:
                st.error("Model did not return valid JSON.")
                st.code(raw)
            except Exception as e:
                st.error(f"Failed: {e}")


if st.session_state.history:
    st.divider()

    with st.expander(f"Previous runs ({len(st.session_state.history)})"):
        for h in reversed(st.session_state.history):
            hue = "#34D399" if h["score"] >= 75 else "#FBBF24" if h["score"] >= 50 else "#FB7185"
            gaps = ", ".join(h["missing"][:3]) or "—"
            st.markdown(f"""
            <div class="card">
                <b style="color:{hue}">{h['score']}/100</b> — {h['jd']}...
                <div style="color:#64748B;font-size:.82rem;margin-top:5px">Missing: {gaps}</div>
            </div>
            """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        st.button("Clear inputs", use_container_width=True, on_click=clear_inputs)
    with b2:
        st.button("Clear history", use_container_width=True, on_click=clear_history)