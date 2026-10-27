from django.shortcuts import render

# Create your views here.

# 메인 페이지를 응답하는 함수

# view함수의 약속
    # 모든 view 함수는 반드시 첫번째 인자로 요청 객체(urls.py로 부터 받은)가 들어온다.
    # 매개변수 이름이 request일 필요는 없음. 하지만 다른 이름을 사용하지 않는다.
def index(request):
    # 메인 페이지 (템플릿)을 응답 데이터로 생성
    # 템플릿을 취합해서 최종적으로 만들어주는 함수
    context = {
        'name': 'Jane',
    }
    return render(request, 'articles/index.html', context)


import random

def dinner(request):
    foods = ['국밥', '국수', '카레', '탕수육', '빵']
    picked = random.choice(foods)
    context = {
        'foods': foods,
        'picked': picked,
    }
    return render(request, 'articles/dinner.html', context)

def search(request):
    return render(request, 'articles/search.html')


# client에게 데이터를 입력할 form이 담긴 페이지를 응답하는 함수
def throw(request):
    return render(request, 'articles/throw.html')


# 사용자 입력 데이터를 받아 그 데이터를 추출하여 어떤 데이터를 보냈는지 다시 알려주는 함수
def catch(request):
    # 1. 사용자가 입력한 데이터를 찾아야 함
        # but 사용자가 입력한 데이터는 어디에 들어있을까?
        # client가 보낸 모든 정보는 첫번째 인자 덩어리에 들어있음
    data = request.GET.get('query')
    # 찾은 데이터를 변수에 담아서 템플릿과 함께 응답
    context = {
        'data': data,
    }
    return render(request, 'articles/catch.html', context)

# variable 라우팅에 선언한 변수명과 동일한 매개변수 이름을 사용해야한다.
def detail(request,num):
    context = {
        'num': num,
    }
    return render(request, 'articles/detail.html', context)