from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import tempfile
import os
import sys

# Add src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from main import ResumeQueryBuilder

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Universal Resume Query Builder API",
    description="Upload a resume and generate optimized job search queries using Gemini AI",
    version="1.0.0"
)

# Enable CORS (for frontend integrations)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze_resume/")
async def analyze_resume(
    file: UploadFile = File(...),
    google_api_key: str = Form(default=os.getenv("GOOGLE_API_KEY", "")),
):
    """
    Upload a resume (PDF, DOCX, TXT) and get structured profile data + generated job search query.
    """

    if not google_api_key:
        return {"error": "Missing Google Gemini API key."}

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        file_type = os.path.splitext(file.filename)[1].lower()[1:]
        processor = ResumeQueryBuilder(google_api_key)
        result = processor.process_resume(tmp_path, file_type)

        return {
            "status": "success",
            "parsed_data": result["parsed_data"].dict(),
            "job_query": result["job_query"],
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
        }

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.get("/")
def root():
    return {"message": "✅ Universal Resume Query Builder API is running!"}
