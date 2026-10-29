from typing import Optional
from uuid import UUID
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.user import StoreUser
from app.models.product import StoreProduct, Product, ProductVariant
from app.schemas.product import ProductOut, ProductListResponse, StoreProductUpdate


class ProductController:
    """Controller untuk katalog produk POS & pengaturan floor display."""

    @staticmethod
    def list_products(
        db: Session,
        current_user: StoreUser,
        q: Optional[str] = None,
        category: Optional[str] = None,
        floor_only: bool = False,
        page: int = 1,
        limit: int = 20,
    ) -> ProductListResponse:
        store_id = current_user.store_id

        # 1. Cek produk di store_products
        query_sp = db.query(StoreProduct).filter(
            StoreProduct.store_id == store_id,
            StoreProduct.is_active_for_pos == True,
        )

        if floor_only:
            query_sp = query_sp.filter(StoreProduct.is_floor_display == True)

        if category:
            query_sp = query_sp.filter(func.lower(StoreProduct.category_name) == category.strip().lower())

        if q:
            search = f"%{q.strip().lower()}%"
            query_sp = query_sp.filter(
                or_(
                    func.lower(StoreProduct.item_name).like(search),
                    func.lower(StoreProduct.sku).like(search),
                    func.lower(StoreProduct.brand_name).like(search),
                )
            )

        total_sp = query_sp.count()

        items = []
        if total_sp > 0:
            offset = (page - 1) * limit
            store_prods = query_sp.order_by(StoreProduct.display_order.asc(), StoreProduct.item_name.asc()).offset(offset).limit(limit).all()

            for sp in store_prods:
                custom_price = float(sp.custom_retail_price) if sp.custom_retail_price is not None else None
                suggested_price = float(sp.suggested_retail_price) if sp.suggested_retail_price is not None else None
                base_p = float(sp.base_price or 0)
                effective = custom_price if custom_price is not None and custom_price > 0 else (suggested_price or base_p)

                items.append(ProductOut(
                    id=sp.id,
                    product_id=None,
                    product_variant_id=None,
                    sku=sp.sku,
                    name=sp.item_name,
                    item_size=sp.item_size,
                    brand_name=sp.brand_name,
                    category_name=sp.category_name,
                    base_price=base_p,
                    suggested_retail_price=suggested_price,
                    custom_retail_price=custom_price,
                    effective_price=effective,
                    is_floor_display=sp.is_floor_display,
                    is_active_for_pos=sp.is_active_for_pos,
                ))

            return ProductListResponse(
                items=items,
                total=total_sp,
                page=page,
                limit=limit,
            )

        # 2. Fallback: Query ke master products & variants jika toko belum ada store_products
        query_master = db.query(ProductVariant).join(Product, Product.id == ProductVariant.product_id).filter(
            ProductVariant.deleted == False,
            ProductVariant.status == 1,
            Product.deleted == False,
        )

        if q:
            search = f"%{q.strip().lower()}%"
            query_master = query_master.filter(
                or_(
                    func.lower(ProductVariant.variant_name).like(search),
                    func.lower(ProductVariant.sku).like(search),
                    func.lower(Product.name).like(search),
                )
            )

        total_master = query_master.count()
        offset = (page - 1) * limit
        variants = query_master.order_by(ProductVariant.created_at.desc()).offset(offset).limit(limit).all()

        for v in variants:
            sell_p = float(v.sell_price or 0)
            base_p = float(v.base_price or 0)
            effective = sell_p if sell_p > 0 else base_p

            items.append(ProductOut(
                id=v.id,
                product_id=v.product_id,
                product_variant_id=v.id,
                sku=v.sku or "",
                name=f"{v.product.name} - {v.variant_name}" if v.product else v.variant_name,
                item_size=None,
                brand_name=None,
                category_name=None,
                base_price=base_p,
                suggested_retail_price=sell_p,
                custom_retail_price=None,
                effective_price=effective,
                is_floor_display=False,
                is_active_for_pos=True,
            ))

        return ProductListResponse(
            items=items,
            total=total_master,
            page=page,
            limit=limit,
        )

    @staticmethod
    def get_product(id: UUID, db: Session, current_user: StoreUser) -> ProductOut:
        sp = db.query(StoreProduct).filter(
            StoreProduct.id == id,
            StoreProduct.store_id == current_user.store_id,
        ).first()

        if sp:
            custom_price = float(sp.custom_retail_price) if sp.custom_retail_price is not None else None
            suggested_price = float(sp.suggested_retail_price) if sp.suggested_retail_price is not None else None
            base_p = float(sp.base_price or 0)
            effective = custom_price if custom_price is not None and custom_price > 0 else (suggested_price or base_p)

            return ProductOut(
                id=sp.id,
                product_id=None,
                product_variant_id=None,
                sku=sp.sku,
                name=sp.item_name,
                item_size=sp.item_size,
                brand_name=sp.brand_name,
                category_name=sp.category_name,
                base_price=base_p,
                suggested_retail_price=suggested_price,
                custom_retail_price=custom_price,
                effective_price=effective,
                is_floor_display=sp.is_floor_display,
                is_active_for_pos=sp.is_active_for_pos,
            )

        v = db.query(ProductVariant).filter(ProductVariant.id == id, ProductVariant.deleted == False).first()
        if v:
            sell_p = float(v.sell_price or 0)
            base_p = float(v.base_price or 0)
            return ProductOut(
                id=v.id,
                product_id=v.product_id,
                product_variant_id=v.id,
                sku=v.sku or "",
                name=f"{v.product.name} - {v.variant_name}" if v.product else v.variant_name,
                item_size=None,
                brand_name=None,
                category_name=None,
                base_price=base_p,
                suggested_retail_price=sell_p,
                custom_retail_price=None,
                effective_price=sell_p if sell_p > 0 else base_p,
                is_floor_display=False,
                is_active_for_pos=True,
            )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

    @staticmethod
    def update_display(
        id: UUID,
        payload: StoreProductUpdate,
        db: Session,
        current_user: StoreUser,
    ) -> dict:
        store_id = current_user.store_id

        sp = db.query(StoreProduct).filter(
            StoreProduct.id == id,
            StoreProduct.store_id == store_id,
        ).first()

        if not sp:
            v = db.query(ProductVariant).filter(ProductVariant.id == id, ProductVariant.deleted == False).first()
            if not v:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan.")

            sp = StoreProduct(
                id=UUID(str(v.id)) if db.query(StoreProduct).filter(StoreProduct.id == v.id).first() is None else uuid.uuid4(),
                store_id=store_id,
                sku=v.sku or f"SKU-{v.id}",
                item_name=f"{v.product.name} - {v.variant_name}" if v.product else v.variant_name,
                base_price=v.base_price or 0,
                suggested_retail_price=v.sell_price,
                custom_retail_price=payload.custom_retail_price,
                is_floor_display=payload.is_floor_display if payload.is_floor_display is not None else False,
                is_active_for_pos=payload.is_active_for_pos if payload.is_active_for_pos is not None else True,
            )
            db.add(sp)
        else:
            if payload.custom_retail_price is not None:
                sp.custom_retail_price = payload.custom_retail_price
            if payload.is_floor_display is not None:
                sp.is_floor_display = payload.is_floor_display
            if payload.is_active_for_pos is not None:
                sp.is_active_for_pos = payload.is_active_for_pos

        db.commit()
        db.refresh(sp)

        return {
            "success": True,
            "message": f"Pengaturan produk {sp.item_name} berhasil diperbarui.",
            "data": {
                "id": str(sp.id),
                "sku": sp.sku,
                "custom_retail_price": float(sp.custom_retail_price) if sp.custom_retail_price is not None else None,
                "is_floor_display": sp.is_floor_display,
                "is_active_for_pos": sp.is_active_for_pos,
            }
        }
