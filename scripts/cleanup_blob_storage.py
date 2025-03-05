'''

This script is used to cleanup orphaned images in blob storage.

It will find all images in blob storage that don't exist in the database and delete them.

*** DRY RUN ***

python scripts/cleanup_blob_storage.py 

*** ACTUALLY DELETES THE IMAGES ***

python scripts/cleanup_blob_storage.py --execute

'''



import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Property, PropertyMedia
from app.blob_storage import BlobStorageService
from urllib.parse import urlparse

def get_all_property_image_urls():
    """Get all image URLs from the database"""
    # Get main image URLs
    main_images = db.session.query(Property.main_image_url).filter(
        Property.main_image_url.isnot(None)
    ).all()
    
    # Get additional image URLs
    additional_images = db.session.query(PropertyMedia.image_url).filter(
        PropertyMedia.image_url.isnot(None)
    ).all()
    
    # Combine and flatten the lists
    all_urls = [url[0] for url in main_images + additional_images if url[0]]
    
    # Extract just the blob names from the URLs
    blob_names = set()
    for url in all_urls:
        try:
            # Parse the URL and get the path
            path = urlparse(url).path
            # The blob name is the last part of the path
            blob_name = path.split('/')[-1]
            blob_names.add(blob_name)
        except Exception as e:
            print(f"Error parsing URL {url}: {e}")
            continue
    
    return blob_names

def cleanup_orphaned_images(dry_run=True):
    """Delete blob storage images that don't exist in the database"""
    app = create_app('development')  # or whatever config you want to use
    
    with app.app_context():
        try:
            # Get all image URLs from database
            db_blob_names = get_all_property_image_urls()
            print(f"Found {len(db_blob_names)} images in database")
            
            # Get all blobs from storage
            blob_service = BlobStorageService()
            all_blobs = blob_service.list_all_blobs()
            print(f"Found {len(all_blobs)} images in blob storage")
            
            # Find orphaned blobs
            orphaned_blobs = [
                blob for blob in all_blobs 
                if blob not in db_blob_names
            ]
            
            print(f"Found {len(orphaned_blobs)} orphaned images")
            
            if dry_run:
                print("\nDRY RUN - No images will be deleted")
                print("\nOrphaned images that would be deleted:")
                for blob in orphaned_blobs:
                    print(f"- {blob}")
            else:
                print("\nDeleting orphaned images...")
                for blob in orphaned_blobs:
                    try:
                        blob_service.delete_image(blob)
                        print(f"Deleted {blob}")
                    except Exception as e:
                        print(f"Error deleting {blob}: {e}")
                
                print(f"\nSuccessfully cleaned up {len(orphaned_blobs)} orphaned images")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Clean up orphaned images in blob storage')
    parser.add_argument('--execute', action='store_true', 
                      help='Actually delete the orphaned images. Without this flag, will only do a dry run.')
    args = parser.parse_args()
    
    cleanup_orphaned_images(dry_run=not args.execute) 