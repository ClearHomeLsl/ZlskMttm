from django.urls import path
from apps.news import views



urlpatterns = [
    path(r'api/news/', views.NewsListView.as_view()),
]