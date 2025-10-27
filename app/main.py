from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import sellers, products, search, purchases, buyers
from app.config import settings

app = FastAPI(
    title="Marketplace API",
    description="API for managing marketplace sellers, products, and purchases",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sellers.router)
app.include_router(buyers.router)
app.include_router(products.router)
app.include_router(search.router)
app.include_router(purchases.router)


@app.get("/")
def root():
    return {
        "message": "Marketplace API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
