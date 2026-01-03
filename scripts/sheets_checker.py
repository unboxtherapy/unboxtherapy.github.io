"""Check Google Sheets for existing reviews to avoid duplicates"""
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_SPREADSHEET_ID, SHEETS_RANGE


def get_existing_reviews():
    """
    Fetch all existing reviews from Google Sheets
    
    Returns:
        set: Set of product permalinks/titles that have been reviewed
    """
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        print("⚠️  GOOGLE_SERVICE_ACCOUNT_JSON not found - cannot check for duplicates")
        return set()
    
    if not GOOGLE_SPREADSHEET_ID:
        print("⚠️  GOOGLE_SPREADSHEET_ID not found - cannot check for duplicates")
        return set()
    
    try:
        print(f"\n{'='*60}")
        print("📊 Checking Google Sheets for Existing Reviews")
        print(f"{'='*60}")
        
        # Parse credentials
        credentials_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        
        # Create credentials
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        # Build Sheets service
        service = build('sheets', 'v4', credentials=credentials)
        
        # Read all data from sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SPREADSHEET_ID,
            range=SHEETS_RANGE
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("✅ No existing reviews found - starting fresh")
            return set()
        
        # Extract permalinks and titles (assuming columns: Timestamp, Title, Focus_KW, Permalink, URL, ...)
        existing_reviews = set()
        
        # Skip header row
        for row in values[1:]:
            if len(row) >= 4:  # Ensure row has at least 4 columns
                title = row[1].strip().lower() if len(row) > 1 else ""
                permalink = row[3].strip().lower() if len(row) > 3 else ""
                
                if title:
                    existing_reviews.add(title)
                if permalink:
                    existing_reviews.add(permalink)
        
        print(f"✅ Found {len(existing_reviews)} existing reviews in Google Sheets")
        
        # Show some examples
        if existing_reviews:
            examples = list(existing_reviews)[:3]
            print(f"\n📝 Example entries:")
            for ex in examples:
                print(f"   - {ex[:60]}...")
        
        return existing_reviews
        
    except Exception as e:
        print(f"❌ Error reading Google Sheets: {e}")
        print("⚠️  Continuing without duplicate check...")
        return set()


def is_product_reviewed(product_name, permalink, existing_reviews):
    """
    Check if a product has already been reviewed
    
    Args:
        product_name: Product name
        permalink: Product permalink
        existing_reviews: Set of existing review identifiers
    
    Returns:
        bool: True if already reviewed
    """
    # Normalize for comparison
    normalized_name = product_name.strip().lower()
    normalized_permalink = permalink.strip().lower()
    
    # Check if either the name or permalink exists
    is_duplicate = (
        normalized_name in existing_reviews or
        normalized_permalink in existing_reviews or
        any(normalized_name in existing for existing in existing_reviews) or
        any(normalized_permalink in existing for existing in existing_reviews)
    )
    
    return is_duplicate


def filter_unreviewed_products(products, existing_reviews):
    """
    Filter out products that have already been reviewed
    
    Args:
        products: List of product dicts from muncheye_scraper
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
    
    unreviewed = []
    duplicates = []
    
    for product in products:
        from slugify import slugify
        
        product_name = product['name']
        creator = product['creator']
        
        # Generate permalink same way as main script
        permalink = slugify(f"{creator}-{product_name}-review")[:100]
        
        # Check if reviewed
        if is_product_reviewed(product_name, permalink, existing_reviews):
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
    
    if duplicates:
        print(f"\n🔄 Duplicates skipped:")
        for dup in duplicates[:5]:
            print(f"   - {dup}")
        if len(duplicates) > 5:
            print(f"   ... and {len(duplicates) - 5} more")
    
    return unreviewed


def get_review_stats():
    """
    Get statistics about existing reviews
    
    Returns:
        dict: Statistics about reviews in sheets
    """
    if not GOOGLE_SERVICE_ACCOUNT_JSON or not GOOGLE_SPREADSHEET_ID:
        return None
    
    try:
        credentials_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SPREADSHEET_ID,
            range=SHEETS_RANGE
        ).execute()
        
        values = result.get('values', [])
        
        if len(values) <= 1:  # Only header or empty
            return {
                'total_reviews': 0,
                'last_review_date': None,
                'platforms': {}
            }
        
        # Analyze data
        total = len(values) - 1  # Exclude header
        
        stats = {
            'total_reviews': total,
            'last_review_date': values[-1][0] if len(values[-1]) > 0 else None,
            'recent_reviews': []
        }
        
        # Get last 5 reviews
        for row in values[-5:]:
            if len(row) >= 2:
                stats['recent_reviews'].append(row[1])
        
        return stats
        
    except Exception as e:
        print(f"⚠️  Error getting stats: {e}")
        return None


def display_review_stats():
    """Display statistics about existing reviews"""
    stats = get_review_stats()
    
    if not stats:
        print("\n⚠️  Could not retrieve review statistics")
        return
    
    print(f"\n{'='*60}")
    print("📊 Review Statistics")
    print(f"{'='*60}")
    print(f"Total reviews published: {stats['total_reviews']}")
    
    if stats['last_review_date']:
        print(f"Last review published: {stats['last_review_date']}")
    
    if stats['recent_reviews']:
        print(f"\n📝 Recent reviews:")
        for review in stats['recent_reviews']:
            print(f"   - {review[:60]}...")


if __name__ == "__main__":
    # Test the checker
    print("Testing Google Sheets checker...")
    
    # Get existing reviews
    existing = get_existing_reviews()
    print(f"\nFound {len(existing)} existing reviews")
    
    # Display stats
    display_review_stats()