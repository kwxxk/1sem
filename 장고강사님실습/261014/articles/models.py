from django.db import models

# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField()
    # 객체가 처음 생성될 때의 시간 (auto_now_add)
    created_at = models.DateTimeField(auto_now_add=True)
    # 객체가 저장될 때마다의 시간 (auto_now)
    updated_at = models.DateTimeField(auto_now=True)
    