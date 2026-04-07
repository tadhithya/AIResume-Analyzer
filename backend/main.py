from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io
import os
from openai import OpenAI

# ✅ Load API key from environment
client = OpenAI(api_key="API_KEY_HERE")

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI Resume Analyzer Running 🚀"}


# 🤖 AI Feedback Function
def get_ai_feedback(resume_text, job_desc):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
                Analyze resume and give improvements.

                Resume:
                {resume_text}

                Job Description:
                {job_desc}
                """
            }]
        )

        return response.choices[0].message.content

    except Exception:
        # 🔥 fallback (VERY IMPORTANT)
        return """⚠️ AI service unavailable (quota exceeded)

💡 Suggestions:
- Add more measurable achievements
- Include relevant keywords from job description
- Highlight projects and experience
- Use strong action verbs (built, developed, improved)

👉 (Demo mode active)"""


# 📄 MAIN API
@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_desc: str = Form("")
):
    content = await file.read()

    # 📄 Extract text
    if file.content_type == "application/pdf":
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif file.content_type == "text/plain":
        text = content.decode("utf-8", errors="ignore")

    else:
        return {"error": "Only PDF and TXT supported"}

    text = text.lower()
    job_desc = job_desc.lower()

    # 🔑 Skills
    skills = [
        "python", "java", "ai", "machine learning",
        "react", "sql", "fastapi", "javascript"
    ]

    found_skills = [s for s in skills if s in text]
    missing_skills = [s for s in skills if s not in text]

    # 🎯 Match score
    jd_keywords = job_desc.split()
    matched_keywords = [w for w in jd_keywords if w in text]

    match_score = int((len(matched_keywords) / len(jd_keywords)) * 100) if jd_keywords else 0
    score = int((len(found_skills) / len(skills)) * 100)

    # 🤖 AI feedback
    ai_feedback = get_ai_feedback(text, job_desc)

    return {
        "score": score,
        "match_score": match_score,
        "found_skills": found_skills,
        "missing_skills": missing_skills,
        "ai_feedback": ai_feedback
    }