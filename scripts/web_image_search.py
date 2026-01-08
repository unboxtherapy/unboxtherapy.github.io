"""Reliable web image search with STRICT product-only filtering"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus, urljoin, urlparse
import json

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def is_product_image(url, alt_text="", context=""):
    """
    STRICT validation: Is this actually a product screenshot/interface?
    Returns True ONLY for genuine product images
    """
    url_lower = url.lower()
    alt_lower = alt_text.lower()
    context_lower = context.lower()
    
    combined = f"{url_lower} {alt_lower} {context_lower}"
    
    # IMMEDIATE REJECTION - These are NEVER product images
    strict_blocklist = [
        # People/faces
        'face', 'person', 'people', 'human', 'man', 'woman', 'guy', 'girl',
        'headshot', 'portrait', 'photo', 'selfie', 'profile', 'avatar',
        'author', 'creator', 'vendor', 'marketer', 'founder', 'ceo',
        
        # Logos and badges
        'logo', 'icon', 'badge', 'seal', 'emblem', 'stamp',
        'jvzoo', 'warriorplus', 'clickbank', 'paykickstart',
        'paypal', 'stripe', 'visa', 'mastercard',
        
        # Social media
        'facebook', 'twitter', 'instagram', 'linkedin', 'youtube',
        'social', 'share', 'follow',
        
        # Promotional graphics
        'banner', 'ad', 'advertisement', 'promo', 'sale', 'discount',
        'urgent', 'limited', 'bonus', 'free', 'countdown', 'timer',
        'testimonial', 'review-star', 'rating',
        
        # Generic stock images
        'stock', 'shutterstock', 'getty', 'istock', 'pixabay', 'unsplash',
        'placeholder', 'dummy', 'sample', 'example',
        
        # UI elements (not product screenshots)
        'button', 'arrow', 'checkmark', 'bullet', 'divider',
        
        # Common ad sizes (these are banner ads, not products)
        '728x90', '300x250', '160x600', '468x60', '120x600', '970x90',
    ]
    
    for blocked in strict_blocklist:
        if blocked in combined:
            return False
    
    # POSITIVE SIGNALS - Must have at least ONE of these
    product_indicators = [
        # Actual product interface
        'screenshot', 'interface', 'dashboard', 'panel', 'screen',
        'console', 'admin', 'backend', 'frontend', 'ui', 'ux',
        
        # Software specific
        'software', 'app', 'tool', 'platform', 'system',
        'workflow', 'process', 'feature', 'demo', 'preview',
        
        # Product packaging (for SaaS)
        'mockup', 'box', 'package', 'ecover', 'cover',
    ]
    
    has_positive_signal = any(indicator in combined for indicator in product_indicators)
    
    if not has_positive_signal:
        # No positive signals = not a product image
        return False
    
    # Check file name patterns (sometimes product screenshots have descriptive names)
    filename = url_lower.split('/')[-1].split('?')[0]
    
    # Good signs in filename
    good_filename_patterns = [
        'screenshot', 'dashboard', 'interface', 'demo', 'preview',
        'feature', 'product', 'software', 'app'
    ]
    
    # If filename contains product terms, that's a good sign
    if any(pattern in filename for pattern in good_filename_patterns):
        return True
    
    # Final check: If we got here, we have positive signals but no blocklist matches
    # This is probably a product image
    return True


def search_bing_images(query, limit=10):
    """Search Bing Images with STRICT product filtering"""
    print(f"🔍 Searching Bing Images...")
    
    try:
        url = f"https://www.bing.com/images/search?q={quote_plus(query)}"
        
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        
        # Bing stores image data in special attributes
        image_elements = soup.find_all('a', class_=re.compile('iusc'))
        
        for element in image_elements[:limit * 3]:  # Get more to filter
            m = element.get('m')
            if m:
                try:
                    data = json.loads(m)
                    image_url = data.get('murl') or data.get('turl')
                    alt_text = data.get('t', '')
                    
                    if image_url and is_product_image(image_url, alt_text):
                        images.append({
                            'url': image_url,
                            'alt': alt_text or query,
                            'source': 'bing'
                        })
                        print(f"📸 Valid: {image_url[:80]}...")
                        
                        if len(images) >= limit:
                            break
                    else:
                        print(f"❌ Rejected: {image_url[:60]}... (not product image)")
                except:
                    continue
        
        return images
        
    except Exception as e:
        print(f"❌ Bing search failed: {e}")
        return []


def search_duckduckgo_images(query, limit=10):
    """Search DuckDuckGo for images with STRICT filtering"""
    print(f"🦆 Searching DuckDuckGo Images...")
    
    try:
        url = "https://duckduckgo.com/"
        
        session = requests.Session()
        session.headers.update({'User-Agent': USER_AGENT})
        
        response = session.get(url, timeout=10)
        
        search_url = f"https://duckduckgo.com/?q={quote_plus(query)}&iax=images&ia=images"
        response = session.get(search_url, timeout=10)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        
        img_tags = soup.find_all('img', src=True)
        
        for img in img_tags:
            src = img.get('src')
            alt = img.get('alt', '')
            
            if src and src.startswith('http') and is_product_image(src, alt):
                images.append({
                    'url': src,
                    'alt': alt or query,
                    'source': 'duckduckgo'
                })
                print(f"📸 Valid: {src[:80]}...")
                
                if len(images) >= limit:
                    break
        
        return images
        
    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {e}")
        return []


def search_product_hunt(product_name, limit=5):
    """Search Product Hunt ONLY if product name suggests it might be listed there"""
    print(f"🚀 Searching Product Hunt...")
    
    # Only search Product Hunt for products that look like real SaaS tools
    product_lower = product_name.lower()
    
    # Skip if it looks like a spammy product
    spam_indicators = ['ai suite', 'bundle', 'mega', 'ultra', 'pro max', 'ultimate']
    if any(spam in product_lower for spam in spam_indicators):
        print(f"⚠️  Product name suggests low-quality tool, skipping Product Hunt")
        return []
    
    try:
        search_query = quote_plus(product_name)
        url = f"https://www.producthunt.com/search?q={search_query}"
        
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=15)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        
        img_tags = soup.find_all('img', src=True)
        
        for img in img_tags:
            src = img.get('src')
            alt = img.get('alt', '')
            
            if src and 'producthunt' in src and is_product_image(src, alt, 'product hunt'):
                images.append({
                    'url': src,
                    'alt': product_name,
                    'source': 'producthunt'
                })
                print(f"📸 Valid: {src[:80]}...")
                
                if len(images) >= limit:
                    break
        
        return images
        
    except Exception as e:
        print(f"❌ Product Hunt search failed: {e}")
        return []


def search_product_images_web(product_name, creator="", limit=10):
    """
    Search for ONLY genuine product screenshots/interfaces
    Much stricter filtering - will return empty if no valid images found
    """
    print(f"\n{'='*60}")
    print(f"🌐 Searching Web for PRODUCT SCREENSHOTS ONLY")
    print(f"🎯 Product: {product_name}")
    if creator:
        print(f"👤 Creator: {creator}")
    print(f"⚠️  STRICT MODE: Only genuine product images will be returned")
    print(f"{'='*60}")
    
    all_images = []
    
    # Build focused search query for product screenshots
    search_terms = [product_name]
    if creator and creator not in ["Unknown Creator", ""]:
        search_terms.append(creator)
    
    # Add terms to specifically find product screenshots
    search_terms.extend(["software screenshot", "dashboard"])
    
    query = " ".join(search_terms)
    
    # Try Bing first (best for product searches)
    print(f"\n{'─'*60}")
    print(f"📡 Source: Bing Images")
    print(f"{'─'*60}")
    
    try:
        images = search_bing_images(query, limit=limit)
        if images:
            all_images.extend(images)
            print(f"✅ Bing: Found {len(images)} valid product images")
        else:
            print(f"⚠️  Bing: No valid product images found")
    except Exception as e:
        print(f"❌ Bing error: {e}")
    
    # If we still don't have enough, try DuckDuckGo
    if len(all_images) < 3:
        print(f"\n{'─'*60}")
        print(f"📡 Source: DuckDuckGo")
        print(f"{'─'*60}")
        
        try:
            images = search_duckduckgo_images(query, limit=5)
            if images:
                all_images.extend(images)
                print(f"✅ DuckDuckGo: Found {len(images)} valid product images")
        except Exception as e:
            print(f"❌ DuckDuckGo error: {e}")
    
    # Try Product Hunt only if we still have nothing
    if len(all_images) == 0:
        print(f"\n{'─'*60}")
        print(f"📡 Source: Product Hunt (last resort)")
        print(f"{'─'*60}")
        
        try:
            images = search_product_hunt(product_name, limit=3)
            if images:
                all_images.extend(images)
                print(f"✅ Product Hunt: Found {len(images)} valid product images")
        except Exception as e:
            print(f"❌ Product Hunt error: {e}")
    
    # Remove duplicates
    seen_urls = set()
    unique_images = []
    for img in all_images:
        if img['url'] not in seen_urls:
            seen_urls.add(img['url'])
            unique_images.append(img)
    
    result = unique_images[:limit]
    
    print(f"\n{'='*60}")
    print(f"📊 Search Complete")
    print(f"{'='*60}")
    
    if result:
        print(f"✅ Found {len(result)} valid product screenshots")
        print(f"\n📸 Selected images:")
        for i, img in enumerate(result[:3], 1):
            print(f"   {i}. {img['url'][:70]}...")
            print(f"      Source: {img['source']}")
    else:
        print(f"⚠️  NO valid product images found")
        print(f"💡 This means:")
        print(f"   - No product screenshots available online")
        print(f"   - Product may be too new or obscure")
        print(f"   - Post will be published WITHOUT featured image")
    
    return result


def get_product_image_from_web(product_name, creator=""):
    """
    Get best featured image for product from the web
    Returns None if no valid product image is found (STRICT)
    """
    images = search_product_images_web(product_name, creator, limit=10)
    
    if not images:
        print(f"\n⚠️  NO valid product images found for {product_name}")
        print(f"💡 Recommendation: Publish post without featured image")
        return None
    
    # Return the first (best) image
    print(f"\n✅ Best product image selected:")
    print(f"   URL: {images[0]['url'][:80]}...")
    print(f"   Alt: {images[0]['alt']}")
    print(f"   Source: {images[0]['source']}")
    
    return images[0]


if __name__ == "__main__":
    # Test with a real product
    print("Testing STRICT Web Image Search...")
    
    # Test 1: Real product that should have images
    test_product = "Notion"
    print(f"\n{'='*60}")
    print(f"Test 1: {test_product} (should find valid images)")
    print(f"{'='*60}")
    
    images = search_product_images_web(test_product, limit=5)
    
    if images:
        print(f"\n✅ SUCCESS: Found {len(images)} valid images")
    else:
        print(f"\n⚠️  No valid images found")
    
    # Test 2: Obscure/fake product that shouldn't have images
    test_product_2 = "SuperAI Mega Ultra Suite Pro Max 9000"
    print(f"\n{'='*60}")
    print(f"Test 2: {test_product_2} (should find NO images)")
    print(f"{'='*60}")
    
    images_2 = search_product_images_web(test_product_2, limit=5)
    
    if images_2:
        print(f"\n⚠️  WARNING: Found {len(images_2)} images (should be 0)")
    else:
        print(f"\n✅ SUCCESS: Correctly found NO valid images")