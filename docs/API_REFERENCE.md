# MarketArena API Reference

## Base URL
```
http://localhost:8100
```

## Endpoints

### Health Check
```http
GET /
```
Returns API status and current marketplace phase.

### Organization Management

#### Create Organization
```http
POST /createOrganization
Content-Type: application/json

{
  "name": "My Company"
}
```

**Response:**
```json
{
  "id": "org-abc123",
  "name": "My Company"
}
```

### Product Management

#### Create Product
```http
POST /product
Content-Type: application/json

{
  "name": "Premium Towel",
  "shortDescription": "Soft and absorbent",
  "longDescription": "High-quality cotton towel...",
  "price": 2999,
  "image": {
    "url": "https://example.com/image.jpg",
    "alternativeText": "Towel image"
  }
}
```

#### Update Product
```http
PATCH /product/{product_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "price": 2499
}
```
**Note:** Only works during EDIT phase.

#### Search Products
```http
GET /search?q=towel
```

**Response:**
```json
[
  {
    "id": "product-xyz",
    "name": "Premium Towel",
    "company": {
      "id": "org-abc",
      "name": "My Company"
    },
    "priceInCent": 2999,
    "currency": "USD",
    "bestseller": true,
    "shortDescription": "Soft and absorbent",
    "image": {
      "url": "https://example.com/image.jpg"
    }
  }
]
```

#### Get Product Details
```http
GET /product/{product_id}
```

#### Purchase Product
```http
POST /buy/{product_id}
```
**Note:** Only works during BUY phase.

### Admin Endpoints (Green Agent Only)

#### Reset Marketplace
```http
POST /admin/reset
```

#### Start Edit Phase
```http
POST /admin/start_edit_phase
```

#### Start Buy Phase
```http
POST /admin/start_buy_phase
```

#### Get Statistics
```http
GET /admin/stats
```

**Response:**
```json
{
  "sellers": [
    {
      "org_id": "org-abc",
      "name": "My Company",
      "total_revenue": 5998,
      "units_sold": 2,
      "avg_price": 2999
    }
  ],
  "marketplace_totals": {
    "total_revenue": 5998,
    "total_units_sold": 2,
    "num_sellers": 1
  },
  "current_day": 1,
  "current_phase": "buy"
}
```

## Phase System

The marketplace operates in three phases:

1. **IDLE** - Initial state, no actions allowed
2. **EDIT** - Sellers can create/update products
3. **BUY** - Customers can purchase products

Only the green agent can control phase transitions via admin endpoints.
