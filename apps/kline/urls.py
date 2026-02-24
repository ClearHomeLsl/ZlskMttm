from django.urls import path
from apps.kline import views

urlpatterns = [
    path(r'', views.KlineIndexView.as_view()),
    path(r'api/kline/', views.KlineCandlestickDataView.as_view()),
    path(r'api/old_price/', views.KlineOldPriceView.as_view()),
    path(r'api/notifications/', views.KlineNotificationsView.as_view()),
]