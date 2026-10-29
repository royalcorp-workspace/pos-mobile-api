from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_store_user
from app.controllers.auth_controller import AuthController
from app.models.user import StoreUser
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="Login Mobile Store / Kasir")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentikasi Pengguna Toko / Kasir di Aplikasi Mobile POS.
    Mendelegasikan proses autentikasi ke AuthController.
    """
    return AuthController.login(request, db)


@router.get("/me", summary="Ambil Profil Pengguna Toko yang Sedang Login")
def get_me(current_user: StoreUser = Depends(get_current_store_user)):
    """Mengembalikan data personil toko yang sedang aktif."""
    return AuthController.get_me(current_user)
