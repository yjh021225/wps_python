from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password # 新增密码处理工具
from .models import Supplier, Warehouse, StorageLocation, ProductCategory, Product, Inventory, Order, OrderItem,User
from .serializers import (
    SupplierSerializer, WarehouseSerializer, StorageLocationSerializer,
    ProductCategorySerializer, ProductSerializer, InventorySerializer, OrderSerializer,UserSerializer
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

class UserViewSet(viewsets.ModelViewSet):
    """系统用户与账号权限管理接口"""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    # ================= 下面是新增的个人中心与密码相关接口 =================

    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        """个人设置：获取或修改当前登录用户信息"""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            # 只允许修改真实姓名等非敏感信息
            user.real_name = request.data.get('real_name', user.real_name)
            user.save()
            return Response({'message': '个人信息更新成功', 'real_name': user.real_name})

    @action(detail=False, methods=['post'])
    def update_password(self, request):
        """个人设置：修改密码"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not check_password(old_password, user.password):
            return Response({'error': '原密码错误，修改失败！'}, status=400)

        user.password = make_password(new_password)
        user.save()
        return Response({'message': '密码修改成功，请使用新密码重新登录！'})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def forgot_password(self, request):
        """忘记密码：通过账号和真实姓名重置为默认密码 (无需登录即可访问)"""
        username = request.data.get('username')
        real_name = request.data.get('real_name')
        try:
            # 必须账号和真实姓名完全匹配才能重置
            user = User.objects.get(username=username, real_name=real_name)
            user.password = make_password('123456')
            user.save()
            return Response({'message': '身份验证成功！您的密码已重置为：123456。请登录后尽快修改。'})
        except User.DoesNotExist:
            return Response({'error': '账号或真实姓名不匹配，验证失败！'}, status=400)