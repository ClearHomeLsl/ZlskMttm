from django.urls import path
from apps.aliyun_pay import views


urlpatterns = [
    path(r'api/aliyun_pay/', views.AliyunPayView.as_view()),
    path(r'api/aliyun_pay/call_back/', views.AliyunPayCallBackView.as_view()),
    path('api/aliyun_pay/alipay_notify/', views.AliPayNotifyView.as_view(), name='alipay_notify'),
    path('api/aliyun_pay/payment_result/', views.AliPayMentResultView.as_view(), name='payment_result'),
]