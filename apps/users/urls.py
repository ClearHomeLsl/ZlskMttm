from django.urls import path
from apps.users import views



urlpatterns = [
    path(r'api/user_login/', views.UserLoginView.as_view()),
    path(r'api/user_register/', views.UserRegisterView.as_view()),
    path(r'api/verify_code/', views.V2GetVerifyCode.as_view()),
    path(r'api/receive_vip/', views.ReceiveVipView.as_view()),
    path(r'api/game_center/', views.GameCenterView.as_view()),
    path(r'api/study/upload_image/', views.ImageUploadAPIView.as_view()),
    path(r'api/study/content_list/', views.StudyContentView.as_view()),
    path(r'api/study/content_detail/<uuid:content_id>/', views.StudyContentDetailView.as_view()),
    path(r'api/study/comment_oper/', views.CommentOperGoodView.as_view()),
]