from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, WarehouseViewSet, StorageLocationViewSet,
    ProductCategoryViewSet, ProductViewSet,
    InventoryViewSet, OrderViewSet,UserViewSet,

)
# 使用 DRF 的默认路由器，它会自动为 ModelViewSet 生成标准的 RESTful 路由
router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'locations', StorageLocationViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'inventories', InventoryViewSet) # <-- 注册库存接口
router.register(r'orders', OrderViewSet)          # <-- 注册单据接口
router.register(r'users', UserViewSet)
urlpatterns = [
    # 将 router 自动生成的 URL 包含进来
    path('', include(router.urls)),
]
