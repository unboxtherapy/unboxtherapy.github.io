"""Generate comprehensive product review articles WITHOUT embedded images"""
from groq_client import generate_content
from config import GROQ_API_KEY
import re
import json


def generate_review_article(product_data, sales_data, affiliate_link=""):
    """
    Generate comprehensive 2500+ word product review article
    NO EMBEDDED IMAGES - Featured image only
    """
    
    product_name = product_data['name']
    creator = product_data['creator']
    price = product_data['price']
    launch_date = product_data['launch_date']
    platform = product_data.get('platform', 'Unknown')
    
    # Extract sales page information
    features = sales_data.get('features', [])
    benefits = sales_data.get('benefits', [])
    page_content = sales_data.get('page_content', '')
    pricing_info = sales_data.get('pricing', [])
    
    # Build comprehensive prompt for AI
    prompt = f"""Write a comprehensive, detailed product review for {product_name} by {creator}.

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. Write 2500-3500 words (MINIMUM 2500 words)
2. DO NOT include any images in the article body (NO ![alt](url) syntax)
3. DO NOT use markdown image syntax anywhere
4. Use natural, conversational tone like a real reviewer
5. Include specific details, examples, and analysis
6. Use markdown formatting: headers (##, ###), bold, lists, tables
7. Be honest but constructive in your analysis

PRODUCT INFORMATION:
- Product: {product_name}
- Creator: {creator}
- Price: ${price}
- Platform: {platform}
- Launch Date: {launch_date}

FEATURES FOUND ON SALES PAGE:
{chr(10).join(f'- {f}' for f in features[:20]) if features else 'Limited feature information available'}

BENEFITS & VALUE PROPOSITION:
{chr(10).join(f'- {b}' for b in benefits[:10]) if benefits else 'See general benefits below'}

ADDITIONAL CONTEXT FROM SALES PAGE:
{page_content[:3000] if page_content else 'Limited additional information available'}

PRICING DETAILS:
{chr(10).join(f"- ${p.get('price', 'Unknown')}: {p.get('context', '')[:100]}" for p in pricing_info[:5]) if pricing_info else f'Starting at ${price}'}

AFFILIATE LINK (use sparingly, naturally):
{affiliate_link}

---

ARTICLE STRUCTURE (2500-3500 words total):

## Introduction (200-300 words)
- Hook: Start with a relatable problem this product solves
- Brief overview of what {product_name} is
- Who is {creator} and why should readers trust this review
- What to expect in this review
- NO IMAGES HERE

## What is {product_name}? (300-400 words)
- Detailed explanation of the product
- What category/niche does it fit into
- Primary purpose and use cases
- Target audience analysis
- Key differentiating factors
- NO IMAGES HERE

## Key Features Breakdown (500-700 words)
Analyze the main features in depth:
- Explain each major feature in detail
- How does each feature work
- Real-world applications
- Compare to industry standards
- Use a comparison table if helpful
- NO IMAGES HERE

Example table format (optional):
| Feature | Description | Benefit |
|---------|-------------|---------|
| Feature 1 | How it works | Value to user |

## How Does {product_name} Work? (300-400 words)
- Step-by-step workflow explanation
- User experience walkthrough
- Integration process
- Learning curve analysis
- Technical requirements (if any)
- NO IMAGES HERE

## Benefits and Advantages (400-500 words)
Deep dive into real benefits:
- Time savings
- Cost effectiveness
- Productivity improvements
- Competitive advantages
- Long-term value
- Use specific examples and scenarios
- NO IMAGES HERE

## Potential Drawbacks (200-300 words)
Be honest about limitations:
- Learning curve
- Pricing considerations
- Feature gaps
- Who this might NOT be for
- Areas for improvement
- NO IMAGES HERE

## Pricing and Value Analysis (250-350 words)
- Detailed pricing breakdown
- What's included at each tier
- ROI analysis
- Comparison to alternatives
- Is it worth the price?
- Money-back guarantee details
- NO IMAGES HERE

## Who Should Use {product_name}? (200-250 words)
- Ideal user personas
- Business types that benefit most
- Skill level requirements
- Use case scenarios
- Who should avoid it
- NO IMAGES HERE

## Final Verdict (200-300 words)
- Summary of key points
- Overall rating considerations
- Recommendation
- Best practices for getting started
- Call to action (subtle mention of affiliate link)
- NO IMAGES HERE

---

WRITING STYLE REQUIREMENTS:
✅ Use first-person perspective ("I analyzed", "In my testing")
✅ Include specific details and examples
✅ Write like you've actually used the product
✅ Be conversational but professional
✅ Use transition phrases between sections
✅ Include pros/cons naturally in discussion
✅ Back up claims with reasoning
✅ Use subheadings (###) within major sections
✅ Include relevant statistics if applicable
✅ Address common objections

❌ NO generic statements without detail
❌ NO obvious AI writing patterns
❌ NO excessive hype or sales language
❌ NO markdown image syntax ![alt](url)
❌ NO HTML image tags <img>
❌ NO placeholder text like "[insert details]"
❌ NO apologetic language ("unfortunately", "sadly")
❌ NO mentioning you're an AI

TONE: Helpful expert who has thoroughly researched the product. Honest, balanced, insightful.

LENGTH: Aim for 2800-3200 words. Each section should be substantial with real analysis.

IMPORTANT REMINDERS:
- DO NOT include any images (![alt](url)) anywhere in the article
- Featured image will be handled separately
- Focus on detailed written analysis
- Use tables, lists, and formatting instead of images
- Write comprehensive, valuable content

Begin the article now (NO front matter, NO images):"""

    print("🤖 Generating comprehensive 2500+ word review article...")
    print("⚡ Using Groq (Llama 3.3 70B) - Lightning fast inference!")
    print("📊 Target: 2500-3500 words for thorough coverage")
    print("🚫 NO embedded images - featured image only")
    
    # Use higher token limit for longer articles
    response_text = generate_content(
        prompt, 
        max_tokens=5000,
        temperature=0.7
    )
    
    content = remove_front_matter(response_text)
    
    # AGGRESSIVE image removal
    print("\n🧹 Cleaning article content...")
    
    # Remove ALL markdown images
    original_image_count = len(re.findall(r'!\[.*?\]\(.*?\)', content))
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    
    # Remove ALL HTML images
    content = re.sub(r'<img[^>]*>', '', content)
    content = re.sub(r'<img[^>]*\/>', '', content)
    
    # Remove emoji images
    content = re.sub(r'!\[[\U0001F300-\U0001F9FF].*?\]\(.*?\)', '', content)
    
    # Remove any remaining image-like patterns
    content = re.sub(r'!\[.*?\]\s*\(.*?\)', '', content)
    
    # Fix markdown table formatting
    content = re.sub(r'\|\s*–+\s*\|', '|----------|', content)
    content = re.sub(r'\|\s*-+\s*\|', '|----------|', content)
    content = re.sub(r'\|--+\|', '|----------|', content)
    content = re.sub(r'\|\s+\|', '| |', content)
    
    # Clean up extra blank lines from removed images
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    # Final verification
    remaining_images = len(re.findall(r'!\[.*?\]\(.*?\)', content))
    remaining_html_images = len(re.findall(r'<img', content))
    
    word_count = len(content.split())
    
    print(f"\n✅ Article generated:")
    print(f"   📝 Characters: {len(content):,}")
    print(f"   📖 Words: ~{word_count:,}")
    
    if original_image_count > 0:
        print(f"   🧹 Removed {original_image_count} embedded images")
    
    if remaining_images > 0 or remaining_html_images > 0:
        print(f"   ⚠️  WARNING: {remaining_images + remaining_html_images} images still detected!")
        # Emergency cleanup
        content = re.sub(r'!\[.*?\].*?\)', '', content)
        content = re.sub(r'<img.*?>', '', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        print(f"   🚨 Emergency cleanup applied")
    else:
        print(f"   ✅ Clean: No embedded images (featured image only)")
    
    # Count tables
    table_count = len(re.findall(r'\|.*\|.*\n\|[-]+\|', content))
    print(f"   📊 Tables: {table_count}")
    
    if word_count < 2500:
        print(f"\n⚠️  WARNING: Article is shorter than target ({word_count} words)")
        print(f"💡 Consider providing more detailed JV page content")
    else:
        print(f"✅ Article meets length requirement ({word_count} words)")
    
    return content


def remove_front_matter(content):
    """Remove any front matter from AI-generated content"""
    # Remove YAML front matter
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    
    # Remove any leading metadata lines
    lines = content.split('\n')
    clean_lines = []
    skip_yaml = True
    
    for line in lines:
        # Stop skipping once we hit actual content
        if line.strip().startswith('#') or (line.strip() and ':' not in line):
            skip_yaml = False
        
        if not skip_yaml:
            clean_lines.append(line)
        elif skip_yaml and line.strip() and ':' not in line:
            skip_yaml = False
            clean_lines.append(line)
    
    return '\n'.join(clean_lines).strip()


# Keep other functions from original file (create_review_front_matter, etc.)
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