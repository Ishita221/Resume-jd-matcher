# Resume ↔ JD Matcher

Paste a resume and a job description, get a match score, the skills that overlap, what's missing, and what to fix.

**Live:** https://resume-jd-matcher-epvsnwfabrnbxjhgamusxc.streamlit.app/

![screenshot](screenshot.png)

## Why

I was applying to internships and manually comparing my resume against every job description. It was slow and I kept missing things. So I automated it.

## How it works

Resume → text extraction → prompt → Gemini → JSON → UI

- **PDF** is parsed locally with `pypdf` — no API call, no quota used
- **Images** are sent to Gemini for text extraction, which costs one extra call
- The model is asked for strict JSON, which is cleaned and parsed before rendering
- Extracted text is shown in a preview so you can see what was actually read before spending a call on it

## Stack

Python · Streamlit · Gemini API · pypdf · Pillow

Streamlit was a deliberate choice. The value in this project is the prompt design and output handling, not the interface. React + FastAPI would have added three weeks of frontend and plumbing work and produced the same result. If this became a real product — multi-user, auth, persistent data — Streamlit would be the wrong tool and I'd move to FastAPI + React.

## What I ran into

**Model deprecation.** Started on `gemini-2.0-flash`, which had been retired. The error was `429 quota exceeded, limit: 0` — which reads like I'd used up my quota, but `limit: 0` actually means no access at all. Two very different problems behind the same error code. Moved to querying `list_models()` at runtime instead of trusting documentation, since the ecosystem moves faster than the docs do.

**Rate limits are per-model, per-day.** The free tier gives 20 requests/day *per model*. Hit this repeatedly while testing. Wrapped the call in `try/except` so the app shows a readable message instead of dumping a stack trace.

**JSON reliability.** The model wraps output in markdown fences unpredictably — sometimes ` ```json `, sometimes a preamble, sometimes clean. Strips fences before parsing, and on a parse failure falls back to displaying the raw response via `st.code(raw)` so the failure is debuggable instead of silent.

**Wasted calls on junk input.** Typing "jigul" still triggered a full API call and returned a meaningless score of 0. Added minimum-length validation before the call — 200 characters for the resume, 50 for the JD, because resumes are always substantial while a JD can legitimately be short.

**`.env` changes don't hot-reload.** `load_dotenv()` runs once at server start and won't overwrite an existing environment variable. Changing the model in `.env` and refreshing the browser silently did nothing — the server needs a full restart. Cost me a while before I printed the value to screen instead of guessing.

## Limitations

- PDF extraction struggles with multi-column layouts and returns nothing at all for scanned documents
- Scores vary by a few points across runs on identical input — LLM output isn't deterministic
- History is session-only; persisting it would require auth and a database
- No retry with exponential backoff, so a rate-limited request just fails rather than waiting and retrying
- Skill names are rendered with `unsafe_allow_html=True`. Safe here because the content comes from my own prompt, but this would be an XSS hole if the input were untrusted

## Run locally

```bash
git clone https://github.com/Ishita221/Resume-jd-matcher.git
cd Resume-jd-matcher
pip install -r requirements.txt
```

Create a `.env` file:


GEMINI_API_KEY=your_key_here
Then:

```bash
streamlit run app.py
```

Get a free API key at [Google AI Studio](https://aistudio.google.com/apikey).