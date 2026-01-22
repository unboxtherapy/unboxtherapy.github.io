"""Google Gemini AI Client - Free, Powerful LLM"""
import google.generativeai as genai
import os
from config import GEMINI_API_KEY, GEMINI_MODEL

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
else:
    model = None


def generate_content(prompt, max_tokens=4000, temperature=0.7):
    """
    Generate content using Google Gemini
    
    Args:
        prompt: The prompt to send to the model
        max_tokens: Maximum tokens to generate (default: 4000)
        temperature: Creativity (0.0-2.0, default: 0.7)
    
    Returns:
        Generated text content
    """
    if not model:
        raise ValueError("❌ GEMINI_API_KEY not found. Get one free at https://aistudio.google.com/apikey")
    
    try:
        # Configure generation settings
        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        
        # Generate content
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Gemini API error: {e}")
        
        # Handle specific error cases
        if "quota" in error_msg.lower() or "limit" in error_msg.lower():
            print(f"⚠️  Rate limit reached. Please wait a moment and try again.")
            print(f"💡 Gemini free tier limits: 15 requests/minute, 1500 requests/day")
        
        elif "invalid" in error_msg.lower() or "key" in error_msg.lower():
            print(f"⚠️  Invalid API key. Get a new one at https://aistudio.google.com/apikey")
        
        elif "model" in error_msg.lower():
            print(f"⚠️  Model {GEMINI_MODEL} not available, trying gemini-pro...")
            try:
                fallback_model = genai.GenerativeModel("gemini-pro")
                response = fallback_model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature
                    )
                )
                print(f"✅ Successfully generated with gemini-pro")
                return response.text
            except Exception as e2:
                print(f"❌ Fallback model also failed: {e2}")
        
        raise


def generate_with_system_prompt(system_prompt, user_prompt, max_tokens=4000):
    """
    Generate content with system and user prompts
    
    Args:
        system_prompt: System instructions
        user_prompt: User query
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated text content
    """
    if not model:
        raise ValueError("❌ GEMINI_API_KEY not found")
    
    try:
        # Combine system and user prompts for Gemini
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.7,
        )
        
        response = model.generate_content(
            combined_prompt,
            generation_config=generation_config
        )
        
        return response.text
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        raise


def test_gemini_connection():
    """Test Gemini API connection"""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set")
        print("🔗 Get free API key at: https://aistudio.google.com/apikey")
        return False
    
    try:
        response = generate_content("Say 'Hello, I am working!' in exactly 5 words.", max_tokens=50)
        print(f"✅ Gemini connected successfully!")
        print(f"📝 Test response: {response}")
        return True
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing Gemini connection...")
    test_gemini_connection()