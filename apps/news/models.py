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

# class UserProfile(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     username = models.CharField(verbose_name='用户名', max_length=16, unique=True, null=False, blank=False)
#     mobile = models.CharField(verbose_name='手机号', max_length=16, null=False, blank=False)
#     real_name = models.CharField(verbose_name='真实姓名', max_length=16)
#     password = models.CharField(verbose_name='密码', max_length=255, null=False, blank=False)
#     is_vip = models.BooleanField(verbose_name='是否为会员', default=False)
#     vip_end_time = models.DateTimeField(verbose_name="会员到期时间", null=True, blank=True)
#     create_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
#     register_ip = models.CharField(verbose_name='注册IP', max_length=16)
#     last_login_ip = models.CharField(verbose_name='上次登陆IP', max_length=16)
#     last_login_time = models.DateTimeField(verbose_name='上次登陆时间', null=True, blank=True)
#     is_delete = models.BooleanField(verbose_name="是否注销", default=False)
#     deleted_at = models.DateTimeField(verbose_name="注销时间", null=True, blank=True)


class FinanceNews(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(verbose_name='标题', max_length=50, null=False, blank=False)
    content = models.TextField(verbose_name='内容', null=False, blank=False)
    author = models.CharField(verbose_name='作者', max_length=16, null=False, blank=False)
    news_link = models.URLField(verbose_name='文章链接', null=False, blank=False)
    release_time = models.DateTimeField(verbose_name='发布时间', null=False, blank=False)
    add_time = models.DateTimeField(verbose_name='添加时间', null=False, blank=False)

    class Meta:
        verbose_name = "金融新闻"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title