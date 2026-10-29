from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import api_v1_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## Royal Corporation - Mobile POS API (MVP)
    
    API backend eksklusif untuk operasional **Toko Mebel & Kasir di Aplikasi Mobile**:
    - **Multi-Identifier Auth**: Login dengan AN8 JDE, Email, Username, atau WhatsApp.
    - **Plafon Kredit (Credit Ceiling)**: Pengecekan limit kredit tempo & saldo piutang toko.
    - **Katalog Produk Kasir POS**: Akses produk, varian, harga jual retail kustom, dan status floor display.
    - **Transaksi Kasir POS**: Pembuatan order kasir, kalkulasi diskon tunai (DT4 2.5%), dan validasi plafon kredit.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }
