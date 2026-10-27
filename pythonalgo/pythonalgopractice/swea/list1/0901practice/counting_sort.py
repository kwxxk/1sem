# def counting_sort(data, k):
#     data = arr
#     temp = [0] * len(data)
#     cnt = [0] * (k+1)
#
#     for i in range(len(data)):
#         cnt[data[i]] +=1
#     for i in range(1,k+1):
#         cnt[i] += cnt[i-1]
#     for i in range(len(data)-1,-1,-1):
#         cnt[data[i]] -= 1
#         temp[cnt[data[i]]] = data[i]
#     return temp
# arr = [12,3,9,1,15,7]
# result = counting_sort(arr,15)
# print(*result)

def counting_sort(DATA, TEMP, k):

    DAT = [0] * (k + 1)

    # 1단계
    for i in range(len(DATA)):
        DAT[DATA[i]] += 1 # 값을 인덱스로, 갯수 counting

    # 2단계 : DAT값 조정 (누적)
    for i in range(1, k + 1):
        DAT[i] += DAT[i - 1]

    # 3단계 : 뒤에서부터 정렬된 배열 생성
    for i in range(len(DATA) - 1, -1, -1):
        DAT[DATA[i]] -= 1
        TEMP[DAT[DATA[i]]] = DATA[i]

DATA = [12, 3, 9, 1, 15, 7]
k = 15
TEMP = [0] * len(DATA) # 정렬된 결과를 저장할 배열

counting_sort(DATA, TEMP, k)

print(*TEMP)