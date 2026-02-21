from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 调用父类方法获取原生数据（包含 access 和 refresh token）
        data = super().validate(attrs)

        # 在返回给前端的数据中，额外加上用户的角色和用户名
        data['username'] = self.user.username
        data['role'] = self.user.role

        return data


class LoginView(TokenObtainPairView):
    # 使用我们自定义的序列化器
    serializer_class = CustomTokenObtainPairSerializer