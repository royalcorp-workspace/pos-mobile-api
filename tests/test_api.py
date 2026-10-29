import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Royal POS Mobile API"
    assert data["status"] == "online"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "nonexistent_user", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_sales_user_rejected():
    """Sales Canvasser dilarang login ke API Mobile Toko."""
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "sales.canvasser@royal.co.id", "password": "password123"}
    )
    assert response.status_code == 403
    assert "Akses ditolak" in response.json()["detail"]


def test_login_store_an8_success():
    """Toko login via AN8 JDE berhasil mendapatkan JWT token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "105088", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["user_type"] == "store"
    assert data["store"]["address_number"] == 105088
    assert len(data["access_token"]) > 10


def test_store_profile_and_credit_ceiling():
    """Ambil data profil toko & limit plafon kredit."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"identifier": "105088", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Profile
    res_prof = client.get("/api/v1/store/profile", headers=headers)
    assert res_prof.status_code == 200
    prof = res_prof.json()
    assert prof["code"] == "11151"
    assert prof["address_number"] == 105088

    # 2. Credit Ceiling
    res_credit = client.get("/api/v1/store/credit-ceiling", headers=headers)
    assert res_credit.status_code == 200
    credit = res_credit.json()
    assert "available_credit" in credit
    assert credit["can_place_order"] is True


def test_get_products_catalog():
    """Ambil katalog produk POS untuk kasir toko."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"identifier": "105088", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/products?limit=5", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_create_order_cash_with_dt4_discount():
    """Order tunai di POS otomatis mendapatkan potongan DT4 cash discount 2.5%."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"identifier": "105088", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order_payload = {
        "payment_method": "CASH",
        "customer_name": "Testing Customer",
        "customer_phone": "08111222333",
        "notes": "Pytest Cash Order",
        "items": [
            {
                "product_id": "01a0e5b3-1b20-7039-852f-d445194dfb94",
                "name": "Item Test Kasir",
                "quantity": 2,
                "unit_price": 1000000.0,
            }
        ]
    }
    response = client.post("/api/v1/orders", json=order_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["subtotal"] == 2000000.0
    assert data["discount"] == 50000.0  # 2.5% dari 2jt
    assert data["total"] == 1950000.0
    assert data["payment_status"] == 1


def test_create_order_credit_limit_rejection():
    """Order tempo melebihi sisa plafon kredit wajib ditolak (HTTP 400)."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"identifier": "105088", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order_payload = {
        "payment_method": "CREDIT_LIMIT",
        "customer_name": "Testing Customer Tempo",
        "items": [
            {
                "product_id": "01a0e5b3-1b20-7039-852f-d445194dfb94",
                "name": "Item Melebihi Plafon",
                "quantity": 10,
                "unit_price": 5000000.0,
            }
        ]
    }
    response = client.post("/api/v1/orders", json=order_payload, headers=headers)
    assert response.status_code == 400
    assert "Plafon kredit tidak mencukupi" in response.json()["detail"]
