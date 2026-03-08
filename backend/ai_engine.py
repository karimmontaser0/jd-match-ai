from google import genai
import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
env_path = os.path.join(root_dir, ".env")
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def generate_questions(resume_text: str, job_description: str):
    # This will show up in your terminal to confirm the backend was reached
    print("--- AI Engine Triggered ---")
    print(f"Resume Length: {len(resume_text)} chars")
    print(f"JD Length: {len(job_description)} chars")

    prompt = f"""
    You are a professional technical recruiter and mechatronics expert.
    Analyze the following resume and job description to generate 5 high-quality, 
    challenging interview questions tailored to the candidate's experience.

    RESUME: {resume_text}
    JOB DESCRIPTION: {job_description}
    """

    try:
        # Using Gemini 2.5 Flash-Lite for 2026 performance
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        print("--- AI Response Successful ---")
        return response.text
    except Exception as e:
        print(f"--- AI Engine ERROR: {str(e)} ---")
        return f"AI Engine Error: {str(e)}"