from fastapi import APIRouter, Depends
from app.api.deps import get_current_store_user
from app.controllers.store_controller import StoreController
from app.models.user import StoreUser
from app.schemas.store import StoreProfileResponse, CreditCeilingResponse

router = APIRouter()


@router.get("/profile", response_model=StoreProfileResponse, summary="Profil Lengkap Toko & Plafon Kredit")
def get_store_profile(current_user: StoreUser = Depends(get_current_store_user)):
    """Mengambil data profil toko via StoreController."""
    return StoreController.get_profile(current_user)


@router.get("/credit-ceiling", response_model=CreditCeilingResponse, summary="Informasi Plafon Kredit & Status Pemesanan Tempo")
def get_credit_ceiling(current_user: StoreUser = Depends(get_current_store_user)):
    """Cek sisa plafon kredit toko via StoreController."""
    return StoreController.get_credit_ceiling(current_user)
