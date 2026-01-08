"""Generate comprehensive product review articles"""
from groq_client import generate_content
from config import GROQ_API_KEY
import re
import json


def generate_review_article(product_data, sales_data, affiliate_link=""):
    """
    Generate comprehensive product review article with embedded images
    
    Args:
        product_data: Dict from muncheye_scraper
        sales_data: Dict from sales_page_scraper
        affiliate_link: Affiliate URL (empty by default)
    
    Returns:
        Complete article in Jekyll format
    """
    
    product_name = product_data['name']
    creator = product_data['creator']
    price = product_data['price']
    commission = product_data['commission']
    platform = product_data['platform']
    launch_date = product_data['launch_date']
    
    features = sales_data.get('features', [])
    description = sales_data.get('description', '')
    benefits = sales_data.get('benefits', [])
    pricing_info = sales_data.get('pricing', [])
    bonuses = sales_data.get('bonuses', [])
    guarantee = sales_data.get('guarantee', '')
    images = sales_data.get('images', [])
    
    # Prepare image information for AI (only product screenshots)
    image_list = []
    for idx, img in enumerate(images[:5], 1):  # Limit to TOP 5 images only
        image_list.append({
            'id': f'image_{idx}',
            'url': img['url'],
            'alt': img.get('alt', f'{product_name} screenshot {idx}'),
            'markdown': f'![{img.get("alt", product_name)}]({img["url"]})'
        })
    
    prompt = f"""
Write a comprehensive, unbiased product review for: {product_name} by {creator}

PRODUCT INFORMATION:
- Name: {product_name}
- Creator: {creator}
- Price: ${price}
- Platform: {platform}
- Launch Date: {launch_date}
- Description: {description}

FEATURES:
{json.dumps(features, indent=2)}

BENEFITS:
{json.dumps(benefits, indent=2)}

BONUSES:
{json.dumps(bonuses, indent=2)}

GUARANTEE:
{guarantee}

AVAILABLE IMAGES FROM JV PAGE:
{json.dumps(image_list, indent=2)}

CRITICAL IMAGE RULES:
✗ DO NOT use emoji images (🔥, 💡, ⚡, 🎯, etc.)
✗ DO NOT add any decorative icons or symbols as images
✗ ONLY use actual product screenshots/interface images from the list above
✗ NO affiliate marketer photos, NO personal photos, NO model photos
✓ Only embed images that show: product dashboard, features, workflows, pricing tables
✓ Use 2-3 images MAXIMUM throughout the article
✓ Only use images if they clearly show the product interface/features
✓ Skip images that show people's faces or promotional models

IMAGE PLACEMENT GUIDELINES:
- After "What is {product_name}?" section (product overview/dashboard)
- In "Key Features" section (ONE feature screenshot only)
- In "How Does It Work?" section (workflow/process image)
- DO NOT add images just for decoration

ARTICLE STRUCTURE:

1. **Introduction** (2-3 paragraphs)
   - Hook with the problem this product solves
   - Brief overview of what the product is
   - Who it's for
   - NO IMAGES in introduction

2. **What is {product_name}?** (H2)
   - Detailed explanation
   - Main purpose and functionality
   - Target audience
   - [ADD ONE PRODUCT INTERFACE IMAGE HERE IF AVAILABLE]

3. **Key Features** (H2)
   - List 5-10 main features with explanations
   - Use H3 subheadings for each major feature
   - [ADD ONE FEATURE SCREENSHOT IF AVAILABLE]
   - Include practical use cases

4. **How Does It Work?** (H2)
   - Step-by-step process
   - User experience overview
   - [ADD ONE WORKFLOW IMAGE IF AVAILABLE]

5. **Benefits of Using {product_name}** (H2)
   - Concrete benefits
   - Real-world applications
   - Time/money savings
   - NO IMAGES in this section

6. **Pricing & Packages** (H2)
   - Price breakdown (${price})
   - Value analysis
   - Money-back guarantee details
   - NO affiliate links or buttons

7. **Pros and Cons** (H2)
   - Honest pros (5-7 points)
   - Honest cons (3-5 points)
   - Use tables for comparison

8. **Who Should Buy {product_name}?** (H2)
   - Ideal customers
   - Who will benefit most
   - Who shouldn't buy (be honest)

9. **Bonuses & Special Offers** (H2)
   - List bonus items
   - Limited-time offers
   - NO affiliate promotions

10. **{product_name} vs Competitors** (H2)
    - Comparison with 2-3 similar products
    - Unique selling points
    - Comparison table

11. **Frequently Asked Questions** (H2)
    - 8-10 relevant questions with answers
    - Use H3 for each question

12. **Final Verdict** (H2)
    - Overall assessment
    - Rating (X/10)
    - Final recommendation
    - NO call-to-action or affiliate links

WRITING STYLE:
- Write for a 10-year-old's reading level
- Use "you" to address readers
- Max 3 sentences per paragraph
- Conversational but professional tone
- Include specific examples
- Be honest about limitations
- Use bullet points and lists where appropriate
- Include comparison tables
- Add "Quick Summary" boxes

SEO OPTIMIZATION:
- Naturally include product name throughout
- Use semantic keywords: software review, {creator} product, {platform} launch, digital marketing tools
- Include LSI keywords: features, benefits, pricing, honest review, worth it
- Meta-friendly structure

SPECIAL ELEMENTS:
- Add a "Quick Verdict" box at the top after intro
- Include pricing calculator if relevant
- Use comparison tables
- Add "Key Takeaways" box before conclusion

CRITICAL REQUIREMENTS:
- Article must be AT LEAST 2500 words (MINIMUM - aim for 3000+ words)
- Write in Jekyll format (NO front matter, that's added separately)
- Use H2, H3, H4 headings (NO H1)
- Be balanced - include genuine cons
- Include affiliate disclosure: "This review contains affiliate links, meaning we may earn a commission if you make a purchase through our links at no extra cost to you."
- DO NOT include any affiliate links, buttons, or CTAs in the content
- Focus on informative, educational content only
- Add comparison tables in markdown format
- Include FAQ schema-friendly format
- MAXIMUM 3 images total in the entire article
- ONLY product interface/screenshot images - NO decorative images
- NO emoji images or icon graphics

Write the complete article now with ONLY relevant product images embedded (maximum 3):
"""
    
    print("🤖 Generating comprehensive review article...")
    print("⚡ Using Groq (Llama 3.3 70B) - Lightning fast inference!")
    
    response_text = generate_content(prompt, max_tokens=4000)
    
    content = remove_front_matter(response_text)
    
    # Remove any emoji or decorative images that AI might have added
    # Pattern: ![emoji or single char](url)
    content = re.sub(r'!\[[\U0001F300-\U0001F9FF].*?\]\(.*?\)', '', content)  # Remove emoji images
    content = re.sub(r'!\[[🔥💡⚡🎯✨🚀💪👍✅❌⚠️📊📈📉💰🎁]\]\(.*?\)', '', content)  # Common emojis
    
    print(f"✅ Article generated ({len(content)} characters)")
    
    # Count embedded images
    image_count = len(re.findall(r'!\[.*?\]\(.*?\)', content))
    print(f"📸 Embedded {image_count} images in the article")
    
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