import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")


def build_prompt(resume, jd):
    return f"""
Compare this resume against this job description.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Give your answer as plain text:
- Match score out of 100
- Skills that match
- Skills that are missing
- 3 suggestions to improve the resume
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
                st.write(response.text)
            except Exception as e:
                st.error(f"Failed: {e}")
