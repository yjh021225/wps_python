from rest_framework import serializers
from .models import Supplier, Warehouse, StorageLocation, ProductCategory, Product
from .models import Supplier, Warehouse, StorageLocation, ProductCategory, Product, Inventory, Order, OrderItem

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

    class Meta:
        model = Order
        fields = '__all__'