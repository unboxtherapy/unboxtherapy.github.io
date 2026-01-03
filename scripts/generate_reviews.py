"""Main script to generate product review posts from MunchEye"""
import os
import time
import datetime
from slugify import slugify

# Import all modules
from config import *
from muncheye_scraper import get_products_for_review
from sales_page_scraper import scrape_sales_page, search_product_info
from sheets_checker import get_existing_reviews, filter_unreviewed_products, display_review_stats
from review_article_generator import (
    generate_review_article,
    create_review_front_matter,
    generate_image_prompt
)
from image_generator import generate_image_freepik
from google_indexing import submit_to_google_indexing, check_indexing_status
from google_sheets_logger import log_to_google_sheets
from webpushr_notifier import send_blog_post_notification


def main():
    print("=" * 60)
    print("🚀 MunchEye Product Review Generator")
    print("=" * 60)
    
    # Verify environment variables
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found")
        return
    print("✅ GEMINI_API_KEY found")
    
    if not FREEPIK_API_KEY:
        print("❌ FREEPIK_API_KEY not found")
        return
    print("✅ FREEPIK_API_KEY found")
    
    # Get products to review
    print(f"\n{'='*60}")
    print(f"Step 1: Fetching Products from MunchEye")
    print(f"{'='*60}")
    
    # Get more products initially since we'll filter duplicates
    initial_products = get_products_for_review(limit=POSTS_PER_RUN * 3)
    
    if not initial_products:
        print("❌ No products found on MunchEye")
        return
    
    print(f"\n✅ Found {len(initial_products)} products on MunchEye")
    
    # Step 2: Check Google Sheets for existing reviews
    print(f"\n{'='*60}")
    print(f"Step 2: Checking for Duplicate Reviews")
    print(f"{'='*60}")
    
    existing_reviews = get_existing_reviews()
    display_review_stats()
    
    # Filter out already reviewed products
    products = filter_unreviewed_products(initial_products, existing_reviews)
    
    if not products:
        print("\n❌ All scraped products have already been reviewed!")
        print("💡 Try again later when new products are launched on MunchEye")
        return
    
    # Limit to desired number
    products = products[:POSTS_PER_RUN]
    
    print(f"\n✅ {len(products)} new products ready for review")
    
    posts_generated = 0
    
    for i, product in enumerate(products, 1):
        print(f"\n{'='*60}")
        print(f"📝 Processing Product {i}/{len(products)}")
        print(f"{'='*60}")
        
        product_name = product['name']
        creator = product['creator']
        
        print(f"\n📦 Product: {creator}: {product_name}")
        print(f"💰 Price: ${product['price']} | Commission: {product['commission']}%")
        print(f"🏷️  Platform: {product['platform']}")
        print(f"📅 Launch: {product['launch_date']}")
        
        # Generate permalink
        permalink = slugify(f"{creator}-{product_name}-review")[:100]
        
        # Double-check if review exists locally (belt and suspenders approach)
        today = datetime.date.today().isoformat()
        post_path = f"{POSTS_DIR}/{today}-{permalink}.md"
        image_file = f"{IMAGES_DIR}/{permalink}.webp"
        
        if os.path.exists(post_path):
            print(f"\n⚠️  Review already exists locally: {post_path}")
            print("⏭️  Skipping to next product...")
            continue
        
        # Additional check: see if similar permalink exists with different date
        existing_posts = [f for f in os.listdir(POSTS_DIR) if permalink in f]
        if existing_posts:
            print(f"\n⚠️  Similar review found: {existing_posts[0]}")
            print("⏭️  Skipping to next product...")
            continue
        
        try:
            # Step 2: Scrape sales page
            print(f"\n{'='*60}")
            print(f"Step 2: Extracting Sales Page Information")
            print(f"{'='*60}")
            
            sales_data = scrape_sales_page(product['url'])
            
            if not sales_data or not sales_data.get('features'):
                print(f"⚠️  Sales page data incomplete, searching online...")
                sales_data = search_product_info(product_name, creator)
            
            # Step 3: Generate review article
            print(f"\n{'='*60}")
            print(f"Step 3: Generating Review Article")
            print(f"{'='*60}")
            
            # Prepare affiliate link placeholder
            affiliate_link = f"https://your-affiliate-link.com/{permalink}"
            
            article_content = generate_review_article(
                product_data=product,
                sales_data=sales_data,
                affiliate_link=affiliate_link
            )
            
            print(f"✅ Article generated ({len(article_content)} characters)")
            
            # Step 4: Create front matter
            print(f"\n{'='*60}")
            print(f"Step 4: Creating Front Matter")
            print(f"{'='*60}")
            
            front_matter = create_review_front_matter(product, permalink)
            
            # Combine front matter and content
            full_article = front_matter + "\n\n" + article_content
            
            # Step 5: Generate featured image
            print(f"\n{'='*60}")
            print(f"Step 5: Generating Featured Image")
            print(f"{'='*60}")
            
            # Try to use image from sales page first
            if sales_data.get('images') and len(sales_data['images']) > 0:
                print(f"📸 Using image from sales page...")
                # Download first image from sales page
                try:
                    import requests
                    from PIL import Image
                    from io import BytesIO
                    
                    img_url = sales_data['images'][0]['url']
                    response = requests.get(img_url, timeout=30)
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    
                    # Save and optimize
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    img.save(image_file, "WEBP", quality=IMAGE_QUALITY, optimize=True)
                    
                    print(f"✅ Image downloaded and optimized")
                    
                except Exception as e:
                    print(f"⚠️  Could not download sales page image: {e}")
                    print(f"🎨 Generating AI image instead...")
                    
                    image_prompt = generate_image_prompt(f"{product_name} product review")
                    generate_image_freepik(image_prompt, image_file)
            else:
                # Generate AI image
                print(f"🎨 Generating AI image...")
                image_prompt = generate_image_prompt(f"{product_name} software review screenshot")
                generate_image_freepik(image_prompt, image_file)
            
            # Step 6: Save post
            print(f"\n{'='*60}")
            print(f"Step 6: Saving Review Post")
            print(f"{'='*60}")
            
            with open(post_path, "w", encoding="utf-8") as f:
                f.write(full_article)
            
            print(f"✅ Review saved: {post_path}")
            
            post_url = f"{SITE_DOMAIN}/{permalink}"
            
            print(f"\n{'='*60}")
            print(f"✅ SUCCESS! Review {i} Generated")
            print(f"{'='*60}")
            print(f"📰 Title: {product_name} Review")
            print(f"🌐 URL: {post_url}")
            
            posts_generated += 1
            
            # Step 7: Wait before indexing (only after last post)
            if i == len(products):
                print(f"\n{'='*60}")
                print(f"Step 7: Waiting for GitHub Pages Deployment")
                print(f"{'='*60}")
                
                for remaining in range(WAIT_TIME_BEFORE_INDEXING, 0, -30):
                    minutes = remaining // 60
                    seconds = remaining % 60
                    print(f"⏰ Time remaining: {minutes}m {seconds}s", end='\r')
                    time.sleep(30)
                
                print(f"\n✅ Wait complete!")
                
                # Step 8: Submit to Google
                print(f"\n{'='*60}")
                print(f"Step 8: Submitting to Google Search Console")
                print(f"{'='*60}")
                
                indexing_status = "Not Attempted"
                try:
                    success = submit_to_google_indexing(post_url)
                    indexing_status = "Success" if success else "Failed"
                    
                    # Check status
                    if success:
                        time.sleep(10)
                        status_result = check_indexing_status(post_url)
                        if status_result and 'latestUpdate' in status_result:
                            indexing_status = "Confirmed in Queue"
                
                except Exception as e:
                    indexing_status = f"Failed - {str(e)[:100]}"
                    print(f"⚠️  Indexing failed (non-critical): {e}")
                
                # Step 9: Log to Google Sheets
                print(f"\n{'='*60}")
                print(f"Step 9: Logging to Google Sheets")
                print(f"{'='*60}")
                
                try:
                    log_to_google_sheets(
                        title=f"{product_name} Review",
                        focus_kw=product_name,
                        permalink=permalink,
                        image_path=image_file,
                        article_content=article_content,
                        indexing_status=indexing_status
                    )
                except Exception as e:
                    print(f"⚠️  Sheets logging failed: {e}")
                
                # Step 10: Send push notification
                print(f"\n{'='*60}")
                print(f"Step 10: Sending Push Notification")
                print(f"{'='*60}")
                
                try:
                    send_blog_post_notification(
                        title=f"{product_name} Review",
                        permalink=permalink,
                        focus_kw=product_name
                    )
                except Exception as e:
                    print(f"⚠️  Push notification failed: {e}")
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ FAILED: {e}")
            print(f"{'='*60}")
            import traceback
            traceback.print_exc()
            continue
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"🎉 REVIEW GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Reviews generated: {posts_generated}")
    print(f"📊 Products processed: {len(products)}")


if __name__ == "__main__":
    main()