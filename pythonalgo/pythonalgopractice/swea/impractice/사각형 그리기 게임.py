t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    matrix = [
        list(map(int,input().split()))
        for _ in range(n)
    ]
    cnt = 0
    max_area =0
    for start_y in range(n):
        for start_x in range(n):

            for end_y in range(start_y , n):
                for end_x in range(start_x , n):
                    if matrix[start_y][start_x] != matrix[end_y][end_x]:
                        continue
                    height = end_y - start_y +1
                    width = end_x - start_x +1
                    area = height * width

                    if area > max_area:
                        max_area = area
                        cnt = 1

                    elif max_area == area:
                        cnt += 1
    print(f"#{test_case} {cnt}")
    # 박스 크기 제한 -> 6이상 일때 넘겨버리기
    #왼쪽 위와 오른쪽 아래가 같은 값인지 확인
