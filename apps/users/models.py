import uuid


from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password

#
# class User(AbstractUser):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     remark = models.TextField(blank=True, null=True)
#
#     class Meta:
#         verbose_name = "管理员用户"
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.id

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(verbose_name='用户名', max_length=16, unique=True, null=False, blank=False)
    mobile = models.CharField(verbose_name='手机号', max_length=16, null=False, blank=False)
    real_name = models.CharField(verbose_name='真实姓名', max_length=16)
    password = models.CharField(verbose_name='密码', max_length=255, null=False, blank=False)
    is_vip = models.BooleanField(verbose_name='是否为会员', default=False)
    vip_end_time = models.DateTimeField(verbose_name="会员到期时间", null=True, blank=True)
    create_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    register_ip = models.CharField(verbose_name='注册IP', max_length=16)
    last_login_ip = models.CharField(verbose_name='上次登陆IP', max_length=16)
    last_login_time = models.DateTimeField(verbose_name='上次登陆时间', null=True, blank=True)
    is_delete = models.BooleanField(verbose_name="是否注销", default=False)
    deleted_at = models.DateTimeField(verbose_name="注销时间", null=True, blank=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username + "_" + self.mobile

    def set_password(self, raw_password):
        """
        加密并设置密码
        """
        if raw_password:
            # 使用Django的密码哈希函数加密
            self.password = make_password(raw_password)
        else:
            self.password = None

    def check_password(self, raw_password):
        """
        验证密码
        """
        if not self.password or not raw_password:
            return False

        # 使用Django的密码检查函数
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        """
        重写save方法，确保密码被加密
        """
        # 如果密码是明文（不是以加密格式开头）
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)



