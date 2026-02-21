from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    自定义用户模型，继承 Django 自带的用户体系，外加角色区分
    """
    ROLE_CHOICES = (
        ('admin', '系统管理员'),
        ('supervisor', '仓库主管'),
        ('operator', '普通操作员'),
    )

    # 核心字段：角色分流就靠它了
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator', verbose_name='系统角色')

    # 可以额外加上工号、手机号等，这里先加个真实姓名
    real_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='真实姓名')

    class Meta:
        db_table = 'wms_user'  # 在 MySQL 里生成的表名
        verbose_name = '系统用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"