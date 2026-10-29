from datetime import datetime
import random
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import StoreUser
from app.models.order import Order, OrderItem
from app.models.customer import Customer
from app.schemas.order import OrderCreateRequest, OrderOut, OrderItemOut, OrderListResponse


class OrderController:
    """Controller untuk pembuatan dan pengelolaan transaksi kasir POS."""

    @staticmethod
    def generate_order_number() -> str:
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        rand_suffix = f"{random.randint(1000, 9999)}"
        return f"ORD-POS-{date_str}-{rand_suffix}"

    @classmethod
    def create_order(cls, payload: OrderCreateRequest, db: Session, current_user: StoreUser) -> OrderOut:
        store = current_user.store
        payment_method = payload.payment_method.strip().upper()

        if payment_method not in ["CASH", "TRANSFER", "CREDIT_LIMIT"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Metode pembayaran harus berupa 'CASH', 'TRANSFER', atau 'CREDIT_LIMIT'.",
            )

        # 1. Hitung Subtotal Item
        subtotal = 0.0
        order_items_data = []

        for item in payload.items:
            item_total = float(item.quantity) * float(item.unit_price)
            subtotal += item_total
            order_items_data.append({
                "id": uuid.uuid4(),
                "product_id": item.product_id,
                "product_variant_id": item.product_variant_id,
                "name": item.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "discount_nominal": 0.0,
                "discount_percent": 0.0,
                "total": item_total,
                "item_notes": item.item_notes,
            })

        # 2. Kalkulasi Diskon & Total
        discount = 0.0
        if payment_method == "CASH":
            discount = round(subtotal * 0.025, 2)  # DT4 2.5% discount

        tax = 0.0
        total = max(0.0, subtotal - discount + tax)

        # 3. Validasi Limit Kredit
        if payment_method == "CREDIT_LIMIT":
            available_credit = store.available_credit
            if total > available_credit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plafon kredit tidak mencukupi! Total pesanan Rp {total:,.2f} melebihi sisa plafon kredit Rp {available_credit:,.2f}.",
                )

        # 4. Resolve / Create Customer
        customer = None
        if payload.customer_phone:
            customer = db.query(Customer).filter(
                Customer.phone == payload.customer_phone,
                Customer.deleted == False,
            ).first()

        if not customer:
            customer = Customer(
                id=uuid.uuid4(),
                name=payload.customer_name or f"Pelanggan {store.name}",
                email=payload.customer_email,
                phone=payload.customer_phone,
                customer_type=1,
                creator=current_user.name,
            )
            db.add(customer)
            db.flush()

        # 5. Buat Order & Items secara Atomik
        order_id = uuid.uuid4()
        order_num = cls.generate_order_number()

        while db.query(Order).filter(Order.order_number == order_num).first():
            order_num = cls.generate_order_number()

        pay_status = 1 if payment_method in ["CASH", "TRANSFER"] else 0

        order = Order(
            id=order_id,
            order_number=order_num,
            customer_id=customer.id,
            store_id=store.id,
            status=1,
            payment_method=payment_method,
            payment_status=pay_status,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total,
            notes=payload.notes,
            creator=current_user.name,
            address_number=store.address_number,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(order)

        for item_data in order_items_data:
            order_item = OrderItem(
                id=item_data["id"],
                order_id=order_id,
                product_id=item_data["product_id"],
                product_variant_id=item_data["product_variant_id"],
                name=item_data["name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                discount_nominal=item_data["discount_nominal"],
                discount_percent=item_data["discount_percent"],
                total=item_data["total"],
                item_notes=item_data["item_notes"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.add(order_item)

        if payment_method == "CREDIT_LIMIT":
            store.outstanding_balance = float(store.outstanding_balance or 0) + total

        db.commit()
        db.refresh(order)

        items_out = [
            OrderItemOut(
                id=item.id,
                product_id=item.product_id,
                product_variant_id=item.product_variant_id,
                name=item.name,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                discount_nominal=float(item.discount_nominal),
                discount_percent=float(item.discount_percent),
                total=float(item.total),
                item_notes=item.item_notes,
            )
            for item in order.items
        ]

        return OrderOut(
            id=order.id,
            order_number=order.order_number,
            store_id=order.store_id,
            customer_name=customer.name,
            customer_phone=customer.phone,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            status=order.status,
            subtotal=float(order.subtotal),
            discount=float(order.discount),
            tax=float(order.tax),
            total=float(order.total),
            notes=order.notes,
            created_at=order.created_at,
            items=items_out,
        )

    @staticmethod
    def list_orders(page: int, limit: int, db: Session, current_user: StoreUser) -> OrderListResponse:
        store_id = current_user.store_id

        query = db.query(Order).filter(
            Order.store_id == store_id,
            Order.deleted == False,
        )

        total = query.count()
        offset = (page - 1) * limit
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()

        items_out = []
        for o in orders:
            items_out.append(OrderOut(
                id=o.id,
                order_number=o.order_number,
                store_id=o.store_id,
                customer_name=None,
                customer_phone=None,
                payment_method=o.payment_method,
                payment_status=o.payment_status,
                status=o.status,
                subtotal=float(o.subtotal or 0),
                discount=float(o.discount or 0),
                tax=float(o.tax or 0),
                total=float(o.total or 0),
                notes=o.notes,
                created_at=o.created_at,
                items=[
                    OrderItemOut(
                        id=it.id,
                        product_id=it.product_id,
                        product_variant_id=it.product_variant_id,
                        name=it.name,
                        quantity=it.quantity,
                        unit_price=float(it.unit_price),
                        discount_nominal=float(it.discount_nominal),
                        discount_percent=float(it.discount_percent),
                        total=float(it.total),
                        item_notes=it.item_notes,
                    )
                    for it in o.items
                ]
            ))

        return OrderListResponse(
            items=items_out,
            total=total,
            page=page,
            limit=limit,
        )

    @staticmethod
    def get_order_detail(order_number: str, db: Session, current_user: StoreUser) -> OrderOut:
        store_id = current_user.store_id

        order = db.query(Order).filter(
            Order.order_number == order_number,
            Order.store_id == store_id,
            Order.deleted == False,
        ).first()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pesanan tidak ditemukan atau bukan milik toko Anda.",
            )

        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()

        items_out = [
            OrderItemOut(
                id=it.id,
                product_id=it.product_id,
                product_variant_id=it.product_variant_id,
                name=it.name,
                quantity=it.quantity,
                unit_price=float(it.unit_price),
                discount_nominal=float(it.discount_nominal),
                discount_percent=float(it.discount_percent),
                total=float(it.total),
                item_notes=it.item_notes,
            )
            for it in order.items
        ]

        return OrderOut(
            id=order.id,
            order_number=order.order_number,
            store_id=order.store_id,
            customer_name=customer.name if customer else None,
            customer_phone=customer.phone if customer else None,
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            status=order.status,
            subtotal=float(order.subtotal or 0),
            discount=float(order.discount or 0),
            tax=float(order.tax or 0),
            total=float(order.total or 0),
            notes=order.notes,
            created_at=order.created_at,
            items=items_out,
        )
