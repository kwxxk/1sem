from django.urls import path,include
from my_app import views

app_name = 'my_app'
urlpatterns = [
    path('hello/', views.hello, name='hello'),
]
