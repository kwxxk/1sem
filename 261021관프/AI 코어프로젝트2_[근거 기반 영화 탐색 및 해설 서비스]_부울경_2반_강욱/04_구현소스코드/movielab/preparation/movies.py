import json
import re
import unicodedata
from pathlib import Path

from ..config import UserError


def read_movies(path: Path):
    if not path.is_file():
        raise UserError("영화 데이터가 없습니다. config.json의 movies_path를 확인하세요.")
    movies = json.loads(path.read_text(encoding="utf-8"))
    ids = [str(m["movie_id"]) for m in movies]
    if len(ids) != len(set(ids)):
        raise UserError("영화 데이터에 중복 ID가 있습니다.")
    return movies


def movie_text(movie):
    fields = [
        ("제목", movie["title"]), ("원제", movie.get("original_title", "")),
        ("개봉연도", movie.get("year", "")), ("개봉일", movie.get("release_date", "")),
        ("장르", ", ".join(movie.get("genres", []))),
        ("감독", ", ".join(movie.get("director", []))),
        ("출연", ", ".join(movie.get("cast", []))),
        ("상영시간(분)", movie.get("runtime", "")),
        ("언어", movie.get("original_language", "")),
        ("제작국가", ", ".join(movie.get("production_countries", []))),
        ("평점", movie.get("vote_average", "")),
        ("평가수", movie.get("vote_count", "")),
        ("줄거리", movie.get("overview", "")),
    ]
    return "\n".join(f"{key}: {value}" for key, value in fields)


def normalize(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip().casefold()


# 배포 영화 제목과 같은 작품의 위키 제목이 다른 경우의 명시적 대응.
# 다른 연도 리메이크는 아래 별칭보다 연도 검증이 우선한다.
WIKI_ALIASES = {
    "11": "스타워즈", "105": "백 투 더 퓨처", "165": "백 투 더 퓨처 2",
    "196": "백 투 더 퓨처 3", "140607": "스타워즈: 깨어난 포스",
    "1891": "제국의 역습", "1892": "제다이의 귀환", "181808": "스타워즈: 라스트 제다이",
    "181812": "스타워즈: 라이즈 오브 스카이워커", "280": "터미네이터 2",
    "85": "레이더스", "601": "E.T.", "600": "풀 메탈 재킷", "1417": "판의 미로",
    "495764": "버즈 오브 프레이", "772": "나 홀로 집에 2", "389": "12인의 성난 사람들",
    "38356": "트랜스포머: 달의 어둠", "447365": "가디언즈 오브 갤럭시: Volume 3",
    "37735": "이지 A", "296": "터미네이터 3", "534": "터미네이터: 미래전쟁의 시작",
    "203801": "맨 프롬 UNCLE", "9532": "파이널 데스티네이션", "644": "A.I.",
    "12230": "101마리의 달마시안 개", "12477": "반딧불이의 묘", "762": "몬티 파이튼과 성배",
    "615173": "마녀(魔女) Part2. The Other One",
}


def is_item_document(title, movie):
    title = unicodedata.normalize("NFKC", title)
    # 동명 인물/TV 드라마 및 개봉연도가 다른 리메이크를 항목 문서로 오인하지 않는다.
    if any(word in title for word in ("드라마)", "소설)", "음반)", "노래)")):
        return False
    years = re.findall(r"\((\d{4})년?\s*영화\)", title)
    if years and str(movie.get("year")) not in years:
        return False
    base = re.sub(r"\s*\([^)]*\)", "", title)
    # 데이터 제공처와 위키의 띄어쓰기·문장부호 차이를 허용한다.
    compact = lambda value: re.sub(r"[\W_]+", "", normalize(value))
    names = {compact(movie["title"]), compact(movie.get("original_title", ""))}
    names.add(compact(re.sub(r"\s*\([^)]*\)", "", unicodedata.normalize("NFKC", movie["title"]))))
    alias = WIKI_ALIASES.get(str(movie["movie_id"]))
    if alias:
        names.add(compact(re.sub(r"\s*\([^)]*\)", "", alias)))
    if re.search(r"\d$", movie["title"]):
        names.add(compact(movie["title"] + "부"))
    return compact(base) in names
