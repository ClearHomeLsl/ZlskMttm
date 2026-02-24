from django.urls import path
from apps.users import views



urlpatterns = [
    path(r'api/user_login/', views.UserLoginView.as_view()),
    path(r'api/user_register/', views.UserRegisterView.as_view()),
    path(r'api/verify_code/', views.V2GetVerifyCode.as_view()),
]