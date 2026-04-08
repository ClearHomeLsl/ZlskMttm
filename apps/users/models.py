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




class Person(models.Model):
    # 定义选项元组
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M',
        verbose_name='性别'
    )

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(verbose_name='用户名', max_length=16, unique=True, null=False, blank=False)
    email = models.EmailField(verbose_name='邮箱', blank=True, null=True)
    mobile = models.CharField(verbose_name='手机号', max_length=16, null=False, blank=False)
    real_name = models.CharField(verbose_name='真实姓名', max_length=16, blank=True, null=True)
    password = models.CharField(verbose_name='密码', max_length=255, null=False, blank=False)
    is_vip = models.BooleanField(verbose_name='是否为会员', default=False)
    vip_end_time = models.DateTimeField(verbose_name="会员到期时间", null=True, blank=True)
    create_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    register_ip = models.CharField(verbose_name='注册IP', max_length=16)
    last_login_ip = models.CharField(verbose_name='上次登陆IP', max_length=16)
    last_login_time = models.DateTimeField(verbose_name='上次登陆时间', null=True, blank=True)
    is_receive_vip = models.BooleanField(verbose_name='是否已领取新手VIP', default=False)
    is_vip_experience = models.BooleanField(verbose_name='是否为体验VIP用户', default=False)
    point = models.IntegerField(verbose_name='积分', default=0)
    POINT_LEVEL = [
        (1, "交易萌新"),
        (2, "市场学徒"),
        (3, "市场新锐"),
        (4, "策略新手"),
        (5, "策略学徒"),
        (6, "图表猎人"),
        (7, "趋势捕手"),
        (8, "资金魔术师"),
        (9, "市场先知"),
        (10, "交易指挥官"),
    ]
    point_level = models.IntegerField(verbose_name='积分等级', default=1, choices=POINT_LEVEL)
    USER_STUTAS = [
        (1, "正常"),
        (2, "封禁"),
        (3, "冻结"),
    ]
    user_stutas = models.IntegerField(verbose_name='用户状态', default=1, choices=USER_STUTAS)
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


class GameSymbol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='产品名', null=False, blank=False)
    nick_name = models.CharField(max_length=100, verbose_name='产品别名', null=True, blank=True)
    is_game = models.BooleanField(verbose_name='是否可竞猜', default=False)

    class Meta:
        verbose_name = "竞猜产品"
        verbose_name_plural = verbose_name


class GameCenter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.ForeignKey(GameSymbol, verbose_name='竞猜产品', on_delete=models.CASCADE)
    game_date = models.DateTimeField(verbose_name='交易日', null=False, blank=False)
    start_time = models.DateTimeField(verbose_name='开始日', null=False, blank=False)
    end_time = models.DateTimeField(verbose_name='结算日', null=False, blank=False)
    open_price = models.DecimalField(verbose_name='当日开盘价', null=True, blank=True, decimal_places=2, max_digits=10)
    close_price = models.DecimalField(verbose_name='当日收盘价', null=True, blank=True, decimal_places=2, max_digits=10)
    RESULT_CHOICES = [
        (1, "up"),
        (2, "down")
    ]
    result = models.IntegerField(verbose_name='当日结果', choices=RESULT_CHOICES, null=True, blank=True)
    create_at = models.DateTimeField(verbose_name='创建时间', default=timezone.now, null=False, blank=False)

    class Meta:
        verbose_name = "竞猜交易日"
        verbose_name_plural = verbose_name


class UserGameSignUp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    game_center = models.ForeignKey(GameCenter, verbose_name='竞猜交易日', on_delete=models.CASCADE)
    point = models.DecimalField(verbose_name='竞猜积分', null=True, blank=True, decimal_places=2, max_digits=10)
    GUESS_CHOICES = [
        (1, "up"),
        (2, "down")
    ]
    guess = models.IntegerField(verbose_name='竞猜方向', choices=GUESS_CHOICES)
    RESULT_CHOICES = [
        (1, "win"),
        (2, "lose"),
    ]
    result = models.IntegerField(verbose_name='竞猜结果', choices=RESULT_CHOICES, null=True, blank=True)
    create_at = models.DateTimeField(verbose_name='竞猜时间', default=timezone.now, null=False, blank=False)
    is_end = models.BooleanField(verbose_name='是否结算', default=False)
    end_time = models.DateTimeField(verbose_name='结算时间', null=True, blank=True)

    class Meta:
        verbose_name = "竞猜报名记录"
        verbose_name_plural = verbose_name


class PointRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, verbose_name='用户', on_delete=models.CASCADE)
    old_point = models.DecimalField(verbose_name='变化前积分', null=True, blank=True, decimal_places=2, max_digits=10)
    add_point = models.DecimalField(verbose_name='变化积分', null=True, blank=True, decimal_places=2, max_digits=10)
    new_point = models.DecimalField(verbose_name='变化后积分', null=True, blank=True, decimal_places=2, max_digits=10)
    CHANGE_OPER = [
        (1, "报名竞猜"),
        (2, "竞猜获胜"),
        (3, "会员赠送"),
        (4, "注册赠送"),
        (5, "系统赠送"),
    ]
    change_oper = models.IntegerField(verbose_name='变动类型', choices=CHANGE_OPER, null=True, blank=True)
    create_at = models.DateTimeField(verbose_name='创建时间', default=timezone.now, null=False, blank=False)

    class Meta:
        verbose_name = "积分变动记录"
        verbose_name_plural = verbose_name


class StudyContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, verbose_name='标题', null=False, blank=False)
    content = models.TextField(verbose_name='内容', null=False, blank=False)
    user = models.ForeignKey(UserProfile, verbose_name='作者', on_delete=models.CASCADE)
    create_at = models.DateTimeField(verbose_name='创建时间', default=timezone.now, null=False, blank=False)
    STATUS_CHOICES = [
        (1, "审核中"),
        (2, "审核未通过"),
        (3, "审核通过")
    ]
    status = models.IntegerField(verbose_name='文章状态', choices=STATUS_CHOICES, null=True, blank=True, default=1)
    cover_image_path = models.CharField(max_length=100, verbose_name='封面图片壁纸', null=True, blank=True)

    class Meta:
        verbose_name = "学习中心文章"
        verbose_name_plural = verbose_name


class StudyGood(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, verbose_name='点赞用户', on_delete=models.CASCADE)
    study_content = models.ForeignKey(StudyContent, verbose_name='被点赞文章', on_delete=models.CASCADE)
    create_at = models.DateTimeField(verbose_name='点赞时间', default=timezone.now, null=False, blank=False)
    is_del = models.BooleanField(verbose_name='是否取消', default=False)

    class Meta:
        verbose_name = "用户点赞记录"
        verbose_name_plural = verbose_name


class StudyComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, verbose_name='评论用户', on_delete=models.CASCADE)
    study_content = models.ForeignKey(StudyContent, verbose_name='被评论文章', on_delete=models.CASCADE)
    create_at = models.DateTimeField(verbose_name='评论时间', default=timezone.now, null=False, blank=False)
    comment = models.CharField(verbose_name='评论内容', null=False, blank=False, max_length=4000)
    is_del = models.BooleanField(verbose_name='是否删除', default=False)

    class Meta:
        verbose_name = "用户评论记录"
        verbose_name_plural = verbose_name


class StudyCommentGood(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, verbose_name='点赞评论用户', on_delete=models.CASCADE)
    comment = models.ForeignKey(StudyComment, verbose_name='被点赞评论', on_delete=models.CASCADE)
    create_at = models.DateTimeField(verbose_name='点赞评论时间', default=timezone.now, null=False, blank=False)
    is_del = models.BooleanField(verbose_name='是否取消', default=False)

    class Meta:
        verbose_name = "用户评论点赞记录"
        verbose_name_plural = verbose_name


class EmailSub(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(verbose_name='邮箱', null=False, blank=False)
    is_sub= models.BooleanField(verbose_name='是否订阅', default=False)
    # TODO 暂无取消订阅方法
    del_time = models.DateTimeField(verbose_name='取消订阅时间', null=True, blank=True)
    create_at = models.DateTimeField(verbose_name='创建时间', default=timezone.now, null=False, blank=False)

    class Meta:
        verbose_name = "订阅邮箱"
        verbose_name_plural = verbose_name


class AgencyApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name='姓名', null=False, blank=False)
    mobile = models.CharField(verbose_name='联系方式', null=False, blank=False)
    email = models.CharField(verbose_name='电子邮箱', null=False, blank=False)
    content = models.TextField(verbose_name='合作意向描述', null=False, blank=False)
    create_at = models.DateTimeField(verbose_name='申请时间', default=timezone.now, null=False, blank=False)
    is_connect = models.BooleanField(verbose_name='是否已联系', default=False)
    connect_time = models.DateTimeField(verbose_name='联系时间', null=True, blank=True)
    connect_result = models.TextField(verbose_name='联系结果(备注)', null=True, blank=True)

    class Meta:
        verbose_name = "合作申请记录"
        verbose_name_plural = verbose_name



# class StudyOperDoc(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(UserProfile, verbose_name='<UNK>', on_delete=models.CASCADE)
#     content = model



