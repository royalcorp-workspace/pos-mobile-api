from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_store_user
from app.controllers.order_controller import OrderController
from app.models.user import StoreUser
from app.schemas.order import OrderCreateRequest, OrderOut, OrderListResponse

router = APIRouter()


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED, summary="Buat Transaksi Kasir POS")
def create_order(
    payload: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: StoreUser = Depends(get_current_store_user),
):
    """Membuat transaksi kasir POS via OrderController."""
    return OrderController.create_order(payload=payload, db=db, current_user=current_user)


@router.get("", response_model=OrderListResponse, summary="Riwayat Pesanan Toko")
def list_orders(
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(20, ge=1, le=100, description="Jumlah item per halaman"),
    db: Session = Depends(get_db),
    current_user: StoreUser = Depends(get_current_store_user),
):
    """Mengambil riwayat transaksi pesanan via OrderController."""
    return OrderController.list_orders(page=page, limit=limit, db=db, current_user=current_user)


@router.get("/{order_number}", response_model=OrderOut, summary="Detail Pesanan Toko")
def get_order_detail(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: StoreUser = Depends(get_current_store_user),
):
    """Mengambil detail satu pesanan via OrderController."""
    return OrderController.get_order_detail(order_number=order_number, db=db, current_user=current_user)
