"""Simple JSON file tracker - replaces Google Sheets"""
import json
import os
from datetime import datetime
from config import REVIEWS_DB_FILE, SITE_DOMAIN


def load_reviews_database():
    """Load existing reviews from JSON file"""
    if not os.path.exists(REVIEWS_DB_FILE):
        return []
    
    try:
        with open(REVIEWS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading reviews database: {e}")
        return []


def save_reviews_database(reviews):
    """Save reviews to JSON file"""
    try:
        # Ensure parent directory exists
        db_dir = os.path.dirname(REVIEWS_DB_FILE)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        with open(REVIEWS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error saving reviews database: {e}")
        return False


def get_existing_reviews():
    """
    Get set of existing review permalinks and titles
    
    Returns:
        set: Set of product permalinks/titles that have been reviewed
    """
    print(f"\n{'='*60}")
    print("📊 Checking Reviews Database")
    print(f"{'='*60}")
    
    reviews = load_reviews_database()
    
    if not reviews:
        print("✅ No existing reviews found - starting fresh")
        return set()
    
    existing_reviews = set()
    
    for review in reviews:
        title = review.get('title', '').strip().lower()
        permalink = review.get('permalink', '').strip().lower()
        
        if title:
            existing_reviews.add(title)
        if permalink:
            existing_reviews.add(permalink)
    
    print(f"✅ Found {len(reviews)} existing reviews")
    
    # Show some examples
    if reviews:
        examples = reviews[-3:]  # Last 3 reviews
        print(f"\n📝 Recent reviews:")
        for ex in examples:
            print(f"   - {ex.get('title', 'Unknown')[:60]}")
    
    return existing_reviews


def log_published_review(title, focus_kw, permalink, image_path, article_content, indexing_status):
    """
    Log a newly published review
    
    Args:
        title: Review title
        focus_kw: Focus keyword
        permalink: Post permalink
        image_path: Path to featured image
        article_content: Full article text
        indexing_status: Google indexing status
    
    Returns:
        bool: Success status
    """
    print(f"\n{'='*60}")
    print(f"💾 Logging Review to Database")
    print(f"{'='*60}")
    
    try:
        # Load existing reviews
        reviews = load_reviews_database()
        
        # Extract description
        import re
        clean_content = re.sub(r'[#*`\[\]]', '', article_content)
        description = ' '.join(clean_content.split())[:200] + "..."
        
        # Create new review entry
        review_entry = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'focus_kw': focus_kw,
            'permalink': permalink,
            'url': f"{SITE_DOMAIN}/{permalink}/",
            'image_path': image_path,
            'image_url': f"{SITE_DOMAIN}/{image_path}",
            'description': description,
            'indexing_status': indexing_status,
            'word_count': len(article_content.split()),
            'published_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Add to reviews list
        reviews.append(review_entry)
        
        # Save updated database
        if save_reviews_database(reviews):
            print(f"✅ Review logged successfully!")
            print(f"📊 Total reviews in database: {len(reviews)}")
            return True
        else:
            return False
        
    except Exception as e:
        print(f"❌ Error logging review: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_review_stats():
    """
    Get statistics about published reviews
    
    Returns:
        dict: Review statistics
    """
    reviews = load_reviews_database()
    
    if not reviews:
        return {
            'total_reviews': 0,
            'last_review_date': None,
            'recent_reviews': []
        }
    
    stats = {
        'total_reviews': len(reviews),
        'last_review_date': reviews[-1].get('timestamp') if reviews else None,
        'recent_reviews': [r.get('title', 'Unknown') for r in reviews[-5:]],
        'total_words': sum(r.get('word_count', 0) for r in reviews),
        'avg_words': sum(r.get('word_count', 0) for r in reviews) // len(reviews) if reviews else 0
    }
    
    return stats


def display_review_stats():
    """Display review statistics"""
    stats = get_review_stats()
    
    print(f"\n{'='*60}")
    print("📊 Review Statistics")
    print(f"{'='*60}")
    print(f"Total reviews published: {stats['total_reviews']}")
    
    if stats['total_reviews'] > 0:
        print(f"Total words written: {stats['total_words']:,}")
        print(f"Average words per review: {stats['avg_words']}")
    
    if stats['last_review_date']:
        print(f"Last review published: {stats['last_review_date']}")
    
    if stats['recent_reviews']:
        print(f"\n📝 Recent reviews:")
        for review in stats['recent_reviews']:
            print(f"   - {review[:60]}")


def filter_unreviewed_products(products, existing_reviews):
    """
    Filter out products that have already been reviewed
    
    Args:
        products: List of product dicts
        existing_reviews: Set of existing review identifiers
    
    Returns:
        List of products not yet reviewed
    """
    if not existing_reviews:
        print("\n✅ No existing reviews to filter against")
        return products
    
    print(f"\n{'='*60}")
    print("🔍 Filtering Out Already Reviewed Products")
    print(f"{'='*60}")
    
    from slugify import slugify
    
    unreviewed = []
    duplicates = []
    
    for product in products:
        product_name = product['name']
        creator = product['creator']
        
        # Generate permalink
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
            duplicates.append(product_name)
            print(f"⏭️  Skipping: {creator}: {product_name} (already reviewed)")
        else:
            unreviewed.append(product)
            print(f"✅ New: {creator}: {product_name}")
    
    print(f"\n{'='*60}")
    print(f"📊 Filtering Results:")
    print(f"{'='*60}")
    print(f"Total products found: {len(products)}")
    print(f"Already reviewed: {len(duplicates)}")
    print(f"New products: {len(unreviewed)}")
    
    return unreviewed


if __name__ == "__main__":
    # Test the tracker
    print("Testing JSON tracker...")
    
    # Get existing reviews
    existing = get_existing_reviews()
    print(f"\nFound {len(existing)} existing reviews")
    
    # Display stats
    display_review_stats()