from fastapi import FastAPI, UploadFile, File, Form
from pdf_parser import extract_resume_text
from ai_engine import generate_questions

app = FastAPI()

@app.get("/")
def home():
    return {"message": "JD-Match AI server running"}

@app.post("/generate-questions")
async def questions(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    resume_text = extract_resume_text(resume.file)

    questions = generate_questions(resume_text, job_description)

    return {"questions": questions}