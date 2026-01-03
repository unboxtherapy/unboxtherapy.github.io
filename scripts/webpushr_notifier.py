"""Send push notifications via Webpushr (Optional)"""
import os
import requests
from config import SITE_DOMAIN, TEXT_MODEL, GEMINI_API_KEY
from google import genai

# Webpushr API credentials
WEBPUSHR_API_KEY = os.environ.get("WEBPUSHR_API_KEY")
WEBPUSHR_AUTH_TOKEN = os.environ.get("WEBPUSHR_AUTH_TOKEN")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def generate_description(title, focus_kw):
    """Generate SEO-optimized meta description (150-160 characters)"""
    if not client:
        return f"Read our honest review of {focus_kw}. Features, pricing, pros & cons analysis."
    
    prompt = f"""
Generate a compelling meta description for this product review.

Title: {title}
Focus Keyword: {focus_kw}

Requirements:
- EXACTLY 150-160 characters (this is critical)
- Include the focus keyword naturally
- Action-oriented and engaging
- Make readers want to click
- No quotes or special characters
- Complete sentence

Return ONLY the description text, nothing else.
"""
    
    try:
        response = client.models.generate_content(
            model=TEXT_MODEL,
            contents=prompt
        )
        
        description = response.text.strip()
        
        if len(description) > 160:
            description = description[:157] + "..."
        
        return description
    except Exception as e:
        print(f"⚠️  Error generating description: {e}")
        return f"Comprehensive review of {focus_kw}. Read our honest analysis, features, pricing & pros/cons before buying."


def send_webpushr_notification(title, message, target_url, image_url=None):
    """
    Send push notification via Webpushr
    
    Args:
        title: Notification title
        message: Notification message
        target_url: URL to open when clicked
        image_url: Optional large image URL
    
    Returns:
        bool: Success status
    """
    
    if not WEBPUSHR_API_KEY:
        print("⚠️  WEBPUSHR_API_KEY not found - skipping notification")
        return False
    
    if not WEBPUSHR_AUTH_TOKEN:
        print("⚠️  WEBPUSHR_AUTH_TOKEN not found - skipping notification")
        return False
    
    try:
        print(f"📢 Sending Webpushr notification...")
        
        api_url = "https://api.webpushr.com/v1/notification/send/all"
        
        headers = {
            "webpushrKey": WEBPUSHR_API_KEY,
            "webpushrAuthToken": WEBPUSHR_AUTH_TOKEN,
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": title,
            "message": message,
            "target_url": target_url,
            "icon": f"{SITE_DOMAIN}/assets/images/site-logo.webp",
            "auto_hide": 1
        }
        
        if image_url:
            payload["image"] = image_url
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Notification sent successfully!")
            print(f"📊 Queue ID: {result.get('qid', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error sending Webpushr notification: {e}")
        return False


def send_blog_post_notification(title, permalink, focus_kw):
    """
    Send notification for new blog post/review
    
    Args:
        title: Blog post title
        permalink: Post permalink
        focus_kw: Focus keyword
    
    Returns:
        bool: Success status
    """
    
    post_url = f"{SITE_DOMAIN}/{permalink}"
    
    clean_permalink = permalink.strip('/').split('/')[-1]
    image_url = f"{SITE_DOMAIN}/assets/images/{clean_permalink}.webp"
    
    try:
        description = generate_description(title, focus_kw)
    except Exception as e:
        print(f"⚠️  Error generating description: {e}")
        description = f"New review: {title[:100]}"
    
    notification_title = title[:80] if len(title) > 80 else title
    notification_message = description
    
    return send_webpushr_notification(
        title=notification_title,
        message=notification_message,
        target_url=post_url,
        image_url=image_url
    )