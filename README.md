# Royal POS Mobile API (MVP)

Backend RESTful API berbasis **Python FastAPI** yang dirancang khusus untuk operasional **Toko Mebel & Kasir pada Aplikasi Mobile POS** di ekosistem Royal Corporation.

---

## 1. Latar Belakang & Pembatasan Akses

Sesuai dengan arsitektur hak akses terpadu:
- **Akun Toko & Kasir (di bawah Sales Canvasser)**:
  - **Dilarang login ke Web CMS** (`cms-img-store`).
  - **Akses eksklusif hanya melalui Aplikasi Mobile POS** menggunakan API ini.
- **Sales Canvasser & Super Admin**:
  - Mengakses Web CMS (`cms-img-store`) untuk monitoring, persetujuan limit kredit, dan canvassing toko.

---

## 2. Fitur MVP Mobile POS API

1. **Autentikasi Multi-Identifier (`POST /api/v1/auth/login`)**:
   - Mendukung login dengan:
     - Nomor Pelanggan JDE Toko (AN8), misal `105088`.
     - Email toko, misal `toko.jde105088@royal.co.id`.
     - Username toko, misal `toko_105088`.
     - Nomor HP / WhatsApp.
   - Proteksi otorisasi: Menolak akun non-toko (Superadmin/Sales) dari login ke Mobile API.
   - Mengembalikan **JWT Bearer Token** dan konteks toko (`StoreContext`).

2. **Konteks Plafon Kredit Toko (`GET /api/v1/store/profile` & `GET /api/v1/store/credit-ceiling`)**:
   - Menampilkan plafon kredit (`credit_limit`), saldo piutang (`outstanding_balance`), sisa plafon kredit (`available_credit`), dan payment term.
   - Status kelayakan toko untuk melakukan pemesanan dengan tempo pembayaran (TOP).

3. **Katalog Produk Kasir POS (`GET /api/v1/products`)**:
   - Menampilkan produk & varian aktif untuk kasir toko.
   - Mengambil harga kustom (`custom_retail_price`) atau suggested retail price.
   - Filter floor display (`floor_only=true`) dan pencarian SKU/Nama.
   - Update status display kasur toko (`PATCH /api/v1/products/{id}/display`).

4. **Transaksi Kasir POS (`POST /api/v1/orders`)**:
   - Pilihan metode pembayaran: `CASH`, `TRANSFER`, atau `CREDIT_LIMIT`.
   - **DT4 Cash Discount**: Otomatis memberikan diskon tunai 2.5% jika pembayaran menggunakan metode `CASH`.
   - **Validasi Plafon Kredit**: Menolak pesanan tempo jika total order melebihi sisa kredit (`available_credit`).
   - Tersimpan secara transaksional atomik ke schema `sales.orders` dan `sales.order_items`.

---

## 3. Menjalankan Service

### Menggunakan Docker Compose (Direkomendasikan)
```bash
cd pos-mobile-api
docker compose up -d --build
```
API akan berjalan di `http://localhost:8003`.
Dokumentasi interaktif Swagger UI tersedia di `http://localhost:8003/docs`.

### Menggunakan Virtualenv Lokal
```bash
cd pos-mobile-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 4. Contoh Penggunaan cURL

### A. Login Toko via AN8 JDE
```bash
curl -X POST "http://localhost:8003/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "105088",
    "password": "password123"
  }'
```

### B. Ambil Profil & Plafon Kredit
```bash
curl -X GET "http://localhost:8003/api/v1/store/profile" \
  -H "Authorization: Bearer <TOKEN>"
```

### C. Ambil Katalog Produk POS
```bash
curl -X GET "http://localhost:8003/api/v1/products?limit=10" \
  -H "Authorization: Bearer <TOKEN>"
```

### D. Buat Transaksi Kasir POS (CASH - DT4 2.5% Discount)
```bash
curl -X POST "http://localhost:8003/api/v1/orders" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "CASH",
    "customer_name": "Pak Budi",
    "customer_phone": "081234567890",
    "notes": "Kasir Toko - Cash Lunas",
    "items": [
      {
        "product_id": "019f5664-90aa-72b2-a42e-158223652ea4",
        "name": "Serenity Grand Legend 160x200",
        "quantity": 1,
        "unit_price": 2500000
      }
    ]
  }'
```
