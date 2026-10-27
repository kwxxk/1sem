from django.urls import path

# 현재디렉토리로 부터 views.py
from . import views

app_name = "articles"

urlpatterns = [
    # 전체 게시글 조회
    # https://127.0.0.1:8000/aritlces/ 로 url 요청이 오면
    # views.py의 index함수를 실행하겠다
    path('index/', views.index, name = 'index'),
    # <int:pk> -> variable routing
    path('<int:pk>/', views.detail, name = 'detail'),
    # CREATE : 랜더링 + 리다이렉트
    # 게시글 생성 페이지를 띄운다 -> GET 요청 (랜더링)
    # 게시글 작성하고 게시글 생성한다 -> POST 요청 (리다이렉트)
    path('new/', views.new, name = "new"),
    path('create/', views.create, name = "create"),
    # UPDATE(전에있던 데이터 불러와야함) : 랜더링 + 리다이렉트

    path('<int:pk>/update/', views.update, name = "update"),
    # DELETE -> 게시글 조회(variable routing) 후 삭제
    path('<int:pk>/delete/', views.delete, name = "delete"),

]