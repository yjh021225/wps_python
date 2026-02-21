from django.contrib import admin
from django.urls import path
from wms_api.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls), # Django自带的后台管理
    path('api/login/', LoginView.as_view(), name='login'), # 我们的真实登录接口
]