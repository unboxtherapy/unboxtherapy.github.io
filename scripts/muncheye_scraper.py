def parse_with_gemini(html_content, sections, limit_per_section):
    """Use Groq AI to intelligently parse MunchEye HTML"""
    
    if not GROQ_API_KEY:
        print("⚠️  Groq API key not available, using fallback parser")
        return []
    
    print(f"🤖 Using Groq AI (Llama 3.1 8B) to parse MunchEye sections...")
    print(f"⚡ Lightning fast analysis incoming...")
    
    # Truncate HTML to stay within token limits (Groq: 12k TPM on free tier)
    # ~4 chars per token, so 25k chars ≈ 6.25k tokens (safe margin)
    html_sample = html_content[:25000]
    
    # Get current date for context
    from datetime import datetime, timedelta
    today = datetime.now().date()
    min_launch_date = (today + timedelta(days=3)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    section_names = []
    if 'big_launches' in sections:
        section_names.append("Big Launches")
    if 'just_launched' in sections:
        section_names.append("All Launches")
    
    prompt = f"""You are analyzing the MunchEye.com homepage to extract FUTURE product launch information.

TODAY'S DATE: {today_str}
MINIMUM LAUNCH DATE: {min_launch_date} (must be 3+ days from today)

TARGET SECTIONS:
{', '.join(section_names)}

HTML CONTENT TO ANALYZE:
{html_sample}

EXTRACTION REQUIREMENTS:

1. SECTION IDENTIFICATION:
   - Look for HTML sections with IDs "left-column" (Big Launches) or "right-column" (All Launches)
   - Extract ONLY products from these specific sections
   - Identify which section each product comes from

2. DATE FILTERING (CRITICAL):
   - Extract the launch date from each product listing
   - Launch dates are typically in format "DD MMM" (e.g., "15 Jan", "20 Jan")
   - Convert to YYYY-MM-DD format (year is 2026 if date is in future, otherwise use current year logic)
   - ONLY include products launching on or after {min_launch_date}
   - SKIP products launching today, tomorrow, or within next 2 days
   - SKIP products that have already launched (past dates)

3. PRODUCT DATA EXTRACTION:
   For each valid product, extract:
   - Product name: Usually in format "Creator: Product Name" or "Vendor: Product Name"
   - Creator/Vendor: The person/company before the colon
   - Price: Dollar amount (look for $XX or $XX.XX)
   - Commission: Percentage (look for "at XX%" or similar)
   - Platform: JVZoo, WarriorPlus, ClickBank, PayKickstart, etc.
   - Launch date: Convert to YYYY-MM-DD format
   - Product URL: The link to the MunchEye product detail page

4. QUALITY CHECKS:
   - Ensure product name is meaningful (not just "Product" or "Launch")
   - Verify launch date is valid and 3+ days away
   - Extract actual clickable URLs from href attributes
   - Prefer products from "Big Launches" section when available

5. OUTPUT LIMIT:
   - Return maximum 3-4 products that meet ALL criteria above
   - Prioritize products from "Big Launches" section first
   - Only include products launching 3+ days from now

OUTPUT FORMAT (JSON array only, no markdown):
[
  {{
    "name": "Exact Product Name",
    "creator": "Vendor/Creator Name",
    "price": "47",
    "commission": "50",
    "platform": "JVZoo",
    "launch_date": "2026-01-15",
    "url": "https://muncheye.com/product-detail-page",
    "section": "Big Launches"
  }}
]

CRITICAL RULES:
✓ Extract ONLY from specified sections ("Big Launches" or "All Launches")
✓ Launch date MUST be {min_launch_date} or later (3+ days from today)
✓ Return ONLY products launching in the FUTURE
✓ Maximum 3-4 products
✓ Valid JSON array format
✓ No markdown code blocks, no explanations
✓ Extract real URLs from HTML href attributes
✓ Dates in YYYY-MM-DD format

Return ONLY the JSON array:"""
    
    try:
        print(f"🔄 Sending HTML to Groq for analysis...")
        response_text = generate_content(prompt, max_tokens=3000)
        
        # Clean response
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'^```\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        response_text = response_text.strip()
        
        # Parse JSON
        products_data = json.loads(response_text)
        
        if not isinstance(products_data, list):
            print(f"❌ Groq returned non-list data")
            return []
        
        # Validate and enrich products
        validated_products = []
        for product in products_data:
            if not product.get('name'):
                continue
            
            # Double-check date requirement
            launch_date_str = product.get('launch_date')
            if launch_date_str:
                try:
                    launch_date = datetime.strptime(launch_date_str, '%Y-%m-%d').date()
                    days_until = (launch_date - today).days
                    if days_until < 3:
                        print(f"⏭️  Skipping {product['name'][:40]}... only {days_until} days away")
                        continue
                except:
                    pass
            
            # Ensure all required fields
            validated_product = {
                'name': product.get('name', 'Unknown Product'),
                'creator': product.get('creator', 'Unknown Creator'),
                'price': str(product.get('price', 'Unknown')),
                'commission': str(product.get('commission', '50')),
                'platform': product.get('platform', 'Unknown'),
                'launch_date': product.get('launch_date', datetime.now().strftime('%Y-%m-%d')),
                'url': product.get('url', MUNCHEYE_URL),
                'section': product.get('section', 'Unknown'),
                'category': 'Product Launch',
                'scraped_at': datetime.now().isoformat()
            }
            
            validated_products.append(validated_product)
            print(f"✅ Found: {validated_product['creator']}: {validated_product['name']} (${validated_product['price']}) - Section: {validated_product['section']}")
        
        print(f"\n✅ Groq extracted {len(validated_products)} products from target sections")
        return validated_products
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Groq JSON response: {e}")
        print(f"Response text: {response_text[:500]}...")
        return []
    except Exception as e:
        print(f"❌ Groq parsing error: {e}")
        import traceback
        traceback.print_exc()
        return []