t = int(input())

for test_case in range(1, t + 1):
    n = int(input())

    houses = [
        tuple(map(int, input().split()))
        for _ in range(n)
    ]

    house_positions = {
        (hx, hy)
        for hx, hy, limit in houses
    }

    candidates = []

    # 충전소를 설치할 수 있는 모든 좌표 확인
    for station_y in range(-15, 16):
        for station_x in range(-15, 16):

            if (station_x, station_y) in house_positions:
                continue  #  집이 있는 위치에는 충전소 설치 불가

            distances = []
            covered = []  # 집별 담당 가능 여부 저장

            for hx, hy, limit in houses:
                distance = (abs(hx - station_x) + abs(hy - station_y))
                distances.append(distance)
                covered.append(distance <= limit)  # 담당 가능하면 True

            candidates.append(
                (station_x, station_y, distances, covered)
            )

    INF = float('inf')

    # 충전소 1개로 모든 집을 담당할 수 있는지 확인
    best_one = INF

    for station_x, station_y, distances, covered in candidates:
        if all(covered):  # 모든 집의 담당 가능 여부가 True인지 확인
            total_distance = sum(distances)
            best_one = min(best_one, total_distance)

    if best_one != INF:
        answer = best_one  # 1개로 가능하면 반드시 1개만 설치

    else: # 충전소 2개 확인
        best_two = INF
        candidate_count = len(candidates)

        for i in range(candidate_count - 1):
            x1, y1, distances1, covered1 = candidates[i]
            for j in range(i + 1, candidate_count):
                x2, y2, distances2, covered2 = candidates[j]
                can_cover_all = True
                total_distance = 0

                for house_idx in range(n):
                    if not (covered1[house_idx]or covered2[house_idx]):
                        can_cover_all = False
                        break  # 두 충전소 모두 담당할 수 없는 집이 있으면 중단

                    near_distance = min(distances1[house_idx],distances2[house_idx])
                    total_distance += near_distance

                if can_cover_all: best_two = min(best_two, total_distance)

        if best_two == INF: answer = -1  # 충전소 2개로도 모든 집을 담당하지 못함
        else: answer = best_two

    print(f"#{test_case} {answer}")