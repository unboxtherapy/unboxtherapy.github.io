"""Scrape products from MunchEye.com"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time

MUNCHEYE_URL = "https://muncheye.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def scrape_muncheye_products(sections=None, limit_per_section=5):
    """
    Scrape products from MunchEye
    
    Args:
        sections: List of sections to scrape ['big_launches', 'just_launched', 'all_launches']
        limit_per_section: Number of products to get from each section
    
    Returns:
        List of product dictionaries
    """
    if sections is None:
        sections = ['big_launches', 'just_launched']
    
    print(f"🔍 Scraping MunchEye.com...")
    
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(MUNCHEYE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        # Scrape Big Launches
        if 'big_launches' in sections:
            print(f"\n📊 Scraping Big Launches...")
            big_launches = scrape_big_launches(soup, limit_per_section)
            products.extend(big_launches)
        
        # Scrape Just Launched
        if 'just_launched' in sections:
            print(f"\n🚀 Scraping Just Launched...")
            just_launched = scrape_just_launched(soup, limit_per_section)
            products.extend(just_launched)
        
        # Scrape All Launches (future products)
        if 'all_launches' in sections:
            print(f"\n📅 Scraping All Launches...")
            all_launches = scrape_all_launches(soup, limit_per_section)
            products.extend(all_launches)
        
        print(f"\n✅ Total products scraped: {len(products)}")
        return products
        
    except Exception as e:
        print(f"❌ Error scraping MunchEye: {e}")
        return []


def scrape_big_launches(soup, limit):
    """Scrape Big Launches section"""
    products = []
    
    # Find the "Big Launches" section
    big_launches_section = soup.find('h2', text='Big Launches')
    if not big_launches_section:
        print("⚠️ Big Launches section not found")
        return products
    
    # Get the table/list after the heading
    launches_container = big_launches_section.find_next_sibling()
    if not launches_container:
        return products
    
    # Find all launch entries
    launch_items = launches_container.find_all(['div', 'li', 'tr'], limit=limit)
    
    for item in launch_items[:limit]:
        try:
            product = extract_product_info(item, 'Big Launch')
            if product:
                products.append(product)
        except Exception as e:
            print(f"⚠️ Error parsing big launch item: {e}")
            continue
    
    return products


def scrape_just_launched(soup, limit):
    """Scrape Just Launched section"""
    products = []
    
    # Find the "Just Launched" section
    just_launched_section = soup.find('h2', text='Just Launched')
    if not just_launched_section:
        print("⚠️ Just Launched section not found")
        return products
    
    launches_container = just_launched_section.find_next_sibling()
    if not launches_container:
        return products
    
    launch_items = launches_container.find_all(['div', 'li', 'tr'], limit=limit)
    
    for item in launch_items[:limit]:
        try:
            product = extract_product_info(item, 'Just Launched')
            if product:
                products.append(product)
        except Exception as e:
            print(f"⚠️ Error parsing just launched item: {e}")
            continue
    
    return products


def scrape_all_launches(soup, limit):
    """Scrape All Launches section (future products)"""
    products = []
    
    all_launches_section = soup.find('h2', text='All Launches')
    if not all_launches_section:
        print("⚠️ All Launches section not found")
        return products
    
    launches_container = all_launches_section.find_next_sibling()
    if not launches_container:
        return products
    
    launch_items = launches_container.find_all(['div', 'li', 'tr'], limit=limit)
    
    for item in launch_items[:limit]:
        try:
            product = extract_product_info(item, 'Upcoming Launch')
            if product:
                products.append(product)
        except Exception as e:
            print(f"⚠️ Error parsing all launch item: {e}")
            continue
    
    return products


def extract_product_info(element, category):
    """Extract product information from HTML element"""
    
    # Find link to product page
    link = element.find('a')
    if not link:
        return None
    
    product_url = link.get('href', '')
    if not product_url.startswith('http'):
        product_url = MUNCHEYE_URL.rstrip('/') + '/' + product_url.lstrip('/')
    
    # Extract product name
    product_name = link.get_text(strip=True)
    
    # Try to extract creator name (usually before colon)
    creator = ""
    if ':' in product_name:
        parts = product_name.split(':', 1)
        creator = parts[0].strip()
        product_name = parts[1].strip() if len(parts) > 1 else product_name
    
    # Extract date
    date_text = element.get_text()
    launch_date = extract_date(date_text)
    
    # Extract price and commission
    price_match = re.search(r'\$?(\d+(?:\.\d+)?)', date_text)
    price = price_match.group(1) if price_match else "N/A"
    
    commission_match = re.search(r'at\s+(\d+)%', date_text)
    commission = commission_match.group(1) if commission_match else "N/A"
    
    # Extract platform (JVZoo, WarriorPlus, etc.)
    platform = extract_platform(element)
    
    product_data = {
        'name': product_name,
        'creator': creator,
        'url': product_url,
        'launch_date': launch_date,
        'price': price,
        'commission': commission,
        'platform': platform,
        'category': category,
        'scraped_at': datetime.now().isoformat()
    }
    
    print(f"✅ Found: {creator}: {product_name} (${price} at {commission}%)")
    
    return product_data


def extract_date(text):
    """Extract launch date from text"""
    today = datetime.now()
    
    # Try to find date pattern (e.g., "6 Jan", "Jan 6")
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
        
        # If date is in the past this year, assume next year
        try:
            date = datetime(year, month, day)
            if date < today:
                date = datetime(year + 1, month, day)
            return date.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    return today.strftime('%Y-%m-%d')


def extract_platform(element):
    """Extract affiliate platform from element"""
    text = element.get_text()
    
    if 'jvzoo' in text.lower():
        return 'JVZoo'
    elif 'warrior' in text.lower():
        return 'WarriorPlus'
    elif 'clickbank' in text.lower():
        return 'ClickBank'
    elif 'paykickstart' in text.lower():
        return 'PayKickstart'
    
    # Try to find from image alt text
    img = element.find('img')
    if img:
        alt_text = img.get('alt', '').lower()
        if 'jvzoo' in alt_text:
            return 'JVZoo'
        elif 'warrior' in alt_text:
            return 'WarriorPlus'
    
    return 'Unknown'


def filter_products_for_review(products, days_threshold=7):
    """
    Filter products suitable for review
    - Recently launched (within last N days)
    - Or launching soon (within next N days)
    """
    today = datetime.now()
    filtered = []
    
    for product in products:
        try:
            launch_date = datetime.strptime(product['launch_date'], '%Y-%m-%d')
            days_diff = (launch_date - today).days
            
            # Include if launched recently or launching soon
            if -days_threshold <= days_diff <= days_threshold:
                filtered.append(product)
        except Exception as e:
            print(f"⚠️ Error filtering product: {e}")
            continue
    
    return filtered


def get_products_for_review(limit=5):
    """
    Get products ready for review
    
    Returns:
        List of products to review (will fetch 3x limit to account for duplicates)
    """
    print(f"\n{'='*60}")
    print(f"🎯 Fetching products from MunchEye")
    print(f"{'='*60}")
    
    # Scrape more products to account for potential duplicates
    fetch_limit = limit * 3
    
    products = scrape_muncheye_products(
        sections=['just_launched', 'big_launches', 'all_launches'],
        limit_per_section=fetch_limit  # Get more from each section
    )
    
    if not products:
        print("❌ No products found")
        return []
    
    # Filter for recent/upcoming products
    filtered = filter_products_for_review(products, days_threshold=30)  # Increased to 30 days
    
    # Remove duplicates based on product name
    seen = set()
    unique_products = []
    for p in filtered:
        product_key = f"{p['creator'].lower()}-{p['name'].lower()}"
        if product_key not in seen:
            seen.add(product_key)
            unique_products.append(p)
    
    print(f"\n✅ Found {len(unique_products)} unique products")
    
    # Return all unique products (will be filtered for duplicates later)
    return unique_products


if __name__ == "__main__":
    # Test the scraper
    products = get_products_for_review(limit=5)
    
    print(f"\n{'='*60}")
    print(f"📊 Review Summary")
    print(f"{'='*60}")
    
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product['creator']}: {product['name']}")
        print(f"   Price: ${product['price']} | Commission: {product['commission']}%")
        print(f"   Platform: {product['platform']}")
        print(f"   Launch: {product['launch_date']}")
        print(f"   URL: {product['url']}")