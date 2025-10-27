# Marketplace API

A FastAPI-based marketplace backend with PostgreSQL database for managing organizations, products, and purchases.

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
│   │   ├── organization.py
│   │   ├── product.py
│   │   └── purchase.py
│   ├── schemas/             # Pydantic schemas for request/response
│   │   ├── __init__.py
│   │   ├── organization.py
│   │   ├── product.py
│   │   └── purchase.py
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── organizations.py
│       ├── products.py
│       ├── search.py
│       └── purchases.py
├── alembic/                 # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── pyproject.toml           # Project dependencies (uv)
├── docker-compose.yml       # PostgreSQL container
├── run.py                   # Development server runner
└── README.md
```

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose (for PostgreSQL)

## Setup Instructions

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
cd Rede_Labs
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Start PostgreSQL Database

```bash
docker-compose up -d
```

This will start a PostgreSQL container with:
- **User**: `marketplace_user`
- **Password**: `marketplace_pass`
- **Database**: `marketplace_db`
- **Port**: `5432`

### 5. Configure Environment

Copy the example environment file and adjust if needed:

```bash
cp .env.example .env
```

### 6. Run Database Migrations

```bash
# Create initial migration
uv run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
uv run alembic upgrade head
```

### 7. Start the Development Server

```bash
uv run python run.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Organizations

- **POST /createOrganization** - Create a new organization
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

### Organizations
- `id` (String, Primary Key)
- `name` (String)

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
- `organization_id` (Foreign Key → Organizations)

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

### Stop Database

```bash
docker-compose down
```

To remove data volumes:
```bash
docker-compose down -v
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
- ✅ Organization creation and authentication
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

- **POST /createOrganization** - Creates organization with auth token
- **POST /createBuyer** - Creates buyer with auth token
- **POST /product/{id}** - Create product (requires org auth)
- **PATCH /product/{id}** - Update product (requires org auth, ownership check)
- **GET /product/{id}** - Get product details (public)
- **GET /search?q={query}** - Search products (public, ranked results)
- **POST /buy/{productId}** - Purchase product (requires buyer auth)

### Authentication

- Organizations receive an `auth_token` upon creation
- Buyers receive an `auth_token` upon creation
- Product create/update requires organization token in `Authorization` header
- Purchases require buyer token in `Authorization` header
- Organizations can only update their own products
- Tokens are securely generated using `secrets.token_urlsafe(32)`

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Package Manager**: uv
- **Server**: Uvicorn
- **Testing**: pytest + httpx TestClient
