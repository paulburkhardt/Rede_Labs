#!/usr/bin/env python3
"""
Script to process images from the images folder, generate descriptions using OpenAI API,
and store them with base64 encoded data in the database.
"""
import os
import sys
import base64
import hashlib
import argparse
from pathlib import Path
from openai import OpenAI
from sqlalchemy.orm import Session

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or "dummy"

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine, Base
from app.models.image import Image

# Supported image extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def generate_image_description(client: OpenAI, base64_image: str, image_path: str) -> str:
    """Generate a detailed description for an image using OpenAI Vision API."""
    try:
        # Determine the image format from the file extension
        ext = Path(image_path).suffix.lower()
        mime_type = f"image/{ext[1:]}" if ext != '.jpg' else "image/jpeg"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Describe this product image in extreme detail, as if explaining it to someone who cannot see it. Focus on:

- Product type and category
- All visible colors, patterns, textures, and finishes
- Materials and construction details
- Size, proportions, and scale
- Every visible feature, component, and design element
- Quality indicators and condition
- Design style and aesthetic
- Intended functionality and use
- Unique or distinctive characteristics
- Background, lighting, and presentation

Provide ONLY the pure description. Do not include any preamble, introduction, or phrases like "Here's a description" or "This image shows". Start directly with the description itself. Be extremely thorough and specific."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating description for {image_path}: {e}")
        return None


def load_description_from_file(image_path: Path) -> str:
    """Load description from text file if it exists."""
    desc_path = image_path.with_suffix(image_path.suffix + '.txt')
    
    if desc_path.exists():
        with open(desc_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    return None


def save_description_to_file(image_path: Path, description: str):
    """Save description as a text file alongside the image."""
    # Create description filename (same name as image but with .txt extension)
    desc_path = image_path.with_suffix(image_path.suffix + '.txt')
    
    with open(desc_path, 'w', encoding='utf-8') as f:
        f.write(description)
    
    return desc_path


def process_images(images_dir: str, db: Session, client: OpenAI, regenerate: bool = False):
    """Process all images in the directory and subdirectories.
    
    Args:
        images_dir: Directory containing images
        db: Database session
        client: OpenAI client
        regenerate: If True, regenerate descriptions even if .txt files exist
    """
    images_path = Path(images_dir)
    
    if not images_path.exists():
        print(f"Images directory not found: {images_dir}")
        return
    
    # Find all image files recursively
    image_files = []
    for ext in SUPPORTED_EXTENSIONS:
        image_files.extend(images_path.rglob(f"*{ext}"))
    
    print(f"Found {len(image_files)} images to process")
    
    processed = 0
    skipped = 0
    errors = 0
    
    for image_file in image_files:
        try:
            # Check if image already exists in database
            relative_path = str(image_file.relative_to(images_path))
            
            # Extract product number from folder name (e.g., "01", "02", "03")
            product_number = image_file.parent.name
            
            # Encode image to base64
            print(f"Processing: {relative_path} (Product: {product_number})")
            base64_data = encode_image_to_base64(str(image_file))
            
            # Debug: Show hash of image data to verify uniqueness
            image_hash = hashlib.md5(base64_data.encode()).hexdigest()[:8]
            print(f"  🔍 Image hash: {image_hash}")
            
            # Check if this image already exists (by base64 content) - only in normal mode
            if not regenerate:
                existing_image = db.query(Image).filter(Image.base64 == base64_data).first()
                if existing_image:
                    print(f"  ⏭️  Already exists in database (ID: {existing_image.id}), skipping")
                    skipped += 1
                    continue
            
            # Check if description file already exists
            existing_description = load_description_from_file(image_file)
            
            if existing_description and not regenerate:
                print(f"  📄 Found existing description file, using it")
                description = existing_description
            else:
                if existing_description and regenerate:
                    print(f"  🔄 Regenerating description (--regenerate mode)")
                else:
                    print(f"  🤖 Generating detailed description...")
                
                # Generate description using OpenAI
                description = generate_image_description(client, base64_data, str(image_file))
                
                if description is None:
                    print(f"  ❌ Failed to generate description")
                    errors += 1
                    continue
                
                # Save description to text file
                desc_file = save_description_to_file(image_file, description)
                print(f"  💾 Saved description to: {desc_file.name}")
            
            # Create new image record
            new_image = Image(
                base64=base64_data,
                image_description=description,
                product_number=product_number
            )
            
            db.add(new_image)
            db.commit()
            db.refresh(new_image)  # Refresh to ensure it's properly saved
            
            print(f"  ✅ Saved to database (ID: {new_image.id})")
            print(f"  📝 Description preview: {description[:150]}...")
            processed += 1
            
        except Exception as e:
            print(f"  ❌ Error processing {image_file}: {e}")
            db.rollback()
            errors += 1
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"  ✅ Processed: {processed}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Errors: {errors}")
    print(f"{'='*60}")


def main():
    """Main function to run the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate descriptions for product images using OpenAI Vision API'
    )
    parser.add_argument(
        '--regenerate',
        action='store_true',
        help='Regenerate descriptions even if .txt files already exist'
    )
    args = parser.parse_args()
    
    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        return
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    if args.regenerate:
        print("🔄 Running in REGENERATE mode - will recreate all descriptions")
        print("🗑️  Clearing existing images from database...")
        
        # Clear all existing images from database
        try:
            deleted_count = db.query(Image).delete()
            db.commit()
            print(f"   Deleted {deleted_count} existing image records\n")
        except Exception as e:
            print(f"   Error clearing database: {e}")
            db.rollback()
            return
    
    try:
        # Process images from the current directory (script is in images folder)
        images_dir = os.path.dirname(__file__)
        process_images(images_dir, db, client, regenerate=args.regenerate)
    finally:
        db.close()


if __name__ == "__main__":
    main()
