from django.contrib import admin

# Register your models here.
# 현재 티렉토리의 models.py의 Ariticle 모델을 가져오겠다.
from .models import Article

# admin 사이트에 등록하겠다
admin.site.register(Article)