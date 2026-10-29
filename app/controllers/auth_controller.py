from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import StoreUser
from app.models.store import Store
from app.schemas.auth import LoginRequest, TokenResponse, StoreUserOut, StoreContextOut


class AuthController:
    """Controller untuk autentikasi mobile store user."""

    @staticmethod
    def login(request: LoginRequest, db: Session) -> TokenResponse:
        raw_input = request.identifier.strip()
        is_address_number = raw_input.isdigit()

        user: Optional[StoreUser] = None
        store: Optional[Store] = None

        if is_address_number:
            # 1. Cari Toko berdasarkan AN8 JDE
            an8 = int(raw_input)
            store = db.query(Store).filter(
                Store.address_number == an8,
                Store.deleted == False,
                Store.status == True,
            ).first()

            if store:
                if store.owner_user_id:
                    user = db.query(StoreUser).filter(
                        StoreUser.id == store.owner_user_id,
                        StoreUser.deleted == False,
                        StoreUser.is_active == True,
                    ).first()

                if not user:
                    user = db.query(StoreUser).filter(
                        StoreUser.store_id == store.id,
                        StoreUser.deleted == False,
                        StoreUser.is_active == True,
                    ).first()

        if not user:
            # 2. Cari User via Email, Username, atau Phone
            login_lower = raw_input.lower()
            user = db.query(StoreUser).filter(
                StoreUser.deleted == False,
                StoreUser.is_active == True,
                (func.lower(StoreUser.email) == login_lower)
                | (func.lower(StoreUser.username) == login_lower)
                | (StoreUser.phone == raw_input),
            ).first()

            if user and user.store_id and not store:
                store = db.query(Store).filter(
                    Store.id == user.store_id,
                    Store.deleted == False,
                    Store.status == True,
                ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kredensial salah atau akun toko tidak ditemukan.",
            )

        # Verifikasi Password Bcrypt
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kredensial atau password salah.",
            )

        # Validasi Akses: Khusus Toko / Kasir di Mobile
        is_store_account = (user.user_type == "store") or (user.role_persona in ["store_owner", "store_cashier", "store"])
        if not is_store_account:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses ditolak: Aplikasi Mobile POS khusus untuk pengguna Toko dan Kasir. Akun Manajemen/Sales silakan gunakan Web CMS.",
            )

        if not store and user.store_id:
            store = db.query(Store).filter(
                Store.id == user.store_id,
                Store.deleted == False,
                Store.status == True,
            ).first()

        if not store:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun toko ini belum terhubung dengan data profil toko yang aktif di sistem.",
            )

        # Buat JWT Access Token
        claims = {
            "user_id": str(user.id),
            "store_id": str(store.id),
            "user_type": user.user_type,
            "role_persona": user.role_persona or "store_owner",
            "an8": store.address_number,
        }
        access_token = create_access_token(
            subject=str(user.id),
            claims=claims,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        store_out = StoreContextOut(
            id=store.id,
            code=store.code,
            name=store.name,
            address_number=store.address_number,
            credit_limit=float(store.credit_limit or 0),
            outstanding_balance=float(store.outstanding_balance or 0),
            available_credit=store.available_credit,
            payment_term=int(store.payment_term or 0),
            tier_name=store.tier.name if store.tier else "Standard",
            phone=store.phone,
            address=store.address,
        )

        user_out = StoreUserOut(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            username=user.username,
            user_type=user.user_type,
            role_persona=user.role_persona,
            is_owner=user.is_owner,
            store_id=user.store_id,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=user_out,
            store=store_out,
        )

    @staticmethod
    def get_me(current_user: StoreUser) -> dict:
        store = current_user.store
        store_out = None
        if store:
            store_out = StoreContextOut(
                id=store.id,
                code=store.code,
                name=store.name,
                address_number=store.address_number,
                credit_limit=float(store.credit_limit or 0),
                outstanding_balance=float(store.outstanding_balance or 0),
                available_credit=store.available_credit,
                payment_term=int(store.payment_term or 0),
                tier_name=store.tier.name if store.tier else "Standard",
                phone=store.phone,
                address=store.address,
            )

        user_out = StoreUserOut(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            phone=current_user.phone,
            username=current_user.username,
            user_type=current_user.user_type,
            role_persona=current_user.role_persona,
            is_owner=current_user.is_owner,
            store_id=current_user.store_id,
        )

        return {
            "success": True,
            "data": {
                "user": user_out,
                "store": store_out,
            }
        }
