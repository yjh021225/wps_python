from rest_framework import serializers

from .models import User, Supplier, Warehouse, StorageLocation, ProductCategory, Product, Inventory, Order, OrderItem
from django.contrib.auth.hashers import make_password
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class StorageLocationSerializer(serializers.ModelSerializer):
    # read_only=True 表示这个字段只在返回给前端时展示，前端提交时不要求传这个字段
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = StorageLocation
        fields = '__all__'


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    location_code = serializers.CharField(source='storage_location.code', read_only=True)
    warehouse_name = serializers.CharField(source='storage_location.warehouse.name', read_only=True)
    min_stock = serializers.IntegerField(source='product.min_stock', read_only=True)
    max_stock = serializers.IntegerField(source='product.max_stock', read_only=True)
    class Meta:
        model = Inventory
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    location_code = serializers.CharField(source='storage_location.code', read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ('order',)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    operator_name = serializers.CharField(source='operator.real_name', read_only=True)
    operator_username = serializers.CharField(source='operator.username', read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
class UserSerializer(serializers.ModelSerializer):
    # password 设为 write_only，保证接口返回数据时不会泄露密码（哪怕是密文）
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role_name = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'real_name', 'role', 'role_name', 'is_active', 'date_joined')
        read_only_fields = ('date_joined',)

    def create(self, validated_data):
        # 新增用户时加密密码
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        # 默认赋予 is_staff 权限（仅为了兼容 Django admin）
        validated_data['is_staff'] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 修改用户时，如果填了新密码则加密更新，没填则保持原密码
        if validated_data.get('password'):
            validated_data['password'] = make_password(validated_data['password'])
        else:
            validated_data.pop('password', None)
        return super().update(instance, validated_data)