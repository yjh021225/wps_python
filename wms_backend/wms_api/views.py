from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from .models import Supplier, Warehouse, StorageLocation, ProductCategory, Product, Inventory, Order, OrderItem
from .serializers import (
    SupplierSerializer, WarehouseSerializer, StorageLocationSerializer,
    ProductCategorySerializer, ProductSerializer, InventorySerializer, OrderSerializer
)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['role'] = self.user.role
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ================= 基础档案管理 API 视图集 =================

class SupplierViewSet(viewsets.ModelViewSet):
    """供应商 CRUD 接口"""
    queryset = Supplier.objects.all().order_by('-create_time')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated] # 必须登录带 Token 才能访问

class WarehouseViewSet(viewsets.ModelViewSet):
    """仓库 CRUD 接口"""
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

class StorageLocationViewSet(viewsets.ModelViewSet):
    """储位 CRUD 接口"""
    queryset = StorageLocation.objects.all()
    serializer_class = StorageLocationSerializer
    permission_classes = [IsAuthenticated]

class ProductCategoryViewSet(viewsets.ModelViewSet):
    """商品分类 CRUD 接口"""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    """商品基础档案 CRUD 接口"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class InventoryViewSet(viewsets.ModelViewSet):
    """全局库存查询接口"""
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    """出入库单据及核心流转接口"""
    queryset = Order.objects.all().order_by('-create_time')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    @transaction.atomic  # 开启数据库事务，确保库存和单据同时成功
    def execute_inbound(self, request):
        """执行入库操作的专属接口"""
        data = request.data
        # 自动生成单据号，如: IN20260221153022
        order_no = data.get('order_no', f"IN{timezone.now().strftime('%Y%m%d%H%M%S')}")
        items = data.get('items', [])

        # 1. 创建入库单主表
        order = Order.objects.create(
            order_no=order_no,
            order_type='in',
            status='completed',
            operator=request.user,
            remark=data.get('remark', ''),
            finish_time=timezone.now()
        )

        # 2. 遍历明细，增加库存并记录单据明细
        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                storage_location_id=item['storage_location_id'],
                quantity=item['quantity']
            )
            # 查找或创建库存记录
            inv, created = Inventory.objects.get_or_create(
                product_id=item['product_id'],
                storage_location_id=item['storage_location_id'],
                defaults={'quantity': 0}
            )
            inv.quantity += int(item['quantity'])
            inv.save()

        return Response({'message': '入库作业完成', 'order_no': order.order_no})

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def execute_outbound(self, request):
        """执行出库操作的专属接口"""
        data = request.data
        order_no = data.get('order_no', f"OUT{timezone.now().strftime('%Y%m%d%H%M%S')}")
        items = data.get('items', [])

        # 1. 提前校验所有商品库存是否充足 (防止部分出库后报错回滚)
        for item in items:
            inv = Inventory.objects.filter(
                product_id=item['product_id'],
                storage_location_id=item['storage_location_id']
            ).first()
            if not inv or inv.quantity < int(item['quantity']):
                return Response({'error': f'商品 (ID:{item["product_id"]}) 在指定储位库存不足，无法出库！'}, status=400)

        # 2. 创建出库单主表
        order = Order.objects.create(
            order_no=order_no, order_type='out', status='completed',
            operator=request.user, remark=data.get('remark', ''),
            finish_time=timezone.now()
        )

        # 3. 扣减库存记录明细
        for item in items:
            OrderItem.objects.create(
                order=order, product_id=item['product_id'],
                storage_location_id=item['storage_location_id'], quantity=item['quantity']
            )
            inv = Inventory.objects.get(product_id=item['product_id'], storage_location_id=item['storage_location_id'])
            inv.quantity -= int(item['quantity'])
            inv.save()

        return Response({'message': '出库作业完成', 'order_no': order.order_no})