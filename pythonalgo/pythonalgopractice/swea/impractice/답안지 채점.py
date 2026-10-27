t = int(input())
for test_case in range(1,t+1):
    n,m = map(int,input().split())
    answer = list(map(int,input().split()))
    matrix = [
        list(map(int,input().split()))
        for _ in range(n)
    ]
    student_score = []
    for row in matrix:
        streak = 0
        streak_list = []
        for i in range(m):
            if answer[i] == row[i]:
                streak +=1
            else:
                if streak > 0:
                    streak_list.append(streak)
                    streak = 0
        if streak > 0:
            streak_list.append(streak)
        total_score = 0
        for j in range(len(streak_list)):
            sum_score = (streak_list[j] *(streak_list[j]+1))//2
            total_score +=sum_score

        student_score.append(total_score)
    result = max(student_score) - min(student_score)
    print(f"#{test_case} {result}")