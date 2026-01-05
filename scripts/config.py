"""Configuration settings for the review blog generator"""
import os

# File paths
POSTS_DIR = "_posts"
IMAGES_DIR = "images"
DATA_DIR = "_data"
REVIEWS_DB_FILE = "_data/reviews_database.json"

# Site settings
SITE_DOMAIN = "https://unboxtherapy.github.io"

# AI Configuration - Using Groq (free, fast, never expires)
AI_PROVIDER = "groq"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"  # Latest Llama 3.3 model (Dec 2024)

# Image generation (optional - now using sales page images instead)
FREEPIK_API_KEY = os.environ.get("FREEPIK_API_KEY", "")
FREEPIK_ENDPOINT = "https://api.freepik.com/v1/ai/text-to-image/flux-dev"

# Generation settings
POSTS_PER_RUN = 1  # How many product reviews to generate per run

# Image settings
IMAGE_QUALITY = 80  # 1-100
IMAGE_MAX_WIDTH = 1920
IMAGE_MAX_HEIGHT = 1080
OPTIMIZE_IMAGE = True

# Timing
WAIT_TIME_BEFORE_INDEXING = 180  # seconds (3 minutes)

# MunchEye Settings
MUNCHEYE_SECTIONS = ['just_launched', 'big_launches']  # Only these sections
REVIEW_RECENT_DAYS = 14

# Google Indexing (Optional)
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
ENABLE_GOOGLE_INDEXING = bool(GOOGLE_SERVICE_ACCOUNT_JSON)

# Push Notifications (Optional)
WEBPUSHR_API_KEY = os.environ.get("WEBPUSHR_API_KEY", "")
WEBPUSHR_AUTH_TOKEN = os.environ.get("WEBPUSHR_AUTH_TOKEN", "")
ENABLE_PUSH_NOTIFICATIONS = bool(WEBPUSHR_API_KEY and WEBPUSHR_AUTH_TOKEN)

# Create directories
os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)