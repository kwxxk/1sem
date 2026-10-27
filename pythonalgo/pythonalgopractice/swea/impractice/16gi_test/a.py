t = int(input())
for test_case in range(1,t+1):
    n = int(input())
    house_arr = [
        tuple(map(int, input().split()))
        for _ in range(n)
    ]
    house_pos = {
        (hx,hy)
        for hx,hy, limit in house_arr
    }
    full_mask = (1<<n) - 1
    candidates = []
    for station_y in range(-15,16):
        for station_x in range(-15,16):
            if (station_x,station_y) in house_pos:
                continue
            distances = []
            cover_mask = 0

            for house_idx in range(n):
                hx,hy,limit = house_arr[house_idx]

                distance = (abs(hx-station_x) + abs(hy-station_y))
                distances.append(distance)

                if distance <= limit:
                    cover_mask |= (1<<house_idx)
            candidates.append(
                (station_x,station_y,distances,cover_mask)
            )
    INF = float('inf')

    # 1개로 모든집을 커버 가능한가
    best_one = INF

    for station_x,station_y,distances,cover_mask in candidates:
        if cover_mask == full_mask:
            total_distance = sum(distances)
            best_one = min(best_one,total_distance)


    if best_one != INF:
        answer = best_one
    else:
        # 2개로 확인
        best_two = INF

        for i in range(len(candidates)-1):
            x1,y1,distances1,mask1 = candidates[i]

            for j in range(i+1,len(candidates)):
                x2,y2,distances2,mask2 = candidates[j]

                if (mask1 | mask2) != full_mask:
                    continue

                total_distance = 0

                for house_idx in range(n):
                    near_distance = min(distances1[house_idx],distances2[house_idx])
                    total_distance+= near_distance
                best_two = min(best_two,total_distance)

        if best_two == INF: answer = -1
        else: answer = best_two
    print(f"#{test_case} {answer}")