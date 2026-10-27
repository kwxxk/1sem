from django.shortcuts import redirect, render

from .forms import ArticleForm
from .models import Article


# Create your views here.
def index(request):
    """
    [메인 페이지]
    - 메인 페이지에는 전체 게시글 목록이 출력됨
    - 따라서 DB에서 전체 게시글을 가져와야 함
    - CRUD 중 READ : 전체 게시글 조회
    """
    # 1. DB에서 전체 게시글 조회
    #    - Article.objects.all() 의 결과는 QuerySet (게시글 객체들의 묶음)
    articles = Article.objects.all()

    # 2. 템플릿에 넘겨줄 데이터를 딕셔너리로 묶기
    #    - key('articles') => 템플릿에서 사용할 변수 이름
    #    - value(articles) => 실제로 전달되는 데이터
    context = {
        'articles': articles,
    }

    # 3. 템플릿(index.html)에 데이터(context)를 채워 HTML을 만들고, 응답으로 반환
    return render(request, 'articles/index.html', context)


def detail(request, article_pk):
    """
    [단일 게시글 조회]
    - URL에서 넘겨받은 article_pk로 몇 번 게시글을 볼지 결정
    - DB에서 해당 게시글 1개를 조회한 뒤 템플릿에 전달
    - CRUD 중 READ : 단일 게시글 조회
    """
    # 1. pk가 article_pk인 게시글 1개 조회
    #    - get()의 결과는 QuerySet이 아닌 Article 객체 1개
    article = Article.objects.get(pk=article_pk)

    # 2. 템플릿에 넘겨줄 데이터를 딕셔너리로 묶기
    context = {
        'article': article,
    }

    # 3. 템플릿(detail.html)에 데이터를 채워 HTML을 만들고, 응답으로 반환
    return render(request, 'articles/detail.html', context)


# ============================================================
# STEP 1. new / create 분리 + request.POST 직접 사용
# ============================================================
# def new(request):
#     """
#     [게시글 작성 페이지] - create와 한 쌍 (GET)
#     - 제목/내용을 입력할 form이 담긴 빈 페이지를 응답
#     """
#     return render(request, 'articles/new.html')


# def create(request):
#     """
#     [게시글 저장] - new와 한 쌍 (POST)
#     - new 페이지의 form에서 제출된 데이터를 받아 DB에 저장
#     - CRUD 중 CREATE
#     """
#     # 1. form에서 제출된 제목과 내용 꺼내기
#     #    - get('title') 의 'title' => input 태그의 name 속성 값
#     title = request.POST.get('title')
#     content = request.POST.get('content')
#
#     # 2. Article 인스턴스 생성 후 DB에 저장
#     article = Article(title=title, content=content)
#     article.save()
#
#     # 3. 방금 저장한 게시글의 상세 페이지로 redirect
#     return redirect('articles:detail', article.pk)
#
#     # [STEP 1의 한계]
#     # - 빈 제목, 너무 긴 제목도 검사 없이 그대로 저장됨
#     # - 모델 필드가 늘어날수록 POST.get()을 하나씩 다 써야 함


# ============================================================
# STEP 2. ModelForm 도입 (new / create 아직 분리)
# ============================================================
# def new(request):
#     """
#     [게시글 작성 페이지] - create와 한 쌍 (GET)
#     - ModelForm으로 만든 빈 form을 템플릿에 전달
#     """
#     # 1. 빈 ArticleForm 인스턴스 생성
#     #    - 템플릿에서 {{ form }} 만 쓰면 모델 필드에 맞는 input 태그가 자동 생성됨
#     form = ArticleForm()
#
#     # 2. 템플릿에 넘겨줄 데이터를 딕셔너리로 묶기
#     context = {
#         'form': form,
#     }
#
#     # 3. 템플릿(new.html)에 form을 채워 HTML을 만들고, 응답으로 반환
#     return render(request, 'articles/new.html', context)


# def create(request):
#     """
#     [게시글 저장] - new와 한 쌍 (POST)
#     - 사용자 입력을 ModelForm으로 받아 유효성 검사 후 저장
#     - CRUD 중 CREATE
#     """
#     # 1. 사용자 입력 데이터를 ArticleForm에 통째로 전달
#     #    - request.POST의 key와 모델 필드 이름이 같으면 자동으로 짝지어짐
#     #    - ArticleForm(data=request.POST) 와 같은 의미 (첫 번째 인자가 data)
#     form = ArticleForm(request.POST)
#
#     # 2. 저장 전에 유효성 검사
#     #    - 모델에 정의한 제약조건(max_length, 필수 입력 등)을 기준으로 검사
#     if form.is_valid():
#         # 2-1. 통과 => 저장
#         #      - save()는 DB에 저장된 Article 객체를 반환
#         article = form.save()
#         # 2-2. 저장한 게시글의 상세 페이지로 redirect
#         return redirect('articles:detail', article.pk)
#
#     # 3. 통과하지 못했다면 new 페이지를 다시 응답
#     #    - 이때 form에는 사용자가 입력한 값 + 에러 메시지가 함께 담겨 있음
#     #    - 그래서 사용자는 처음부터 다시 입력하지 않아도 됨
#     context = {
#         'form': form,
#     }
#     return render(request, 'articles/new.html', context)


# ============================================================
# STEP 3. 완성본 - new + create 를 하나의 view로 통합
# ============================================================
def create(request):
    """
    [게시글 작성 페이지 + 저장] - 기존 new와 create를 하나로 통합
    - GET  : 빈 form 페이지 응답 (기존 new 역할)
    - POST : 유효성 검사 후 DB 저장 (기존 create 역할)
    - CRUD 중 CREATE
    """
    # 1. POST 요청 => 데이터를 저장하려는 요청
    if request.method == 'POST':
        # 1-1. 사용자 입력 데이터를 ArticleForm에 담기
        form = ArticleForm(request.POST)
        # 1-2. 유효성 검사 통과 시에만 저장 후 상세 페이지로 redirect
        if form.is_valid():
            article = form.save()
            return redirect('articles:detail', article.pk)
        # 1-3. 유효성 검사 실패 시 => if 블록을 빠져나가 아래 render로 이동
        #      (form에는 입력값 + 에러 메시지가 담겨 있음)

    # 2. POST가 아닌 모든 요청 => 빈 form 준비 (기존 new 역할)
    else:
        # [왜 'GET이면?'이 아니라 'POST면?'을 먼저 확인할까?]
        # - DB를 변경하는 중요한 작업(저장)은 POST일 때만 확실하게 실행
        # - 그 외의 요청은 무엇이 오든 '페이지 보여주기'만 하므로 안전
        form = ArticleForm()

    # 3. 아래 render는 두 가지 경우가 함께 사용
    #    - GET 요청             => 빈 form
    #    - 유효성 검사 실패 POST => 입력값 + 에러 메시지가 담긴 form
    context = {
        'form': form,
    }
    return render(request, 'articles/create.html', context)


def delete(request, article_pk):
    """
    [게시글 삭제]
    - 삭제할 게시글을 먼저 조회한 뒤 삭제
    - CRUD 중 DELETE
    """
    # 1. 삭제할 게시글 조회
    article = Article.objects.get(pk=article_pk)

    # 2. DB에서 삭제
    article.delete()

    # 3. 삭제된 글의 상세 페이지는 더 이상 없으므로 메인 페이지로 redirect
    return redirect('articles:index')


# ============================================================
# STEP 2. ModelForm 도입 (edit / update 아직 분리)
# ============================================================
# def edit(request, article_pk):
#     """
#     [게시글 수정 페이지] - update와 한 쌍 (GET)
#     - 기존 값이 미리 채워진 form 페이지를 응답
#     """
#     # 1. 수정할 게시글 조회
#     article = Article.objects.get(pk=article_pk)
#
#     # 2. 기존 게시글을 instance로 넘겨 ArticleForm 생성
#     #    - instance=article => form의 input에 기존 제목/내용이 채워진 상태로 생성
#     form = ArticleForm(instance=article)
#
#     # 3. 템플릿에 넘겨줄 데이터를 딕셔너리로 묶기
#     #    - article : 템플릿에서 URL을 만들 때 article.pk가 필요
#     #    - form    : 기존 값이 채워진 입력 form
#     context = {
#         'article': article,
#         'form': form,
#     }
#
#     # 4. 템플릿(edit.html)에 데이터를 채워 HTML을 만들고, 응답으로 반환
#     return render(request, 'articles/edit.html', context)


# def update(request, article_pk):
#     """
#     [게시글 수정 저장] - edit과 한 쌍 (POST)
#     - 사용자 입력을 ModelForm으로 받아 유효성 검사 후 기존 게시글 갱신
#     - CRUD 중 UPDATE
#     """
#     # 1. 수정할 게시글 조회
#     article = Article.objects.get(pk=article_pk)
#
#     # 2. 사용자 입력 데이터 + 수정 대상을 함께 전달
#     #    - request.POST     : 새로 입력된 값
#     #    - instance=article : "이 게시글을 수정할 것"이라는 대상 지정
#     form = ArticleForm(request.POST, instance=article)
#
#     # 3. 유효성 검사
#     if form.is_valid():
#         # 3-1. 수정 대상(instance)이 지정되어 있으므로 save()는 새로 만들지 않고 갱신
#         form.save()
#         # 3-2. 수정한 게시글의 상세 페이지로 redirect
#         return redirect('articles:detail', article.pk)
#
#     # 4. 통과하지 못했다면 입력값 + 에러 메시지가 담긴 form으로 edit 페이지 다시 응답
#     context = {
#         'article': article,
#         'form': form,
#     }
#     return render(request, 'articles/edit.html', context)


# ============================================================
# STEP 3. 완성본 - edit + update 를 하나의 view로 통합
# ============================================================
def update(request, article_pk):
    """
    [게시글 수정 페이지 + 수정 저장] - 기존 edit과 update를 하나로 통합
    - GET  : 기존 값이 채워진 form 페이지 응답 (기존 edit 역할)
    - POST : 유효성 검사 후 DB 갱신 (기존 update 역할)
    - CRUD 중 UPDATE
    """
    # 0. 수정할 게시글 조회
    #    - GET/POST 모두 수정 대상이 필요하므로 if문보다 먼저 조회
    article = Article.objects.get(pk=article_pk)

    # 1. POST 요청 => 수정 내용을 저장하려는 요청
    if request.method == 'POST':
        # 1-1. 새로 입력된 값 + 수정 대상(instance)을 함께 전달
        form = ArticleForm(request.POST, instance=article)
        # 1-2. 유효성 검사 통과 시 갱신 후 상세 페이지로 redirect
        if form.is_valid():
            form.save()
            return redirect('articles:detail', article.pk)
        # 1-3. 유효성 검사 실패 시 => 아래 render로 이동

    # 2. POST가 아닌 모든 요청 => 기존 값이 채워진 form 준비 (기존 edit 역할)
    else:
        form = ArticleForm(instance=article)

    # 3. 아래 render는 두 가지 경우가 함께 사용
    #    - GET 요청             => 기존 값이 채워진 form
    #    - 유효성 검사 실패 POST => 수정 중이던 입력값 + 에러 메시지가 담긴 form
    context = {
        'article': article,
        'form': form,
    }
    return render(request, 'articles/update.html', context)
