import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini model configuration
GEMINI_CONFIG = {
    "model": os.getenv("MODEL_NAME", "gemini-2.0-flash"),
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "top_p": 0.9,
    "top_k": 40
}

# Agent configuration
MAX_AGENTS = int(os.getenv("MAX_AGENTS", 4))
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
COST_THRESHOLD = float(os.getenv("COST_THRESHOLD", 5.0))
VERIFICATION_CONFIDENCE = float(os.getenv("VERIFICATION_CONFIDENCE", 0.85))

# API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")
