from django.urls import path
from . import views

app_name = 'articles'
urlpatterns = [
    # path('', views.index),
    # path('articles/', articles/로 요청이 들어왔을때 호출 할 view 함수를 작성)
    # articles/ 주소로 요청이 오면 index 뷰함수를 호출 하겠다.
    # index를 index() 괄호를 작성하지 않은 이유
        # view함수의 호출은 왼쪽 인자 주소로 요청이 "왔을때" 호출이 되어야하기 때문에 함수 주소만 기록해 둠
    path('', views.index, name='index'),
    path('dinner/', views.dinner, name='dinner'),
    path('search/', views.search, name='search'),
    path('throw/', views.throw, name='throw'),
    path('catch/', views.catch, name='catch'),
    path('detail/<int:num>/', views.detail, name='detail'),
]
