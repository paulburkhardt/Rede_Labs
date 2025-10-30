from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging import access_log_with_optional_body
from app.routers import (admin, buyers, images, products, purchases, search,
                         sellers)

app = FastAPI(
    title="Marketplace API",
    description="API for managing marketplace sellers, products, and purchases",
    version="0.1.0",
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
app.include_router(images.router)
app.include_router(admin.router)

@app.middleware("http")
async def log_request_body(request: Request, call_next):
    return await access_log_with_optional_body(request, call_next)


@app.get("/")
def root():
    return {"message": "Marketplace API", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
