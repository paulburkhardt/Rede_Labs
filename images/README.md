# Image Description Generator

The `images/create_image_descriptions.py` script processes images from the `images/` folder and its subfolders, generates comprehensive AI descriptions using OpenAI's Vision API, and stores them both in the database and as text files alongside the images.

**Setup:**

1. Set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

2. Ensure the database is running and migrations are applied.

**Usage:**

```bash
cd images
# Normal mode - uses existing .txt files if present
uv run python create_image_descriptions.py

# Regenerate mode - recreates all descriptions even if .txt files exist
uv run python create_image_descriptions.py --regenerate
```

**Features:**
- Recursively processes all images in `images/` folder and subfolders
- Supports: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`
- **Smart description handling**:
  - **Normal mode**: Checks for existing `.txt` description files first
    - If found, uses existing description (no API call needed)
    - If not found, generates new description using GPT-4o-mini Vision (up to 1000 tokens)
  - **Regenerate mode** (`--regenerate` flag): Forces complete regeneration
    - **Clears all existing images from the database**
    - Overwrites existing `.txt` files with fresh AI-generated descriptions
    - Processes all images from scratch
    - Useful for updating descriptions with improved prompts or fixing issues
- Saves descriptions as `.txt` files alongside each image (e.g., `product.jpg` → `product.jpg.txt`)
- Stores base64-encoded images with descriptions in the `images` table
- **Automatically extracts product number** from folder name (e.g., images in `01/` folder get product_number "01")
- Skips already processed images (checks by base64 content in database)
- Provides progress tracking with emoji indicators and hash verification

**Description Quality:**
The enhanced prompt generates comprehensive descriptions covering:
- Product type, category, and purpose
- Visual appearance (colors, patterns, textures, finishes)
- Materials and construction details
- Dimensions and scale estimation
- All visible features and design elements
- Quality and condition assessment
- Design style and aesthetic
- Functionality and use cases
- Unique characteristics
- Context and presentation

**Output:**
- ✅ Successfully processed images
- 🔍 Image hash displayed for verification
- 📄 Found existing description file (reused in normal mode)
- 🔄 Regenerating description (in --regenerate mode)
- 💾 Description saved to text file (newly generated)
- ⏭️ Skipped (already in database)
- ❌ Errors during processing