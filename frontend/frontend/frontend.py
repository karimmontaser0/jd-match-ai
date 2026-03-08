import reflex as rx
import sys
import os
from google import genai
from dotenv import load_dotenv
import pdfplumber
import io

# --- 1. BACKEND LOGIC ---
def get_client():
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(root_path, ".env"))
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def extract_text(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# --- 2. STATE MANAGEMENT ---
class State(rx.State):
    questions: str = ""
    processing: bool = False
    jd_text: str = ""

    def set_jd_text(self, text: str):
        self.jd_text = text

    async def handle_upload(self, files: list[rx.UploadFile]):
        print(f"\n>>> GENERATE BUTTON CLICKED! Files found: {len(files)}")
        
        # STOP SILENT FAILURES: Show an error on screen if no file is found
        if not files:
            self.questions = "### ⚠️ No file detected\nPlease click the upload box to select your CV before generating."
            return
            
        self.processing = True
        yield 
        
        try:
            for file in files:
                print(f">>> READING FILE: {file.filename}")
                upload_data = await file.read()
                resume_text = extract_text(upload_data)
                
                print(">>> CALLING AI ENGINE...")
                client = get_client()
                prompt = f"""
                You are a technical recruiter expert in Mechatronics, AI, and Automation.
                Analyze this Resume: {resume_text}
                And this Job Description: {self.jd_text}
                Generate 5 challenging, specific interview questions with brief explanations on why you are asking them.
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt
                )
                self.questions = response.text
                print(">>> SUCCESS!")
                
        except Exception as e:
            print(f">>> ERROR: {str(e)}")
            self.questions = f"### ⚠️ System Error\n{str(e)}"
        finally:
            self.processing = False

# --- 3. UI DESIGN ---
def index():
    # Define the ID here so both the box and button use the EXACT same reference
    UP_ID = "cv_upload_zone"

    return rx.box(
        rx.center(
            rx.vstack(
                # Header
                rx.vstack(
                    rx.heading("JD-Match AI", size="9", weight="bold", color="#111827"),
                    rx.text("Technical Interview Intelligence for Engineers", size="4", color="#374151", weight="medium"),
                    spacing="2",
                    text_align="center",
                    margin_bottom="2em",
                ),

                # Main Card
                rx.card(
                    rx.vstack(
                        # Step 1: Upload (Now using native frontend state for instant feedback)
                        rx.vstack(
                            rx.text("Step 1: Upload Resume (PDF)", size="3", weight="bold", color="#111827"),
                            rx.upload(
                                rx.vstack(
                                    rx.icon(tag="upload", size=30, color="#4F46E5"),
                                    rx.text("Click or drop PDF here", size="2", color="#4B5563"),
                                    # This magically shows the filename instantly without backend logic!
                                    rx.foreach(
                                        rx.selected_files(UP_ID),
                                        lambda f: rx.text(f"✅ Selected: {f}", color="#059669", weight="bold", size="2")
                                    )
                                ),
                                id=UP_ID,
                                border="2px dashed #D1D5DB",
                                padding="3em",
                                border_radius="15px",
                                background="#F9FAFB",
                                width="100%",
                                _hover={"background": "#F3F4F6", "border_color": "#4F46E5"},
                            ),
                            width="100%",
                            align_items="start",
                        ),

                        # Step 2: JD Text
                        rx.vstack(
                            rx.text("Step 2: Job Description", size="3", weight="bold", color="#111827"),
                            rx.text_area(
                                placeholder="Paste the automation or software job requirements here...",
                                on_change=State.set_jd_text,
                                width="100%",
                                height="180px",
                                background="white",
                                border_color="#D1D5DB",
                                color="#111827",
                                _focus={"border_color": "#4F46E5"},
                            ),
                            width="100%",
                            align_items="start",
                        ),

                        # Generate Button
                        rx.button(
                            "Generate Interview Guide",
                            on_click=State.handle_upload(rx.upload_files(upload_id=UP_ID)),
                            loading=State.processing,
                            width="100%",
                            size="4",
                            background="#4F46E5",
                            color="white",
                            _hover={"background": "#4338CA", "transform": "translateY(-2px)"},
                            transition="all 0.2s",
                            cursor="pointer",
                        ),
                        spacing="6",
                    ),
                    width="100%",
                    padding="3em",
                    border_radius="24px",
                    box_shadow="0 20px 25px -5px rgba(0, 0, 0, 0.1)",
                    background="white",
                ),

                # Results Section
                rx.cond(
                    State.questions,
                    rx.card(
                        rx.vstack(
                            rx.heading("Your Tailored Questions", size="5", color="#111827", mb="4"),
                            rx.divider(color_scheme="gray"),
                            rx.box(
                                rx.markdown(State.questions),
                                style={"color": "#1F2937", "line_height": "1.8", "font_size": "16px"},
                                width="100%",
                            ),
                            align_items="start",
                        ),
                        width="100%",
                        padding="2.5em",
                        margin_top="2em",
                        background="white",
                        border="1px solid #E5E7EB",
                        border_radius="20px",
                        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                    )
                ),
                
                spacing="4",
                width="680px",
            ),
            padding_y="10vh",
            background="linear-gradient(180deg, #F3F4F6 0%, #E5E7EB 100%)",
            min_height="100vh",
        )
    )

app = rx.App()
app.add_page(index)