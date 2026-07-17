import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

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


st.title("Resume ↔ JD Matcher")

resume = st.text_area("Paste your resume", height=250)
jd = st.text_area("Paste the job description", height=250)

if st.button("Analyze"):
    if not resume or not jd:
        st.warning("Dono box bharo")
    else:
        with st.spinner("Analyzing..."):
            try:
                prompt = build_prompt(resume, jd)
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(prompt)

                raw = response.text.strip()
                raw = raw.replace("```json", "").replace("```", "").strip()

                data = json.loads(raw)
                st.metric("Match Score", f"{data['match_score']}/100")
                st.progress(data['match_score'] / 100)

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("✅ Matching")
                    for s in data['matching_skills']:
                        st.write("•", s)
                with col2:
                    st.subheader("❌ Missing")
                    for s in data['missing_skills']:
                        st.write("•", s)

                st.subheader("💡 Suggestions")
                for i, s in enumerate(data['suggestions'], 1):
                    st.write(f"{i}. {s}")

            except json.JSONDecodeError:
                st.error("Model ne valid JSON nahi diya")
                st.code(raw)
            except Exception as e:
                st.error(f"Failed: {e}")
