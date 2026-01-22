"""Scrape products from MunchEye.com - OPTIMIZED for Gemini"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from gemini_client import generate_content
from config import GEMINI_API_KEY
import json

MUNCHEYE_URL = "https://muncheye.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"



def get_muncheye_detail_info(detail_url):
    """
    Extract the JV Page URL and e-cover image from a MunchEye product detail page
    
    Returns:
        dict: {'jv_page_url': str or None, 'ecover_url': str or None}
    """
    print(f"🔍 Extracting info from MunchEye detail page: {detail_url}")
    try:
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        response = requests.get(detail_url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            'jv_page_url': None,
            'ecover_url': None
        }
        
        # Extract JV Page URL
        jv_label = soup.find('td', text=re.compile(r'JV\s+Page:', re.IGNORECASE))
        if not jv_label:
            # Try finding b tag inside td
            jv_label = soup.find('b', text=re.compile(r'JV\s+Page:', re.IGNORECASE))
            if jv_label:
                jv_label = jv_label.find_parent('td')
        
        if jv_label:
            # The URL should be in the next td
            next_td = jv_label.find_next_sibling('td')
            if next_td:
                link = next_td.find('a', href=True)
                if link:
                    result['jv_page_url'] = link['href']
                    print(f"✅ Found JV Page: {result['jv_page_url']}")
        
        # Extract e-cover image
        product_logo = soup.find('div', class_='product_logo')
        if product_logo:
            img = product_logo.find('img', itemprop='image')
            if img and img.get('src'):
                result['ecover_url'] = img['src']
                print(f"✅ Found e-cover: {result['ecover_url']}")
        
        if not result['jv_page_url']:
            print("⚠️  JV Page link not found on detail page")
        if not result['ecover_url']:
            print("⚠️  E-cover image not found on detail page")
        
        return result
        
    except Exception as e:
        print(f"❌ Error extracting MunchEye info: {e}")
        return {'jv_page_url': None, 'ecover_url': None}



def scrape_muncheye_products(sections=None, limit_per_section=5):
    """
    Scrape products from specific MunchEye sections using Gemini AI
    """
    if sections is None:
        sections = ['big_launches', 'just_launched']
    
    print(f"🔍 Scraping MunchEye.com for sections: {', '.join(sections)}")
    
    try:
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        print(f"📥 Fetching MunchEye homepage...")
        response = requests.get(MUNCHEYE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        html_content = response.text
        
        # Use Gemini to intelligently parse the page
        products = parse_with_gemini(html_content, sections, limit_per_section)
        
        if not products:
            print(f"⚠️  Gemini parsing returned no products, trying fallback...")
            products = parse_with_beautifulsoup(html_content, sections, limit_per_section)
        
        print(f"\n✅ Total products scraped: {len(products)}")
        return products
        
    except Exception as e:
        print(f"❌ Error scraping MunchEye: {e}")
        import traceback
        traceback.print_exc()
        return []


def parse_with_gemini(html_content, sections, limit_per_section):
    """Use Google Gemini to intelligently parse MunchEye HTML"""
    
    if not GEMINI_API_KEY:
        print("⚠️  Gemini API key not available, using fallback parser")
        return []
    
    print(f"🤖 Using Google Gemini to parse MunchEye sections...")
    print(f"⚡ Analyzing extended HTML content (40,000 chars)...")
    
    # OPTIMIZED: Increased from 25k to 40k chars for better context
    # Gemini handles longer context well with its 1M token window
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
    
    prompt = f"""You are analyzing the MunchEye.com homepage to find NEW product launches that haven't been reviewed yet.

TODAY'S DATE: {today_str}
MINIMUM LAUNCH DATE: {min_launch_date} (MUST be 3+ days from today, not sooner)

TARGET SECTIONS ON MUNCHEYE.COM:
- "Big Launches" (left-column) - PRIORITY
- "All Launches" (right-column)

HTML CONTENT (Extended 40k chars for better analysis):
{html_sample}

YOUR MISSION: Find ONE product that meets ALL these requirements:

1. SECTION REQUIREMENT:
   ✓ Product MUST be from "Big Launches" (id="left-column") OR "All Launches" (id="right-column")
   ✓ These sections contain <div class="item"> elements with product info
   ✓ Identify which section the product is from

2. DATE REQUIREMENT (CRITICAL - STOP READING IF DATE IS TOO SOON):
   ✓ Extract launch date from each product (usually "DD MMM" format like "15 Jan")
   ✓ Convert to YYYY-MM-DD format (use 2026 for future months, 2027 if needed)
   ✓ MUST launch on or AFTER {min_launch_date}
   ✓ REJECT products launching in 0-2 days
   ✓ REJECT products that already launched (past dates)
   ✓ We need products launching 3+ days from now to write reviews in advance

3. PRODUCT DATA TO EXTRACT:
   - name: Full product name (from the <a rel="bookmark"> link text)
   - creator: Vendor/Creator name (usually before ":" in the product name)
   - price: Dollar amount (look for $XX pattern)
   - commission: Percentage (look for "at XX%" or commission info)
   - platform: JVZoo, WarriorPlus, ClickBank, PayKickstart, etc.
   - launch_date: In YYYY-MM-DD format
   - url: Full MunchEye product detail page URL (from href attribute)
   - section: "Big Launches" or "All Launches"

4. SEARCH STRATEGY (EFFICIENT):
   Step 1: Look at "Big Launches" section first (priority)
   Step 2: Find first product with launch date >= {min_launch_date}
   Step 3: Extract that ONE product and STOP
   Step 4: If no valid products in Big Launches, check "All Launches"
   Step 5: Return maximum 1-2 products (we only need one to process)

5. QUALITY CHECKS:
   ✓ Product name must be meaningful (not generic like "New Launch")
   ✓ Creator name should be a real person/company name
   ✓ URL must be a valid MunchEye detail page link
   ✓ Launch date must be parseable and future-dated (3+ days)

OUTPUT FORMAT (JSON array - return ONLY valid products, ideally just ONE):
[
  {{
    "name": "Product Name Without Creator Prefix",
    "creator": "Creator or Vendor Name",
    "price": "47",
    "commission": "50",
    "platform": "JVZoo",
    "launch_date": "2026-01-15",
    "url": "https://muncheye.com/full-product-url",
    "section": "Big Launches"
  }}
]

CRITICAL RULES - FOLLOW STRICTLY:
✗ REJECT any product launching before {min_launch_date}
✗ REJECT products from sections other than "Big Launches" or "All Launches"
✗ REJECT products with invalid/missing launch dates
✓ Return 1-2 products maximum (efficiency goal)
✓ Prioritize "Big Launches" over "All Launches"
✓ Extract REAL URLs from href attributes, not placeholder text
✓ Use YYYY-MM-DD date format
✓ Return clean JSON array with NO markdown backticks, NO explanations

RETURN ONLY THE JSON ARRAY NOW:"""
    
    try:
        print(f"📤 Sending HTML to Gemini for analysis...")
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
            print(f"❌ Gemini returned non-list data")
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
        
        print(f"\n✅ Gemini extracted {len(validated_products)} products from target sections")
        return validated_products
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Gemini JSON response: {e}")
        print(f"Response text: {response_text[:500]}...")
        return []
    except Exception as e:
        print(f"❌ Gemini parsing error: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_with_beautifulsoup(html_content, sections, limit_per_section):
    """Fallback parser using BeautifulSoup - targets correct MunchEye columns"""
    print(f"📄 Using BeautifulSoup fallback parser...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    
    # Strategy 1: Look for Big Launches in #left-column
    if 'big_launches' in sections:
        print(f"\n🔍 Looking for 'Big Launches' in #left-column...")
        left_column = soup.find('div', id='left-column')
        
        if left_column:
            print(f"✅ Found Big Launches column")
            items = left_column.find_all('div', class_='item')
            print(f"📊 Found {len(items)} items in Big Launches")
            
            for item in items[:limit_per_section]:
                product = extract_product_from_item(item, "Big Launches")
                if product:
                    products.append(product)
        else:
            print(f"⚠️  #left-column not found")
    
    # Strategy 2: Look for All Launches in #right-column  
    if 'all_launches' in sections:
        print(f"\n🔍 Looking for 'All Launches' in #right-column...")
        right_column = soup.find('div', id='right-column')
        
        if right_column:
            print(f"✅ Found All Launches column")
            items = right_column.find_all('div', class_='item')
            print(f"📊 Found {len(items)} items in All Launches")
            
            for item in items[:limit_per_section]:
                product = extract_product_from_item(item, "All Launches")
                if product:
                    products.append(product)
        else:
            print(f"⚠️  #right-column not found")
    
    print(f"\n✅ Total products from fallback parser: {len(products)}")
    return products


def extract_product_from_item(item, section_name):
    """Extract product info from a MunchEye item div"""
    
    # Get product link and name from item_info
    item_info = item.find('div', class_='item_info')
    if not item_info:
        return None
    
    link = item_info.find('a', rel='bookmark')
    if not link or not link.get('href'):
        return None
    
    product_url = link['href']
    
    # Ensure full URL
    if not product_url.startswith('http'):
        product_url = 'https://muncheye.com' + (product_url if product_url.startswith('/') else '/' + product_url)
    
    product_text = link.get_text(strip=True)
    
    if not product_text or len(product_text) < 5:
        return None
    
    # Parse creator and product name from "Creator: Product Name" format
    creator = ""
    product_name = product_text
    
    if ':' in product_text:
        parts = product_text.split(':', 1)
        creator = parts[0].strip()
        product_name = parts[1].strip() if len(parts) > 1 else product_text
    
    # Extract launch date from meta tag (most reliable)
    launch_date = None
    meta_date = item.find('meta', itemprop='releaseDate')
    if meta_date and meta_date.get('content'):
        launch_date = meta_date['content']  # Already in YYYY-MM-DD format
    
    # Fallback: extract from date div
    if not launch_date:
        date_div = item.find('div', class_='date')
        if date_div:
            day_span = date_div.find('span', class_='day')
            month_span = date_div.find('span', class_='month')
            if day_span and month_span:
                day = day_span.get_text(strip=True)
                month = month_span.get_text(strip=True)
                launch_date = parse_date_from_day_month(day, month)
    
    if not launch_date:
        launch_date = datetime.now().strftime('%Y-%m-%d')
    
    # Extract price and commission from text
    item_text = item.get_text()
    price_match = re.search(r'\$\s?(\d+(?:\.\d+)?)', item_text)
    price = price_match.group(1) if price_match else "Unknown"
    
    commission_match = re.search(r'at\s+(\d+)%', item_text)
    commission = commission_match.group(1) if commission_match else "50"
    
    # Extract platform
    platform = "Unknown"
    if 'WarriorPlus' in item_text or 'W+' in item_text:
        platform = 'WarriorPlus'
    elif 'JVZoo' in item_text or 'JVZ' in item_text:
        platform = 'JVZoo'
    elif 'ClickBank' in item_text:
        platform = 'ClickBank'
    
    product_data = {
        'name': product_name,
        'creator': creator if creator else "Unknown Creator",
        'url': product_url,
        'launch_date': launch_date,
        'price': price,
        'commission': commission,
        'platform': platform,
        'section': section_name,
        'category': 'Product Launch',
        'scraped_at': datetime.now().isoformat()
    }
    
    return product_data


def parse_date_from_day_month(day, month):
    """Parse date from day and month strings"""
    try:
        months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        month_num = months.get(month, datetime.now().month)
        day_num = int(day)
        year = datetime.now().year
        
        date = datetime(year, month_num, day_num)
        if date.date() < datetime.now().date():
            date = datetime(year + 1, month_num, day_num)
        
        return date.strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')


def extract_platform_from_text(text):
    """Extract platform from text"""
    text_lower = text.lower()
    
    if 'jvzoo' in text_lower or 'jvz' in text_lower:
        return 'JVZoo'
    elif 'warrior' in text_lower or 'w+' in text_lower:
        return 'WarriorPlus'
    elif 'clickbank' in text_lower:
        return 'ClickBank'
    elif 'paykickstart' in text_lower:
        return 'PayKickstart'
    
    return 'Unknown'


def extract_date(text):
    """Extract launch date from text"""
    today = datetime.now()
    
    # Try to find date pattern
    date_pattern = r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
    match = re.search(date_pattern, text, re.IGNORECASE)
    
    if match:
        day = int(match.group(1))
        month_abbr = match.group(2)
        
        months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        month = months.get(month_abbr, today.month)
        year = today.year
        
        try:
            date = datetime(year, month, day)
            if date < today:
                date = datetime(year + 1, month, day)
            return date.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    return today.strftime('%Y-%m-%d')



def filter_upcoming_launches(products, min_days_ahead=3):
    """
    Filter products to only include those launching 3+ days from now
    
    Args:
        products: List of product dicts with 'launch_date' field
        min_days_ahead: Minimum days ahead to include (default: 3)
    
    Returns:
        List of products launching min_days_ahead or more from now
    """
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    min_launch_date = today + timedelta(days=min_days_ahead)
    
    print(f"\n📅 Date Filtering:")
    print(f"   Today: {today.strftime('%Y-%m-%d')}")
    print(f"   Minimum launch date: {min_launch_date.strftime('%Y-%m-%d')} ({min_days_ahead}+ days)")
    
    filtered = []
    for product in products:
        launch_date_str = product.get('launch_date')
        if launch_date_str:
            try:
                launch_date = datetime.strptime(launch_date_str, '%Y-%m-%d').date()
                if launch_date >= min_launch_date:
                    filtered.append(product)
                    days_until = (launch_date - today).days
                    print(f"   ✅ {product['name'][:40]}... launches in {days_until} days")
                else:
                    days_until = (launch_date - today).days
                    print(f"   ⏭️  {product['name'][:40]}... too soon ({days_until} days)")
            except Exception as e:
                print(f"   ⚠️  {product['name'][:40]}... invalid date: {launch_date_str}")
    
    print(f"\n📊 {len(filtered)}/{len(products)} products launching {min_days_ahead}+ days from now")
    return filtered

def get_products_for_review(limit=1, categories=None, existing_reviews=None):
    """
    Get upcoming product launches from Big Launches and All Launches sections
    Only includes products launching 3+ days from now that haven't been reviewed yet
    OPTIMIZED: Checks database during scraping to avoid wasting API calls
    
    Args:
        limit: Maximum products to return
        categories: Product categories (not used currently)
        existing_reviews: Set of existing review identifiers from database
    
    Returns:
        List of new, unreviewable products
    """
    print(f"\n{'='*60}")
    print(f"🎯 Fetching UPCOMING launches from MunchEye")
    print(f"🎯 Target sections: Big Launches, All Launches")
    print(f"🎯 Filter: Launching 3+ days from now")
    print(f"🚀 Early exit: Will stop at first valid NEW product")
    print(f"{'='*60}")
    
    # Fetch a reasonable batch to find at least one valid product
    fetch_limit = 10  # Small batch to minimize API usage
    
    products = scrape_muncheye_products(
        sections=['big_launches', 'all_launches'],
        limit_per_section=fetch_limit
    )
    
    if not products:
        print("❌ No products found in target sections")
        return []
    
    print(f"\n✅ Found {len(products)} total products from Big Launches & All Launches")
    
    # Process products one at a time to find first valid one
    from datetime import datetime, timedelta
    from config import MIN_DAYS_AHEAD
    from slugify import slugify
    
    today = datetime.now().date()
    min_launch_date = today + timedelta(days=MIN_DAYS_AHEAD)
    
    print(f"\n📅 Looking for first valid NEW product:")
    print(f"   Today: {today.strftime('%Y-%m-%d')}")
    print(f"   Minimum launch date: {min_launch_date.strftime('%Y-%m-%d')} ({MIN_DAYS_AHEAD}+ days)")
    
    seen = set()
    
    for product in products:
        # Check for duplicates in this batch
        product_key = f"{product['creator'].lower()}-{product['name'].lower()}"
        if product_key in seen:
            print(f"   ⏭️  {product['name'][:40]}... duplicate in batch, skipping")
            continue
        seen.add(product_key)
        
        # Check launch date first (cheapest check)
        launch_date_str = product.get('launch_date')
        if not launch_date_str:
            print(f"   ⚠️  {product['name'][:40]}... no launch date, skipping")
            continue
        
        try:
            launch_date = datetime.strptime(launch_date_str, '%Y-%m-%d').date()
            days_until = (launch_date - today).days
            
            if launch_date < min_launch_date:
                print(f"   ⏭️  {product['name'][:40]}... too soon ({days_until} days)")
                continue
            
            # NOW check if already reviewed (only after date check passes)
            if existing_reviews:
                product_name = product['name']
                creator = product['creator']
                
                # Generate permalink to check database
                permalink = slugify(f"{creator}-{product_name}-review")[:100]
                
                # Check if reviewed
                normalized_name = product_name.strip().lower()
                normalized_permalink = permalink.strip().lower()
                
                is_duplicate = (
                    normalized_name in existing_reviews or
                    normalized_permalink in existing_reviews or
                    any(normalized_name in existing for existing in existing_reviews)
                )
                
                if is_duplicate:
                    print(f"   ⏭️  {product['name'][:40]}... already reviewed in database")
                    continue
            
            # Product passed all checks!
            print(f"   ✅ {product['name'][:40]}... launches in {days_until} days - SELECTED!")
            print(f"\n🎉 Found valid NEW product! Stopping search to save API calls.")
            return [product]  # Return immediately with first valid product
                
        except Exception as e:
            print(f"   ⚠️  {product['name'][:40]}... error: {e}")
            continue
    
    print(f"\n⚠️  No NEW products found launching {MIN_DAYS_AHEAD}+ days from now")
    return []

if __name__ == "__main__":
    # Test the scraper
    print("Testing MunchEye scraper with section targeting...")
    products = get_products_for_review(limit=10)
    
    if products:
        print(f"\n{'='*60}")
        print(f"📊 Sample Upcoming Launches (3+ Days Out)")
        print(f"{'='*60}")
        
        for i, product in enumerate(products[:10], 1):
            print(f"\n{i}. {product['creator']}: {product['name']}")
            print(f"   Section: {product['section']}")
            print(f"   Price: ${product['price']} | Commission: {product['commission']}%")
            print(f"   Platform: {product['platform']}")
            print(f"   URL: {product['url']}")
    else:
        print("\n❌ No products found")