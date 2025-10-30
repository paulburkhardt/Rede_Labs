# Marketplace API

A FastAPI-based marketplace backend with PostgreSQL database for managing sellers, products, and purchases.

## Project Structure

```
Rede_Labs/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── seller.py
│   │   ├── product.py
│   │   └── purchase.py
│   ├── schemas/             # Pydantic schemas for request/response
│   │   ├── __init__.py
│   │   ├── seller.py
│   │   ├── product.py
│   │   └── purchase.py
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── sellers.py
│       ├── products.py
│       ├── search.py
│       └── purchases.py
├── alembic/                 # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── pyproject.toml           # Project dependencies (uv)
├── docker-compose.yml       # PostgreSQL + Backend containers
├── Dockerfile               # Backend container definition
├── run.py                   # Development server runner
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.11+ and [uv](https://github.com/astral-sh/uv) for local development

## Setup Instructions

### Option 1: Docker (Recommended)

#### 1. Start All Services

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL** container:
  - User: `marketplace_user`
  - Password: `marketplace_pass`
  - Database: `marketplace_db`
  - Port: `5432`
- **Backend API** container:
  - FastAPI application
  - Port: `8000`
  - Auto-reloads on code changes

#### 2. Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### Option 2: Local Development

#### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Install Dependencies

```bash
uv sync
```

#### 3. Start PostgreSQL Only

```bash
docker-compose up -d postgres
```

#### 4. Configure Environment

Copy the example environment file and adjust if needed:

```bash
cp .env.example .env
```

#### 5. Run Database Migrations

```bash
uv run alembic upgrade head
```

#### 6. Start the Development Server

```bash
uv run python run.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Sellers

- **POST /createSeller** - Create a new seller
  ```json
  {
    "name": "string"
  }
  ```

### Products

- **POST /product/{id}** - Create a new product
- **PATCH /product/{id}** - Update an existing product
- **GET /product/{id}** - Get product details

### Search

- **GET /search?q={productName}** - Search for products

### Purchases

- **POST /buy/{productId}** - Simulate a product purchase

## Database Schema

### Sellers
- `id` (String, Primary Key)

### Products
- `id` (String, Primary Key)
- `name` (String)
- `short_description` (String)
- `long_description` (String)
- `price_in_cent` (Integer)
- `currency` (String, default: "USD")
- `bestseller` (Boolean)
- `image_url` (String)
- `image_alternative_text` (String)
- `seller_id` (Foreign Key → Sellers)

### Purchases
- `id` (String, Primary Key)
- `product_id` (Foreign Key → Products)
- `purchased_at` (DateTime)

## Development

### Running Tests

```bash
uv run pytest
```

### Database Management

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove data volumes
docker-compose down -v

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres
```

## Testing

The API includes comprehensive integration tests that clear and seed the database before each test.

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Specific Test File

```bash
uv run pytest tests/test_products.py -v
```

### Test Coverage

**48 integration tests** covering:
- ✅ Seller creation and authentication
- ✅ Buyer creation and authentication
- ✅ Product CRUD operations with authorization
- ✅ Search functionality (case-insensitive, partial matching, ranking)
- ✅ Purchase workflows with buyer authentication
- ✅ Security (token isolation, authorization checks)
- ✅ Data consistency across operations
- ✅ Edge cases and error handling

Each test:
1. Clears the database completely
2. Seeds fresh test data
3. Runs in isolation
4. Validates complete workflows

See `IMPLEMENTATION_COMPLETE.md` for detailed test documentation.

## Implementation Status

✅ **All endpoints fully implemented with authentication!**

- **POST /createSeller** - Creates seller with auth token
- **POST /createBuyer** - Creates buyer with auth token
- **POST /product/{id}** - Create product (requires org auth)
- **PATCH /product/{id}** - Update product (requires org auth, ownership check)
- **GET /product/{id}** - Get product details (public)
- **GET /search?q={query}** - Search products (public, ranked results)
- **POST /buy/{productId}** - Purchase product (requires buyer auth)

### Authentication

- Sellers receive an `auth_token` upon creation
- Buyers receive an `auth_token` upon creation
- Product create/update requires seller token in `Authorization` header
- Purchases require buyer token in `Authorization` header
- Sellers can only update their own products
- Tokens are securely generated using `secrets.token_urlsafe(32)`

## Utilities

### Image Description Generator

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

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Package Manager**: uv
- **Server**: Uvicorn
- **Testing**: pytest + httpx TestClient
- **AI**: OpenAI GPT-4o-mini (Vision API)

## Tmux Setup

### Enable logs

Add this to your `~/.tmux.conf`:

```conf
# Ensure the log directory exists
run-shell "mkdir -p ~/tmux-logs"

# Start logging for panes created by splitting
set-hook -g after-split-window  'run-shell "tmux pipe-pane -o -t #{pane_id} \"cat >> ~/tmux-logs/#{session_name}_#{window_index}_#{pane_index}.log\" "'

# Start logging for the initial pane of new windows
set-hook -g after-new-window    'run-shell "tmux pipe-pane -o -t #{pane_id} \"cat >> ~/tmux-logs/#{session_name}_#{window_index}_#{pane_index}.log\" "'

# Also cover panes that already exist when a client attaches (first session, restarts, etc.)
set-hook -g client-attached 'run-shell "for p in $(tmux list-panes -a -F \"#{pane_id}\"); do tmux pipe-pane -o -t \"$p\" \"cat >> ~/tmux-logs/#{session_name}_#{window_index}_#{pane_index}.log\"; done"'
```

Run `tmux source-file ~/.tmux.conf` to apply the changes.

The logs are stored in `~/tmux-logs`.

### Enable scrolling

Add this to your `~/.tmux.conf`:

```conf
set -g mouse on
```

Run `tmux source-file ~/.tmux.conf` to apply the changes.
