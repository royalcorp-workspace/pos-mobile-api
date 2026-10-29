from app.models.user import StoreUser
from app.schemas.store import StoreProfileResponse, CreditCeilingResponse, StoreTierOut


class StoreController:
    """Controller untuk manajemen profil & limit kredit toko."""

    @staticmethod
    def get_profile(current_user: StoreUser) -> StoreProfileResponse:
        store = current_user.store

        tier_out = None
        if store.tier:
            tier_out = StoreTierOut(
                id=store.tier.id,
                code=store.tier.code,
                name=store.tier.name,
                level=store.tier.level,
            )

        return StoreProfileResponse(
            id=store.id,
            code=store.code,
            name=store.name,
            address_number=store.address_number,
            credit_limit=float(store.credit_limit or 0),
            outstanding_balance=float(store.outstanding_balance or 0),
            available_credit=store.available_credit,
            payment_term=int(store.payment_term or 0),
            address=store.address,
            phone=store.phone,
            email=store.email,
            status=store.status,
            tier=tier_out,
        )

    @staticmethod
    def get_credit_ceiling(current_user: StoreUser) -> CreditCeilingResponse:
        store = current_user.store
        available = store.available_credit
        can_place = (available > 0) or (int(store.payment_term or 0) == 0)

        return CreditCeilingResponse(
            store_id=store.id,
            store_name=store.name,
            address_number=store.address_number,
            credit_limit=float(store.credit_limit or 0),
            outstanding_balance=float(store.outstanding_balance or 0),
            available_credit=available,
            payment_term_days=int(store.payment_term or 0),
            can_place_order=can_place,
            max_order_amount_allowed=available,
        )
