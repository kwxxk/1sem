from django.db import models

# Create your models here.
class Article(models.Model):
    # 게시글 제목은 악용의 위험이 있기때문에 글자 제한을 둔다
    title = models.CharField(max_length=20)
    content = models.TextField()
    # auto_now_add : 객체가 처음 생성되는 시간
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now : 객체가 저장 될때마다 시간
    updated_at = models.DateTimeField(auto_now=True)