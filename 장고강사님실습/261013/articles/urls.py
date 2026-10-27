from django.contrib import admin
from django.urls import path, include
# 현재 폴더(디렉토리)로 부터 views.py
from . import views

# 프로젝트가 1개 -> 앱이 여러개
# app_name을 붙여줘야 앱이 여러개라도 다른앱과 혼동이 안됨
# URL namespace
app_name = "articles"

# name = "index" : named URL pattern (주관식 자주나옴)
# html에서 href = "https://127.0.0.1:8000/articles/index/" 
# 써서 url작성 -> 그 대신 name으로 참조하겠다.
# {% url 'articles:index' %}
urlpatterns = [
    path('', views.index, name = "index"),
    path('dinner/', views.dinner, name="dinner"),
    path('search/', views.search, name= "search"),
    path('throw/', views.throw, name="throw"),
    path('catch/', views.catch, name="catch"),
]