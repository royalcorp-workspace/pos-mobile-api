from typing import Generator
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import StoreUser
from app.models.store import Store

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_store_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> StoreUser:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token autentikasi tidak valid atau sudah kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Klaim token tidak valid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Format UUID user pada token tidak valid.",
        )

    user = db.query(StoreUser).filter(
        StoreUser.id == user_uuid,
        StoreUser.deleted == False,
        StoreUser.is_active == True,
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pengguna tidak ditemukan atau akun sedang dinonaktifkan.",
        )

    # Validasi Hak Akses Eksklusif Mobile Toko:
    # Akun wajib bertipe 'store' (bukan admin web pusat / sales canvasser)
    is_store_user = (user.user_type == "store") or (user.role_persona in ["store_owner", "store_cashier", "store"])
    if not is_store_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak: Endpoint Mobile POS ini khusus untuk akun Toko/Kasir.",
        )

    if not user.store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun belum dikaitkan dengan Toko manapun.",
        )

    store = db.query(Store).filter(
        Store.id == user.store_id,
        Store.deleted == False,
        Store.status == True,
    ).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Toko yang terkait dengan akun ini sedang nonaktif atau tidak ditemukan.",
        )

    user.store = store
    return user
