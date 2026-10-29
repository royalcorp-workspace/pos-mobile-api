from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_store_user
from app.controllers.product_controller import ProductController
from app.models.user import StoreUser
from app.schemas.product import ProductOut, ProductListResponse, StoreProductUpdate

router = APIRouter()


@router.get("", response_model=ProductListResponse, summary="Katalog Produk POS Toko")
def list_products(
    q: Optional[str] = Query(None, description="Cari nama produk atau SKU"),
    category: Optional[str] = Query(None, description="Filter nama kategori"),
    floor_only: Optional[bool] = Query(False, description="Hanya tampilkan produk floor display"),
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah item per halaman"),
    db: Session = Depends(get_db),
    current_user: StoreUser = Depends(get_current_store_user),
):
    """Mengambil katalog produk kasir toko via ProductController."""
    return ProductController.list_products(
        db=db,
        current_user=current_user,
        q=q,
        category=category,
        floor_only=floor_only,
        page=page,
        limit=limit,
    )


@router.get("/{id}", response_model=ProductOut, summary="Detail Produk POS")
def get_product(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: StoreUser = Depends(get_current_store_user),
):
    """Mengambil detail satu produk via ProductController."""
    return ProductController.get_product(id=id, db=db, current_user=current_user)


@router.patch("/{id}/display", summary="Update Floor Display & Harga Retail Kustom")
def update_product_display(
    id: UUID,
    payload: StoreProductUpdate,
    db: Session = Depends(get_db),
    current_user: StoreUser = Depends(get_current_store_user),
):
    """Memperbarui status display & custom price via ProductController."""
    return ProductController.update_display(
        id=id,
        payload=payload,
        db=db,
        current_user=current_user,
    )
