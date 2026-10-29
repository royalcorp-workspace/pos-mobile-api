from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.store import router as store_router
from app.api.v1.products import router as products_router
from app.api.v1.orders import router as orders_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(store_router, prefix="/store", tags=["Store & Credit Limit"])
api_v1_router.include_router(products_router, prefix="/products", tags=["POS Products"])
api_v1_router.include_router(orders_router, prefix="/orders", tags=["POS Orders"])
