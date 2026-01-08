"""Generate comprehensive product review articles"""
from groq_client import generate_content
from config import GROQ_API_KEY
import re
import json


# In review_article_generator.py, update the API call:

def generate_review_article(product_data, sales_data, affiliate_link=""):
    """Generate comprehensive 2500+ word product review article"""
    
    # ... (all the prompt code from above) ...
    
    print("🤖 Generating comprehensive 2500+ word review article...")
    print("⚡ Using Groq (Llama 3.3 70B) - Lightning fast inference!")
    print("📊 Target: 2500-3500 words for thorough coverage")
    
    # Use higher token limit for longer articles
    # ~4000 tokens ≈ 3000 words output
    response_text = generate_content(
        prompt, 
        max_tokens=5000,  # Increased from 4000
        temperature=0.7    # Slightly creative but focused
    )
    
    content = remove_front_matter(response_text)
    
    # Remove any emoji images
    content = re.sub(r'!\[[\U0001F300-\U0001F9FF].*?\]\(.*?\)', '', content)
    content = re.sub(r'!\[[🔥💡⚡🎯✨🚀💪👍✅❌⚠️📊📈📉💰🎁]\]\(.*?\)', '', content)
    
    # Fix markdown table formatting issues
    # Replace incorrect separators with proper ones
    content = re.sub(r'\|\s*—+\s*\|', '|----------|', content)
    content = re.sub(r'\|\s*-+\s*\|', '|----------|', content)
    content = re.sub(r'\|--+\|', '|----------|', content)
    
    # Ensure proper spacing in tables
    content = re.sub(r'\|\s+\|', '| |', content)
    
    word_count = len(content.split())
    print(f"✅ Article generated:")
    print(f"   📝 Characters: {len(content):,}")
    print(f"   📖 Words: ~{word_count:,}")
    
    # Count embedded images
    image_count = len(re.findall(r'!\[.*?\]\(.*?\)', content))
    print(f"   📸 Images: {image_count}")
    
    # Count tables
    table_count = len(re.findall(r'\|.*\|.*\n\|[-]+\|', content))
    print(f"   📊 Tables: {table_count}")
    
    if word_count < 2500:
        print(f"⚠️  WARNING: Article is shorter than target ({word_count} words)")
        print(f"💡 Consider providing more detailed JV page content")
    else:
        print(f"✅ Article meets length requirement ({word_count} words)")
    
    return content

def create_review_front_matter(product_data, permalink):
    """Create Jekyll front matter for review article"""
    
    product_name = product_data['name']
    creator = product_data['creator']
    
    title = f"{product_name} Review {product_data['launch_date'][:4]} - Honest Analysis by Real Users"
    
    description = generate_review_description(product_name, creator, product_data['price'])
    
    category = determine_category(product_name)
    
    escaped_title = title.replace('"', '\\"')
    escaped_desc = description.replace('"', '\\"')
    
    front_matter = f"""---
title: "{escaped_title}"
description: "{escaped_desc}"
tags: [{category}, Software Review, {creator}]
categories: [Product Reviews]
featured: true
image: '/images/{permalink}.webp'
rating: 0
product_name: "{product_name}"
creator: "{creator}"
price: "${product_data['price']}"
launch_date: "{product_data['launch_date']}"
affiliate_disclosure: true
---"""
    
    return front_matter


def generate_review_description(product_name, creator, price):
    """Generate SEO meta description for review"""
    
    prompt = f"""
Generate a compelling meta description for this product review.

Product: {product_name}
Creator: {creator}
Price: ${price}

Requirements:
- EXACTLY 150-160 characters
- Include product name and "review"
- Mention honest, unbiased analysis
- Include key benefit or feature
- Make it click-worthy
- No quotes or special characters

Return ONLY the description text.
"""
    
    description = generate_content(prompt, max_tokens=100)
    description = description.strip()
    
    if len(description) > 160:
        description = description[:157] + "..."
    
    return description


def generate_image_prompt(title):
    """Generate image prompt for Freepik AI"""
    prompt = f"""
Create a photorealistic featured image prompt for this blog post:
Title: {title}

Requirements:
- Professional, high-quality
- NO text or words in the image
- Suitable as a blog featured image
- 16:9 aspect ratio
- Relevant to the topic

Return ONLY the image prompt, nothing else.
"""
    
    print("🎨 Generating image prompt...")
    response = generate_content(prompt, max_tokens=200)
    return response.strip()


def determine_category(product_name):
    """Determine product category from name"""
    
    name_lower = product_name.lower()
    
    categories = {
        'ai': ['ai', 'artificial intelligence', 'chatgpt', 'gpt', 'machine learning'],
        'video': ['video', 'youtube', 'reel', 'tiktok', 'shorts'],
        'social': ['social', 'instagram', 'facebook', 'twitter', 'linkedin'],
        'seo': ['seo', 'rank', 'traffic', 'search engine'],
        'email': ['email', 'autoresponder', 'newsletter', 'mail'],
        'ecommerce': ['ecommerce', 'shopify', 'amazon', 'store', 'shop'],
        'website': ['website', 'site', 'builder', 'wordpress', 'hosting'],
        'marketing': ['marketing', 'funnel', 'sales', 'conversion'],
        'content': ['content', 'writing', 'article', 'blog'],
        'graphics': ['graphic', 'design', 'image', 'logo', 'banner']
    }
    
    for category, keywords in categories.items():
        if any(keyword in name_lower for keyword in keywords):
            return category.title()
    
    return 'Software Review'


def remove_front_matter(content):
    """Remove any front matter from AI-generated content"""
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    
    lines = content.split('\n')
    clean_lines = []
    skip_yaml = True
    
    for line in lines:
        if line.strip().startswith('#') or (line.strip() and ':' not in line):
            skip_yaml = False
        
        if not skip_yaml:
            clean_lines.append(line)
        elif skip_yaml and line.strip() and ':' not in line:
            skip_yaml = False
            clean_lines.append(line)
    
    return '\n'.join(clean_lines).strip()