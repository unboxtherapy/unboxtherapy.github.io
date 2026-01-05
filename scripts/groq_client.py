"""Groq AI Client - Fast, Free LLM Inference"""
from groq import Groq
import os
from config import GROQ_API_KEY, GROQ_MODEL

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def generate_content(prompt, max_tokens=4000, temperature=0.7):
    """
    Generate content using Groq's fast inference
    
    Args:
        prompt: The prompt to send to the model
        max_tokens: Maximum tokens to generate (default: 4000)
        temperature: Creativity (0.0-2.0, default: 0.7)
    
    Returns:
        Generated text content
    """
    if not client:
        raise ValueError("❌ GROQ_API_KEY not found. Get one free at https://console.groq.com/")
    
    try:
        # Use the model from config
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=GROQ_MODEL,  # Uses llama-3.3-70b-versatile
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Groq API error: {e}")
        
        # Handle specific error cases
        if "decommissioned" in error_msg.lower() or "not found" in error_msg.lower():
            print(f"⚠️  Model {GROQ_MODEL} not available, trying llama-3.3-70b-versatile...")
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return chat_completion.choices[0].message.content
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
        
        # Handle token limit exceeded (413 error)
        elif "413" in error_msg or "too large" in error_msg.lower() or "limit" in error_msg.lower():
            print(f"⚠️  Request too large, trying faster model with larger context...")
            try:
                # Try llama-3.3-70b-versatile (faster, handles more tokens)
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                print(f"✅ Successfully generated with llama-3.3-70b-versatile")
                return chat_completion.choices[0].message.content
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
    if not client:
        raise ValueError("❌ GROQ_API_KEY not found")
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model=GROQ_MODEL,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        raise


def test_groq_connection():
    """Test Groq API connection"""
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set")
        print("🔗 Get free API key at: https://console.groq.com/")
        return False
    
    try:
        response = generate_content("Say 'Hello, I am working!' in exactly 5 words.", max_tokens=50)
        print(f"✅ Groq connected successfully!")
        print(f"📝 Test response: {response}")
        return True
    except Exception as e:
        print(f"❌ Groq connection failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing Groq connection...")
    test_groq_connection()